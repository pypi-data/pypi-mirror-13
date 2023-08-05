import click
import coreapi
import json
import os
import sys


config_path = None

document_path = None
history_path = None
credentials_path = None
headers_path = None
bookmarks_path = None


def setup_paths():
    global config_path, document_path, history_path
    global credentials_path, headers_path, bookmarks_path

    default_dir = os.path.join(os.path.expanduser('~'), '.coreapi')
    config_path = os.environ.get('COREAPI_CONFIG_DIR', default_dir)

    document_path = os.path.join(config_path, 'document.json')
    history_path = os.path.join(config_path, 'history.json')
    credentials_path = os.path.join(config_path, 'credentials.json')
    headers_path = os.path.join(config_path, 'headers.json')
    bookmarks_path = os.path.join(config_path, 'bookmarks.json')


def coerce_key_types(doc, keys):
    """
    Given a document and a list of keys such as ['rows', '123', 'edit'],
    return a list of keys, such as ['rows', 123, 'edit'].
    """
    ret = []
    active = doc
    for idx, key in enumerate(keys):
        # Coerce array lookups to integers.
        if isinstance(active, coreapi.Array):
            try:
                key = int(key)
            except:
                pass

        # Descend through the document, so we can correctly identify
        # any nested array lookups.
        ret.append(key)
        try:
            active = active[key]
        except (KeyError, IndexError, ValueError, TypeError):
            ret += keys[idx + 1:]
            break

    return ret


def get_document_string(doc):
    if not doc.title:
        return '<Document %s>' % json.dumps(doc.url)
    return '<%s %s>' % (doc.title, json.dumps(doc.url))


def get_session():
    credentials = get_credentials()
    headers = get_headers()
    return coreapi.get_session(credentials, headers)


def get_document():
    if not os.path.exists(document_path):
        return None
    store = open(document_path, 'rb')
    content = store.read()
    store.close()
    return coreapi.load(content)


def set_document(doc):
    content_type, content = coreapi.dump(doc)
    store = open(document_path, 'wb')
    store.write(content)
    store.close()


def display(doc):
    codec = coreapi.codecs.PlainTextCodec()
    return codec.dump(doc, colorize=True)


# Core commands

@click.group(invoke_without_command=True, help='Command line client for interacting with CoreAPI services.\n\nVisit http://www.coreapi.org for more information.')
@click.option('--version', is_flag=True, help='Display the package version number.')
@click.pass_context
def client(ctx, version):
    setup_paths()

    if os.path.isfile(config_path):
        os.remove(config_path)  # pragma: nocover
    if not os.path.isdir(config_path):
        os.mkdir(config_path)

    if ctx.invoked_subcommand is not None:
        return

    if version:
        click.echo('coreapi version %s' % coreapi.__version__)
    else:
        click.echo(ctx.get_help())


@click.command(help='Fetch a document from the given URL.')
@click.argument('url')
def get(url):
    session = get_session()
    history = get_history()
    doc = session.get(url)
    history = history.add(doc)
    click.echo(display(doc))
    set_document(doc)
    set_history(history)


@click.command(help='Clear the active document and other state.\n\nThis includes the current document, history, credentials, headers and bookmarks.')
def clear():
    for path in [
        document_path,
        history_path,
        credentials_path,
        headers_path,
        bookmarks_path
    ]:
        if os.path.exists(path):
            os.remove(path)

    click.echo('Cleared.')


@click.command(help='Display the current document.\n\nOptionally display just the element at the given PATH.')
@click.argument('path', nargs=-1)
def show(path):
    doc = get_document()
    if doc is None:
        click.echo('No current document. Use `coreapi get` to fetch a document first.')
        sys.exit(1)

    if path:
        keys = coerce_key_types(doc, path)
        for key in keys:
            doc = doc[key]
        if isinstance(doc, (bool, type(None))):
            doc = {True: 'true', False: 'false', None: 'null'}[doc]
    click.echo(display(doc))


def validate_params(ctx, param, value):
    if any(['=' not in item for item in value]):
        raise click.BadParameter('Parameters need to be in format <field name>=<value>')
    return dict([tuple(item.split('=', 1)) for item in value])


def validate_inplace(ctx, param, value):
    if value is None:
        return
    if value.lower() not in ('true', 'false'):
        raise click.BadParameter('"--inplace" needs to be one of "true" or "false"')
    return value.lower() == 'true'


