from __future__ import unicode_literals
from collections import OrderedDict
from coreapi.codecs.base import BaseCodec
from coreapi.compat import string_types, force_bytes, urlparse
from coreapi.compat import COMPACT_SEPARATORS, VERBOSE_SEPARATORS
from coreapi.document import Document, Link, Array, Object, Error, Field
from coreapi.exceptions import ParseError
import json


def _graceful_relative_url(base_url, url):
    """
    Return a graceful link for a URL relative to a base URL.

    * If they are the same, return an empty string.
    * If the have the same scheme and hostname, return the path & query params.
    * Otherwise return the full URL.
    """
    if url == base_url:
        return ''
    base_prefix = '%s://%s' % urlparse.urlparse(base_url or '')[0:2]
    url_prefix = '%s://%s' % urlparse.urlparse(url or '')[0:2]
    if base_prefix == url_prefix and url_prefix != '://':
        return url[len(url_prefix):]
    return url


def _escape_key(string):
    """
    The '_type' and '_meta' keys are reserved.
    Prefix with an additional '_' if they occur.
    """
    if string.startswith('_') and string.lstrip('_') in ('type', 'meta'):
        return '_' + string
    return string


def _unescape_key(string):
    """
    Unescape '__type' and '__meta' keys if they occur.
    """
    if string.startswith('__') and string.lstrip('_') in ('type', 'meta'):
        return string[1:]
    return string


def _document_to_primative(node, base_url=None):
    """
    Take a Core API document and return Python primatives
    ready to be rendered into the JSON style encoding.
    """
    if isinstance(node, Document):
        ret = OrderedDict()
        ret['_type'] = 'document'

        # Only fill in items in '_meta' if required.
        meta = OrderedDict()
        url = _graceful_relative_url(base_url, node.url)
        if url:
            meta['url'] = url
        if node.title:
            meta['title'] = node.title
        if meta:
            ret['_meta'] = meta

        ret.update([
            (_escape_key(key), _document_to_primative(value, base_url=node.url))
            for key, value in node.items()
        ])
        return ret

    elif isinstance(node, Link):
        ret = OrderedDict()
        ret['_type'] = 'link'
        url = _graceful_relative_url(base_url, node.url)
        if url:
            ret['url'] = url
        if node.action:
            ret['action'] = node.action
        if node.inplace is not None:
            ret['inplace'] = node.inplace
        if node.fields:
            # Use short format for optional fields, long format for required.
            ret['fields'] = [
                _document_to_primative(field) for field in node.fields
            ]
        return ret

    elif isinstance(node, Field):
        ret = OrderedDict({'name': node.name})
        if node.required:
            ret['required'] = True
        if node.location:
            ret['location'] = node.location
        return ret

    elif isinstance(node, Object):
        return OrderedDict([
            (_escape_key(key), _document_to_primative(value, base_url=base_url))
            for key, value in node.items()
        ])

    elif isinstance(node, Array):
        return [_document_to_primative(value) for value in node]

    elif isinstance(node, Error):
        ret = OrderedDict()
        ret['_type'] = 'error'
        ret['messages'] = node.messages
        return ret

    return node


def _primative_to_document(data, base_url=None):
    """
    Take Python primatives as returned from parsing JSON content,
    and return a Core API document.
    """
    if isinstance(data, dict) and data.get('_type') == 'document':
        # Document
        meta = data.get('_meta', {})
        if not isinstance(meta, dict):
            meta = {}

        url = meta.get('url', '')
        if not isinstance(url, string_types):
            url = ''
        url = urlparse.urljoin(base_url, url)

        title = meta.get('title', '')
        if not isinstance(title, string_types):
            title = ''

        return Document(url=url, title=title, content={
            _unescape_key(key): _primative_to_document(value, url)
            for key, value in data.items()
            if key not in ('_type', '_meta')
        })

    elif isinstance(data, dict) and data.get('_type') == 'link':
        # Link
        url = data.get('url', '')
        if not isinstance(url, string_types):
            url = ''
        url = urlparse.urljoin(base_url, url)

        action = data.get('action')
        if not isinstance(action, string_types):
            action = ''

        inplace = data.get('inplace')
        if not isinstance(inplace, bool):
            inplace = None

        fields = data.get('fields', [])
        if not isinstance(fields, list):
            fields = []
        else:
            # Ignore any field items that don't match the required structure.
            fields = [
                item for item in fields
                if isinstance(item, string_types) or (
                    isinstance(item, dict) and
                    isinstance(item.get('name'), string_types)
                )
            ]
            # Transform the dicts into Field instances.
            fields = [
                Field(
                    item['name'],
                    required=bool(item.get('required', False)),
                    location=str(item.get('type', ''))
                )
                for item in fields if isinstance(item, dict)
            ]

        return Link(url=url, action=action, inplace=inplace, fields=fields)

    elif isinstance(data, dict) and data.get('_type') == 'error':
        # Error
        messages = data.get('messages', [])
        if not isinstance(messages, list):
            messages = []

        # Ignore any messages which are have incorrect type.
        messages = [
            message for message in messages
            if isinstance(message, string_types)
        ]

        return Error(messages)

    elif isinstance(data, dict):
        # Map
        return Object({
            _unescape_key(key): _primative_to_document(value, base_url)
            for key, value in data.items()
            if key not in ('_type', '_meta')
        })

    elif isinstance(data, list):
        # Array
        return Array([
            _primative_to_document(item, base_url) for item in data
        ])

    # String, Integer, Number, Boolean, null.
    return data


class CoreJSONCodec(BaseCodec):
    media_type = 'application/vnd.coreapi+json'

    def load(self, bytes, base_url=None):
        """
        Takes a bytestring and returns a document.
        """
        try:
            data = json.loads(bytes.decode('utf-8'))
        except ValueError as exc:
            raise ParseError('Malformed JSON. %s' % exc)

        doc = _primative_to_document(data, base_url)
        if not isinstance(doc, (Document, Error)):
            raise ParseError('Top level node must be a document or error message.')

        return doc

    def dump(self, document, indent=False, **kwargs):
        """
        Takes a document and returns a bytestring.
        """
        if indent:
            options = {
                'ensure_ascii': False,
                'indent': 4,
                'separators': VERBOSE_SEPARATORS
            }
        else:
            options = {
                'ensure_ascii': False,
                'indent': None,
                'separators': COMPACT_SEPARATORS
            }

        data = _document_to_primative(document)
        return force_bytes(json.dumps(data, **options))
