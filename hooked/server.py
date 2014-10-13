from ConfigParser import RawConfigParser
from StringIO import StringIO
from pprint import pformat
import sys
import json
import subprocess
import logging

import bottle


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

cfg = RawConfigParser()
# set default cfg
cfg.readfp(StringIO("""
[server]
host = localhost
port = 8888
server = wsgiref
debug = false
"""))
# read global and custom cfg files
cfg.read(['/etc/hooked.cfg', './hooked.cfg'])


def checkcfg():
    errors = []
    hooks = set(cfg.sections())
    hooks.remove('server')
    for hook in hooks:
        if not cfg.has_option(hook, 'command'):
            errors.append('[%s] hook should have a "command" option.' % hook)
    if len(errors) > 0:
        log.error('\n--> '.join(['Aborting... Check config failed:'] + errors))
        sys.exit(1)


@bottle.get('/')
def index():
    #return bottle.redirect('https://github.com/bbinet/hooked')
    resp = {
        'success': True,
        'hooks': [],
        }
    hooks = set(cfg.sections())
    hooks.remove('server')
    for hook in hooks:
        items = dict(cfg.items(hook))
        resp['hooks'].append({
            'name': hook,
            'repository': items.get('repository'),
            'branch': items.get('branch'),
            'command': items['command'],
            'cwd': items.get('cwd'),
        })
    log.debug('GET / response =>\n%s' % pformat(resp))
    return resp


@bottle.post('/')
def hook():
    branch = None
    name = None
    data = None
    if bottle.request.json:
        data = bottle.request.json
    elif bottle.request.forms.get('payload', None):
        data = json.loads(bottle.request.forms.get('payload'))
    log.debug('POST / request =>\n%s' % pformat(data))

    if data:
        if 'slug' in data['repository']:
            name = data['repository']['slug']
        elif 'name' in data['repository']:
            name = data['repository']['name']
        if 'ref' in data:
            branch = data['ref'].split('/')[-1]
        elif 'commits' in data and len(data['commits']) > 0:
            branch = data['commits'][0]['branch']
    if not (name and branch):
        return bottle.HTTPError(status=400)

    hooks = set(cfg.sections())
    hooks.remove('server')
    resp = {
        'success': True,
        'hooks': [],
        }
    for hook in hooks:
        items = dict(cfg.items(hook))
        if 'repository' in items and name != items['repository']:
            log.debug('"%s" repository don\'t match [%s] hook' % (name, hook))
            continue
        if 'branch' in items and branch != items['branch']:
            log.debug('"%s" branch don\'t match [%s] hook' % (branch, hook))
            continue
        out, err = subprocess.Popen(
            [items['command'], name, branch],
            cwd=items.get('cwd'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            ).communicate()
        log.info('Running command: %s\n    --> STDOUT: %s\n    --> STDERR: %s'
                 % (' '.join([items['command'], name, branch]), out, err))
        resp['hooks'].append({
            'name': hook,
            'repository': items.get('repository'),
            'branch': items.get('branch'),
            'command': items['command'],
            'cwd': items.get('cwd'),
            'stdout': out,
            'stderr': err,
        })
    return resp


def run():
    if len(sys.argv) > 1:
        cfg.read(sys.argv[1:])
    debug = cfg.getboolean('server', 'debug')
    if debug:
        log.setLevel(logging.DEBUG)
        bottle.debug(True)
    checkcfg()
    bottle.run(
        server=cfg.get('server', 'server'),
        host=cfg.get('server', 'host'),
        port=cfg.get('server', 'port'),
        reloader=debug)


if __name__ == '__main__':
    cfg.set('server', 'debug', True)
    run()