@click.command(help='Interact with the active document.\n\nRequires a PATH to a link in the document.')
@click.argument('path', nargs=-1)
@click.option('--param', '-p', multiple=True, callback=validate_params, help='Parameter in the form <field name>=<value>.')
@click.option('--action', '-a', help='Set the link action explicitly.', default=None)
@click.option('--inplace', '-i', callback=validate_inplace, help='Set the inplace boolean explicitly.', default=None)
def action(path, param, action, inplace):
    if not path:
        click.echo('Missing PATH to a link in the document.')
        sys.exit(1)

    doc = get_document()
    if doc is None:
        click.echo('No current document. Use `coreapi get` to fetch a document first.')
        sys.exit(1)

    session = get_session()
    history = get_history()
    keys = coerce_key_types(doc, path)
    doc = session.action(doc, keys, params=param, action=action, inplace=inplace)
    history = history.add(doc)
    click.echo(display(doc))
    set_document(doc)
    set_history(history)


@click.command(help='Reload the current document.')
def reload_document():
    doc = get_document()
    if doc is None:
        click.echo('No current document. Use `coreapi get` to fetch a document first.')
        sys.exit(1)

    session = get_session()
    history = get_history()
    doc = session.reload(doc)
    history = history.add(doc)
    click.echo(display(doc))
    set_document(doc)
    set_history(history)


# Credentials

def get_credentials():
    if not os.path.isfile(credentials_path):
        return {}
    store = open(credentials_path, 'rb')
    credentials = json.loads(store.read())
    store.close()
    return credentials


def set_credentials(credentials):
    store = open(credentials_path, 'wb')
    store.write(json.dumps(credentials))
    store.close


@click.group(help='Configure request credentials. Request credentials are associated with a given domain, and used in request "Authorization:" headers.')
def credentials():
    pass


@click.command(help="List stored credentials.")
def credentials_show():
    credentials = get_credentials()
    if credentials:
        width = max([len(key) for key in credentials.keys()])
        fmt = '{domain:%d} "{header}"' % width

    click.echo(click.style('Credentials', bold=True))
    for key, value in sorted(credentials.items()):
        click.echo(fmt.format(domain=key, header=value))


@click.command(help="Add CREDENTIALS string for the given DOMAIN.")
@click.argument('domain', nargs=1)
@click.argument('header', nargs=1)
def credentials_add(domain, header):
    credentials = get_credentials()
    credentials[domain] = header
    set_credentials(credentials)

    click.echo(click.style('Added credentials', bold=True))
    click.echo('%s "%s"' % (domain, header))


@click.command(help="Remove credentials for the given DOMAIN.")
@click.argument('domain', nargs=1)
def credentials_remove(domain):
    credentials = get_credentials()
    credentials.pop(domain, None)
    set_credentials(credentials)

    click.echo(click.style('Removed credentials', bold=True))
    click.echo(domain)


# Headers

def get_headers():
    if not os.path.isfile(headers_path):
        return {}
    headers_file = open(headers_path, 'rb')
    headers = json.loads(headers_file.read())
    headers_file.close()
    return headers


def set_headers(headers):
    headers_file = open(headers_path, 'wb')
    headers_file.write(json.dumps(headers))
    headers_file.close()


def titlecase(header):
    return '-'.join([word.title() for word in header.split('-')])


@click.group(help="Configure custom request headers.")
def headers():
    pass


@click.command(help="List custom request headers.")
def headers_show():
    headers = get_headers()

    click.echo(click.style('Headers', bold=True))
    for key, value in sorted(headers.items()):
        click.echo(key + ': ' + value)


@click.command(help="Add custom request HEADER with given VALUE.")
@click.argument('header', nargs=1)
@click.argument('value', nargs=1)
def headers_add(header, value):
    header = titlecase(header)
    headers = get_headers()
    headers[header] = value
    set_headers(headers)

    click.echo(click.style('Added header', bold=True))
    click.echo('%s: %s' % (header, value))


@click.command(help="Remove custom request HEADER.")
@click.argument('header', nargs=1)
def headers_remove(header):
    header = titlecase(header)
    headers = get_headers()
    headers.pop(header, None)
    set_headers(headers)

    click.echo(click.style('Removed header', bold=True))
    click.echo(header)


# Headers

def get_bookmarks():
    if not os.path.isfile(bookmarks_path):
        return {}
    bookmarks_file = open(bookmarks_path, 'rb')
    bookmarks = json.loads(bookmarks_file.read())
    bookmarks_file.close()
    return bookmarks


