# -*- coding: utf-8 -*-

"""Recipe tomcat"""

import os
import stat
from mako.template import Template
from subprocess import check_call, CalledProcessError

import zc.buildout
from birdhousebuilder.recipe import conda, supervisor

catalina_sh = Template(filename=os.path.join(os.path.dirname(__file__), "catalina-wrapper.sh"))
users_xml = Template(filename=os.path.join(os.path.dirname(__file__), "tomcat-users.xml"))
server_xml = Template(filename=os.path.join(os.path.dirname(__file__), "server.xml"))

def tomcat_home(prefix):
    home_path = os.path.join(prefix, 'opt', 'apache-tomcat')
    conda.makedirs(os.path.dirname(home_path))
    return home_path

def content_root(prefix):
    root_path = os.path.join(prefix, 'var', 'lib', 'tomcat', 'content')
    conda.makedirs(os.path.dirname(root_path))
    return root_path

def unzip(prefix, warfile):
    warname = os.path.basename(warfile)
    dirname = warname[0:-4]
    appspath = os.path.join(tomcat_home(prefix), 'webapps')
    dirpath = os.path.join(appspath, dirname)
    if not os.path.isdir(dirpath):
        try:
            check_call(['unzip', '-q', os.path.join(appspath, warname), '-d', dirpath])
        except CalledProcessError:
            raise
        except:
            raise
        
class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs apache-tomcat as conda package and setups tomcat configuration"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        self.options['user'] = self.options.get('user', '')
        self.options['http_port'] = self.options.get('http_port', '8080')
        self.options['https_port'] = self.options.get('https_port', '8443')
        self.options['Xmx'] = self.options.get('Xmx', '1024m')
        self.options['Xms'] = self.options.get('Xms', '128m')
        self.options['MaxPermSize'] = self.options.get('MaxPermSize', '128m')
        self.options['content_root'] = content_root(self.prefix)
        self.options['ncwms_password'] = self.options.get('ncwms_password', '')

    def install(self, update=False):
        installed = []
        installed += list(self.install_tomcat(update))
        installed += list(self.setup_catalina_wrapper())
        installed += list(self.setup_users_config())
        installed += list(self.setup_server_config())
        installed += list(self.setup_supervisor(update))
        return installed

    def install_tomcat(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'apache-tomcat'})
        if update == True:
            return script.update()
        else:
            return script.install()

    def setup_catalina_wrapper(self):
        result = catalina_sh.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'bin', 'catalina-wrapper.sh')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        # make sure script is executable for all
        os.chmod(output, 0o755)
        return [output]

    def setup_users_config(self):
        result = users_xml.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'tomcat-users.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def setup_server_config(self):
        result = server_xml.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'server.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]
    
    def setup_supervisor(self, update=False):
        content_path = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'content')
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'user': self.options.get('user'),
             'program': 'tomcat',
             'command': '{0}/opt/apache-tomcat/bin/catalina-wrapper.sh'.format(self.prefix),
             })
        return script.install(update)

    def update(self):
        return self.install(update=True)

def uninstall(name, options):
    pass

