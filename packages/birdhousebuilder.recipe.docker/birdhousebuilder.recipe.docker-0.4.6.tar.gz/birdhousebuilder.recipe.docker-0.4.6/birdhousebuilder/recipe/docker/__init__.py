# -*- coding: utf-8 -*-

"""Recipe docker"""

import os
import shlex
import shutil
from mako.template import Template

import logging
logger = logging.getLogger(__name__)

templ_dockerignore = Template(filename=os.path.join(os.path.dirname(__file__), "dot_dockerignore"))
templ_dockerfile = Template(filename=os.path.join(os.path.dirname(__file__), "Dockerfile"))
templ_custom_cfg = Template(filename=os.path.join(os.path.dirname(__file__), "custom.cfg"))

def command_to_yaml(command):
    mylist = shlex.split( command )
    cmd = ', '.join( ['"%s"' % el for el in mylist] )
    cmd = '[%s]' % cmd
    return cmd


class Recipe(object):
    """Buildout recipe to generate a Dockerfile."""

    def __init__(self, buildout, name, options):
        self.buildout, self.name = buildout, name
        b_options = buildout['buildout']
        self.buildout_dir = b_options.get('directory')

        self.options = dict()
        self.options['image_name'] = options.get('image-name', 'birdhouse/bird-base')
        self.options['image_version'] = options.get('image-version', 'latest')
        self.options['maintainer'] = options.get('maintainer', 'https://github.com/bird-house')
        self.options['description'] = options.get('description', 'Birdhouse Application')
        self.options['vendor'] = options.get('vendor', 'Birdhouse')
        self.options['version'] = options.get('version', '1.0.0')
        self.options['source'] = options.get('source', '.')
        self.options['git_url'] = options.get('git-url')
        self.options['git_branch'] = options.get('git-branch', 'master')
        self.options['subdir'] = options.get('subdir')
        self.options['buildout_cfg'] = options.get('buildout-cfg')
        self.options['command'] = command_to_yaml( options.get('command', 'make update-config start') )
        self.options['expose'] = ' '.join([port for port in options.get('expose', '').split() if port])
        envs = [env for env in options.get('environment', '').split() if env]
        self.options['environment'] = {k:v for k,v in (env.split('=') for env in envs) }
        settings = [setting for setting in options.get('settings', '').split() if setting]
        self.options['settings'] = {k:v for k,v in (setting.split('=') for setting in settings) }

    def install(self):
        installed = []
        installed += list(self.install_dockerignore())
        installed += list(self.install_dockerfile())
        installed += list(self.install_custom_cfg())
        return installed

    def install_dockerignore(self):
        result = templ_dockerignore.render(**self.options)
        output = os.path.join(self.buildout_dir, '.dockerignore')
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
            os.chmod(output, 0o644)
        return tuple()
    
    def install_dockerfile(self):
        result = templ_dockerfile.render(**self.options)
        output = os.path.join(self.buildout_dir, 'Dockerfile')
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
            os.chmod(output, 0o644)
        return tuple()

    def install_custom_cfg(self):
        result = templ_custom_cfg.render(**self.options)
        output = os.path.join(self.buildout_dir, '.docker.cfg')
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
            os.chmod(output, 0o644)
        return [output]

    def update(self):
        return self.install()

def uninstall(name, options):
    pass

