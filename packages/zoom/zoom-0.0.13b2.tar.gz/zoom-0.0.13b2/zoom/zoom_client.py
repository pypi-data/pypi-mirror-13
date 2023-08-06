import os
import sys
import click

from zoom_project import ZoomProject
from zoom_error import ZoomError

def _stringify(o):
    '''
    Convert object o to str if unicode

    args:
        o: object to convert (dict, tuple, list, unicode)
    return:
        object matching the input type without unicode
    '''
    if type(o) is unicode:
        return str(o)
    elif type(o) is list or type(o) is tuple:
        return [_stringify(value) for value in o]
    elif type(o) is dict:
        return {key: _stringify(value) for key, value in o.iteritems()}
    else:
        return o

def load_zoom_proj(*args, **kwargs):
    '''
    Single source for an instance of a ZoomProject.
    Entirely added for testing. Click makes mocking a pain in the ass.
    '''
    return ZoomProject(*args, **kwargs)

#
# CLI entrypoint
#

@click.group()
@click.pass_context
def cli(ctx):
    zoom_proj = None
    if ctx.invoked_subcommand != 'init':
        try:
            zoom_proj = load_zoom_proj()
        except ZoomError as e:
            print 'fatal:', e
            sys.exit(1)
    ctx.obj = zoom_proj

#
# INIT
#

@cli.command(help='create a new, empty zoom project. '
             'generates a zoomfile (zoom.yml)')
def init():
    try:
        load_zoom_proj(create=True)
        print "zoom project created"
    except ZoomError as e:
        print 'fatal:', e
        sys.exit(1)

#
# ADD commands
#

def _add_resource(zoom_proj, rtype, args):
    '''
    Wrapper for zoom_proj.add_resource to ensure args are in
    the correct format.
    '''
    args = _stringify(args)
    try:
        resource = zoom_proj.add_resource(rtype, args)
        print "added resource {}".format(str(resource))
    except ZoomError as e:
        print 'fatal:', e
        sys.exit(1)

@cli.command('add-git', help='add a git module to this zoom project.')
@click.option('-c', '--commit', metavar='<commit>',
              help='sha to lock to')
@click.option('-b', '--branch', metavar='<branch>',
              help='branch to track')
@click.option('-t', '--tag', metavar='<tag>',
              help='tag to lock to')
@click.argument('url')
@click.argument('path', required=False)
@click.pass_obj
def add_git(zoom_proj, commit, branch, tag, url, path):
    args = {'commit': commit,
            'branch': branch,
            'tag': tag,
            'url': url,
            'path': path}
    _add_resource(zoom_proj, 'git', args)

@cli.command('add-file', help='add a file dep to this zoom project.')
@click.option('-f', '--filename', metavar='<filename>',
              help='filename to resolve to')
@click.argument('url')
@click.argument('path', required=False)
@click.pass_obj
def add_file(zoom_proj, filename, url, path):
    args = {'filename': filename,
            'url': url,
            'path': path}
    _add_resource(zoom_proj, 'file', args)

#
# Foreach
#

@cli.command(help='run a command across multiple modules.')
@click.argument('command')
@click.argument('limit', nargs=-1)
@click.pass_obj
def foreach(zoom_proj, command, limit):
    command = _stringify(command)
    limit = _stringify(limit)
    results = zoom_proj.foreach_module(command, limit=limit)
    for module, result in results.iteritems():
        print str(module)
        err = result['retcode'] != 0
        text = result['stderr'] if err else result['stdout']
        print '\t' + ('\n\t'.join(text.split('\n')))

#
# LIST
#

@cli.command(help='list all resources in this zoom project.')
@click.pass_obj
def list(zoom_proj):
    resources = zoom_proj.get_resources()
    for resource in resources:
        print str(resource)

#
# STATUS
#

@cli.command(help='display the current status for all resources.')
@click.pass_obj
def status(zoom_proj):
    resources = zoom_proj.get_resources()
    for resource in resources:
        print str(resource)
        print '\t' + ('\n\t'.join(resource.status().split('\n')))

#
# SYNC
#

def sync_cb(r):
    '''
    Callback - print start status
    '''
    print 'syncing {}...'.format(str(r))


def sync_err_cb(r, e):
    '''
    Callback - print sync error
    '''
    print 'error syncing {} - {}'.format(str(r), str(e))

@cli.command(help='download resources to thier specified state and location.')
@click.option('-e', '--exact', is_flag=True,
              help='sync modules to the exact commit set in the zoomfile. '
              'this will override branch tracking.')
@click.option('-f', '--force', is_flag=True,
              help='delete and re-sync resources')
@click.argument('limit', nargs=-1)
@click.pass_obj
def sync(zoom_proj, exact, force, limit):
    limit = _stringify(limit)
    zoom_proj.sync(force=force,
                   exact=exact,
                   limit=limit,
                   sync_cb=sync_cb,
                   error_cb=sync_err_cb)
    print 'sync complete'

#
# REV-LOCK
#

@cli.command('rev-lock', help='lock a module to a commit. If no commit '
             'specified, use the last synced commit')
@click.argument('module')
@click.argument('commit', required=False)
@click.pass_obj
def rev_lock(zoom_proj, module, commit):
    module = _stringify(module)
    commit = _stringify(commit)
    try:
        module = zoom_proj.lock_commit(module, commit)
        print 'locked {}@{}'.format(str(module), module.commit)
    except ZoomError as e:
        print 'fatal:', e
        sys.exit(1)

#
# TAG-LOCK
#

@cli.command('tag-lock', help='lock modules to a specified tag.')
@click.argument('tag')
@click.argument('limit', nargs=-1)
@click.pass_obj
def tag_lock(zoom_proj, tag, limit):
    tag = _stringify(tag)
    limit = _stringify(limit)
    try:
        modules = zoom_proj.lock_tag(tag, limit=limit)
        for module in modules:
            print 'locked {}@{}'.format(str(module), module.tag)
    except ZoomError as e:
        print 'fatal:', e
        sys.exit(1)
