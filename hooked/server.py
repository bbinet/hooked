import configparser
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pprint import pformat
from typing import Any, List

import bottle

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)-15s %(levelname)s: %(message)s')
log = logging.getLogger(__name__)
config = configparser.ConfigParser()
config['server'] = {
    'host': 'localhost',
    'port': '8888',
    'server': 'wsgiref',
    'debug': 'false',
}

# read global and custom cfg files
config.read(['/etc/hooked.cfg', './hooked.cfg'])


@dataclass
class Hook:
    repository: str
    branch: str
    command: str

    def __init__(
            self,
            name: str,
            repository: str,
            branch: str,
            command: str,
            cwd: str,
            *_args: Any,
            **_kwargs: Any,
    ) -> None:
        self.name = name
        self.repository = repository
        self.branch = branch
        self.command = command
        self.cwd = cwd

    def __str__(self):
        return f'{self.name}@{self.repository} on {self.branch} does {self.command} in {self.cwd}'


def config_check() -> List[Hook]:
    correct_hooks: List[Hook] = []
    config_hooks = [a for a in set(config.sections()) if a != 'server']
    for hook_data in config_hooks:
        try:
            # This will test and fail the first missing config option
            # TODO: it would be nice to test and report them all
            correct_hooks.append(
                Hook(
                    hook_data,
                    config[hook_data]['repository'],
                    config[hook_data]['branch'],
                    config[hook_data]['command'],
                    config[hook_data]['cwd'],
                )
            )
        except KeyError as e:
            log.error(f'[{hook_data}] is missing{str(e)}')
        except TypeError as e:
            msg = str(e).replace('__init__() ', '').replace('positional ', '').replace('argument', 'option')
            log.error(f'[{hook_data}] {msg}')
    return correct_hooks


@bottle.get('/')
def index():
    resp = {
        'success': True,
        'hooks': [],
    }
    hooks = config_check()
    for hook in hooks:
        resp['hooks'].append({
            'name': hook.name,
            'repository': hook.repository,
            'branch': hook.branch,
            'command': hook.command,
            'cwd': hook.cwd,
        })
    log.debug(f'GET / response =>\n{pformat(resp)}')
    return resp


@bottle.get('/hooks/<repo>/<branch>')
def run_hooks(repo, branch):
    if not (repo and branch):
        return bottle.HTTPError(status=400)
    hooks = config_check()
    resp = {
        'success': True,
        'hooks': [],
    }
    for hook in hooks:
        if repo != hook.repository:
            log.debug(f'"{repo}" repository don\'t match [{hook.name}] hook')
            continue
        if branch != hook.branch:
            log.debug(f'"{branch}" branch don\'t match [{hook.name}] hook')
            continue
        resp['hooks'].append(run_hook(hook, repo, branch))
        log.debug(resp)
    return resp


@bottle.post('/')
def run_git_hooks():
    branch = None
    repo = None
    data = None
    if bottle.request.json:
        data = bottle.request.json
    elif bottle.request.forms.get('payload', None):
        data = json.loads(bottle.request.forms.get('payload'))
    log.debug(f'POST / request =>\n{pformat(data)}')

    if data:
        if 'slug' in data['repository']:
            repo = data['repository']['slug']
        elif 'name' in data['repository']:
            repo = data['repository']['name']
        if 'ref' in data:
            branch = data['ref'].split('/')[-1]
        elif 'commits' in data and len(data['commits']) > 0:
            branch = data['commits'][0]['branch']
        elif 'push' in data and 'changes' in data['push'] \
                and len(data['push']['changes']) > 0:
            branch = data['push']['changes'][0]['new']['name']

    return run_hooks(repo, branch)


@bottle.get('/hook/<hook>')
def run_hook(hook, repo='', branch=''):
    if not config.has_section(hook.name):
        return bottle.HTTPError(status=404)
    # optionally get repository/branch from query params
    repo = bottle.request.query.get('repository', repo)
    branch = bottle.request.query.get('branch', branch)

    out, err = subprocess.Popen(
        [hook.command, repo, branch],
        cwd=hook.cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    log.info('Running command: {%s}\n'
             '--> STDOUT: %s\n'
             '--> STDERR: %s'
             % (' '.join([hook.command, repo, branch]),
                out.decode("utf-8"),
                err.decode("utf-8")))
    return {
        'name': hook.name,
        'repository': hook.repository,
        'branch': hook.branch,
        'command': hook.command,
        'cwd': hook.cwd,
        'stdout': out.decode("utf-8"),
        'stderr': err.decode("utf-8"),
    }


def run():
    if len(sys.argv) > 1:
        config.read(sys.argv[1:])
    debug = config.getboolean('server', 'debug')
    if debug:
        log.setLevel(logging.DEBUG)
        bottle.debug(True)
    valid_hooks = config_check()
    if len(valid_hooks) > 0:
        bottle.run(
            server=config.get('server', 'server'),
            host=config.get('server', 'host'),
            port=config.get('server', 'port'),
            reloader=debug)
    else:
        log.error('Config check failed. Exiting ...')
        sys.exit(1)


if __name__ == '__main__':
    config['server']['debug'] = 'true'
    run()
