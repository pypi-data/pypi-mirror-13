# -*- coding: utf-8 -*-

"""Recipe solr"""

import os
import shutil
from mako.template import Template

from birdhousebuilder.recipe import conda, supervisor

templ_solr_env = Template(filename=os.path.join(os.path.dirname(__file__), "templates", "solr.in.sh"))
templ_log4j = Template(filename=os.path.join(os.path.dirname(__file__), "templates", "log4j.properties"))
templ_solr_core = Template(filename=os.path.join(os.path.dirname(__file__), "templates", "core.properties"))

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        
        self.options['hostname'] = options.get('hostname', 'localhost')
        self.options['http_port'] = options.get('http_port', '8983')
        self.options['sites'] = options.get('sites', 'birdhouse')
        self.options['core'] = options.get('core', 'birdhouse')
        self.options['user'] = options.get('user', '')
        self.solr_home = os.path.join(self.prefix, 'var', 'lib', 'solr')
        self.options['solr_home'] = self.solr_home


    def install(self, update=False):
        installed = []
        installed += list(self.install_solr(update))
        installed += list(self.install_solr_server())
        installed += list(self.install_env())
        installed += list(self.install_log4j())
        installed += list(self.install_core())
        installed += list(self.install_supervisor(update))
        return installed

    
    def install_solr(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'solr'})
        
        if update == True:
            return script.update()
        else:
            return script.install()

        
    def install_solr_server(self):
        conda.makedirs(self.solr_home)
        solr_xml = os.path.join(os.path.dirname(__file__), "templates", "solr.xml")
        out_solr_xml = os.path.join(self.solr_home, "solr.xml")
        shutil.copy(solr_xml, out_solr_xml)
        return [out_solr_xml]

    
    def install_env(self):
        result = templ_solr_env.render(**self.options)
        output = os.path.join(self.solr_home, 'solr.in.sh')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    
    def install_log4j(self):
        result = templ_log4j.render(**self.options)
        output = os.path.join(self.solr_home, 'log4j.properties')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    
    def install_core(self):
        core_dir = os.path.join(self.solr_home, self.options.get('core'))
        conda.makedirs(core_dir)
        
        result = templ_solr_core.render(**self.options)
        output = os.path.join(core_dir, 'core.properties')

        with open(output, 'wt') as fp:
            fp.write(result)

        conf_dir = os.path.join(core_dir, "conf")
        conda.makedirs(conf_dir) 

        solrconfig_xml = os.path.join(os.path.dirname(__file__), "templates", "solrconfig.xml")
        out_solrconfig_xml = os.path.join(conf_dir, "solrconfig.xml")
        shutil.copy(solrconfig_xml, out_solrconfig_xml)

        schema_xml = os.path.join(os.path.dirname(__file__), "templates", "schema.xml")
        out_schema_xml = os.path.join(conf_dir, "schema.xml")
        shutil.copy(schema_xml, out_schema_xml)

        return [output, out_solrconfig_xml, out_schema_xml]

    
    def install_supervisor(self, update=False):
        solr_dir = os.path.join(self.prefix, 'opt', 'solr')
        solr_env = os.path.join(self.solr_home, 'solr.in.sh')
        script = supervisor.Recipe(
            self.buildout,
            self.options.get('sites'),
            {'user': self.options.get('user'),
             'program': 'solr',
             'command': '{0}/bin/solr start -f'.format(solr_dir),
             'environment': 'SOLR_INCLUDE="{0}"'.format(solr_env),
             'directory': solr_dir,
             'stopwaitsecs': '10',
             'killasgroup': 'true',
             'stopasgroup': 'true',
             'stopsignal': 'KILL',
             })
        if update == True:
            return script.update()
        else:
            return script.install()

    def update(self):
        return self.install(update=True)

def uninstall(name, options):
    pass