def set_bookmarks(bookmarks):
    bookmarks_file = open(bookmarks_path, 'wb')
    bookmarks_file.write(json.dumps(bookmarks))
    bookmarks_file.close()


@click.group(help="Add, remove and show bookmarks.")
def bookmarks():
    pass


@click.command(help="List bookmarks.")
def bookmarks_show():
    bookmarks = get_bookmarks()

    if bookmarks:
        width = max([len(key) for key in bookmarks.keys()])
        fmt = '{name:%d} <{title} {url}>' % width

    click.echo(click.style('Bookmarks', bold=True))
    for key, value in sorted(bookmarks.items()):
        click.echo(fmt.format(name=key, title=value['title'] or 'Document', url=json.dumps(value['url'])))


@click.command(help="Add the current document to the bookmarks, with the given NAME.")
@click.argument('name', nargs=1)
def bookmarks_add(name):
    doc = get_document()
    if doc is None:
        click.echo('No current document. Use `coreapi get` to fetch a document first.')
        sys.exit(1)

    bookmarks = get_bookmarks()
    bookmarks[name] = {'url': doc.url, 'title': doc.title}
    set_bookmarks(bookmarks)

    click.echo(click.style('Added bookmark', bold=True))
    click.echo(name)


@click.command(help="Remove a bookmark with the given NAME.")
@click.argument('name', nargs=1)
def bookmarks_remove(name):
    bookmarks = get_bookmarks()
    bookmarks.pop(name, None)
    set_bookmarks(bookmarks)

    click.echo(click.style('Removed bookmark', bold=True))
    click.echo(name)


@click.command(help="Fetch the bookmarked document with the given NAME.")
@click.argument('name', nargs=1)
def bookmarks_get(name):
    bookmarks = get_bookmarks()
    bookmark = bookmarks.get(name)
    if bookmark is None:
        click.echo('Bookmark "%s" does not exist.' % name)
        return

    session = get_session()
    history = get_history()
    doc = session.get(bookmark['url'])
    history = history.add(doc)
    click.echo(display(doc))
    set_document(doc)
    set_history(history)


# History

def get_history():
    if not os.path.isfile(history_path):
        return coreapi.History(max_items=20)
    history_file = open(history_path, 'rb')
    bytestring = history_file.read()
    history_file.close()
    return coreapi.history.load_history(bytestring)


def set_history(history):
    bytestring = coreapi.history.dump_history(history)
    history_file = open(history_path, 'wb')
    history_file.write(bytestring)
    history_file.close()


@click.group(help="Navigate the browser history.")
def history():
    pass


@click.command(help="List the browser history.")
def history_show():
    history = get_history()

    click.echo(click.style('History', bold=True))
    for is_active, doc in history.get_items():
        prefix = '[*] ' if is_active else '[ ] '
        click.echo(prefix + get_document_string(doc))


@click.command(help="Navigate back through the browser history.")
def history_back():
    session = get_session()
    history = get_history()
    if history.is_at_oldest:
        click.echo("Currently at oldest point in history. Cannot navigate back.")
        return
    doc, history = history.back()
    doc = session.reload(doc)
    click.echo(display(doc))
    set_history(history)
    set_document(doc)


@click.command(help="Navigate forward through the browser history.")
def history_forward():
    session = get_session()
    history = get_history()
    if history.is_at_most_recent:
        click.echo("Currently at most recent point in history. Cannot navigate forward.")
        return
    doc, history = history.forward()
    doc = session.reload(doc)
    click.echo(display(doc))
    set_history(history)
    set_document(doc)


client.add_command(get)
client.add_command(show)
client.add_command(action)
client.add_command(reload_document, name='reload')
client.add_command(clear)

client.add_command(credentials)
credentials.add_command(credentials_add, name='add')
credentials.add_command(credentials_remove, name='remove')
credentials.add_command(credentials_show, name='show')

client.add_command(headers)
headers.add_command(headers_add, name='add')
headers.add_command(headers_remove, name='remove')
headers.add_command(headers_show, name='show')

client.add_command(bookmarks)
bookmarks.add_command(bookmarks_add, name='add')
bookmarks.add_command(bookmarks_get, name='get')
bookmarks.add_command(bookmarks_remove, name='remove')
bookmarks.add_command(bookmarks_show, name='show')

client.add_command(history)
history.add_command(history_back, name='back')
history.add_command(history_forward, name='forward')
history.add_command(history_show, name='show')


if __name__ == '__main__':
    client()
