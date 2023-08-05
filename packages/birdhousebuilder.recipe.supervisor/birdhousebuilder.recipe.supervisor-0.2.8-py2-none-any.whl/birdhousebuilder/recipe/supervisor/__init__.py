# -*- coding: utf-8 -*-

"""Recipe supervisor"""

import os
from mako.template import Template

from birdhousebuilder.recipe import conda
from birdhousebuilder.recipe.conda import as_bool

templ_config = Template(filename=os.path.join(os.path.dirname(__file__), "supervisord.conf"))
templ_program = Template(filename=os.path.join(os.path.dirname(__file__), "program.conf"))
templ_start_stop = Template(filename=os.path.join(os.path.dirname(__file__), "supervisord"))

class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs supervisor as conda package and setups configuration."""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        
        bin_path = os.path.join(self.prefix, 'bin')
        lib_path = os.path.join(self.prefix, 'lib')
        self.tmp_path = os.path.join(self.prefix, 'var', 'tmp')

        # buildout options used for supervisord.conf
        
        self.options['host'] = b_options.get('supervisor-host', '127.0.0.1')
        self.options['port'] = b_options.get('supervisor-port', '9001')
        self.options['username'] = b_options.get('supervisor-username', '')
        self.options['password'] = b_options.get('supervisor-password', '')
        self.options['use_monitor'] = b_options.get('supervisor-use-monitor', 'true')
        self.options['chown'] = b_options.get('supervisor-chown', '')
        self.options['loglevel'] = b_options.get('supervisor-loglevel', 'info')

        # options used for program config
        
        self.program = self.options.get('program', name)
        logfile = os.path.join(self.prefix, 'var', 'log', 'supervisor', self.program + ".log")
        # set default options
        self.options['user'] = self.options.get('user', '')
        self.options['directory'] =  self.options.get('directory', bin_path)
        self.options['priority'] = self.options.get('priority', '999')
        self.options['autostart'] = self.options.get('autostart', 'true')
        self.options['autorestart'] = self.options.get('autorestart', 'false')
        self.options['stdout_logfile'] = self.options.get('stdout_logfile', logfile)
        self.options['stderr_logfile'] = self.options.get('stderr_logfile', logfile)
        self.options['startsecs'] = self.options.get('startsecs', '1')
        self.options['numprocs'] = self.options.get('numprocs', '1')
        self.options['stopwaitsecs'] = self.options.get('stopwaitsecs', '10')
        self.options['stopasgroup'] = self.options.get('stopasgroup', 'false')
        self.options['killasgroup'] = self.options.get('killasgroup', 'true')
        self.options['stopsignal'] = self.options.get('stopsignal', 'TERM')
        self.options['environment'] = self.options.get(
            'environment',
            'PATH="/bin:/usr/bin:%s",LD_LIBRARY_PATH="%s",PYTHON_EGG_CACHE="%s"' % (bin_path, lib_path, self.tmp_path))

    def install(self, update=False):
        installed = []
        installed += list(self.install_supervisor(update))
        installed += list(self.install_config())
        installed += list(self.install_program())
        installed += list(self.install_start_stop())
        return installed

    def install_supervisor(self, update):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'supervisor'})
        conda.makedirs(os.path.join(self.prefix, 'var', 'run'))
        conda.makedirs(os.path.join(self.prefix, 'var', 'log', 'supervisor'))
        conda.makedirs(os.path.join(self.tmp_path))
        if update == True:
            return script.update()
        else:
            return script.install()
        
    def install_config(self):
        """
        install supervisor main config file
        """
        result = templ_config.render(**self.options)

        output = os.path.join(self.prefix, 'etc', 'supervisor', 'supervisord.conf')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]
        
    def install_program(self):
        """
        install supervisor program config file
        """
        result = templ_program.render(**self.options)
        output = os.path.join(self.prefix, 'etc', 'supervisor', 'conf.d', self.program + '.conf')
        conda.makedirs(os.path.dirname(output))
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_start_stop(self):
        result = templ_start_stop.render(
            prefix=self.prefix)
        output = os.path.join(self.prefix, 'etc', 'init.d', 'supervisord')
        conda.makedirs(os.path.dirname(output))
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
            os.chmod(output, 0o755)
        return [output]

    def update(self):
        return self.install(update=True)

def uninstall(name, options):
    pass

