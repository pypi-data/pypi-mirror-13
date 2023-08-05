"""
Dependency management for tools.
"""

import os.path

import logging
log = logging.getLogger( __name__ )

from .resolvers import INDETERMINATE_DEPENDENCY
from .resolvers.galaxy_packages import GalaxyPackageDependencyResolver
from .resolvers.tool_shed_packages import ToolShedPackageDependencyResolver
from .resolvers.conda import CondaDependencyResolver
from galaxy.util import plugin_config

# TODO: Load these from the plugins. Would require a two step initialization of
# DependencyManager - where the plugins are loaded first and then the config
# is parsed and sent through.
EXTRA_CONFIG_KWDS = {
    'conda_prefix': None,
    'conda_exec': None,
    'conda_debug': None,
    'conda_channels': 'r,bioconda',
    'conda_auto_install': False,
    'conda_auto_init': False,
}


def build_dependency_manager( config ):
    if getattr( config, "use_tool_dependencies", False ):
        dependency_manager_kwds = {
            'default_base_path': config.tool_dependency_dir,
            'conf_file': config.dependency_resolvers_config_file,
        }
        for key, default_value in EXTRA_CONFIG_KWDS.iteritems():
            dependency_manager_kwds[key] = getattr(config, key, default_value)
        dependency_manager = DependencyManager( **dependency_manager_kwds )
    else:
        dependency_manager = NullDependencyManager()

    return dependency_manager


class NullDependencyManager( object ):

    def uses_tool_shed_dependencies(self):
        return False

    def dependency_shell_commands( self, requirements, **kwds ):
        return []

    def find_dep( self, name, version=None, type='package', **kwds ):
        return INDETERMINATE_DEPENDENCY


class DependencyManager( object ):
    """
    A DependencyManager attempts to resolve named and versioned dependencies by
    searching for them under a list of directories. Directories should be
    of the form:

        $BASE/name/version/...

    and should each contain a file 'env.sh' which can be sourced to make the
    dependency available in the current shell environment.
    """
    def __init__( self, default_base_path, conf_file=None, **extra_config ):
        """
        Create a new dependency manager looking for packages under the paths listed
        in `base_paths`.  The default base path is app.config.tool_dependency_dir.
        """
        if not os.path.exists( default_base_path ):
            log.warn( "Path '%s' does not exist, ignoring", default_base_path )
        if not os.path.isdir( default_base_path ):
            log.warn( "Path '%s' is not directory, ignoring", default_base_path )
        self.extra_config = extra_config
        self.default_base_path = os.path.abspath( default_base_path )
        self.resolver_classes = self.__resolvers_dict()
        self.dependency_resolvers = self.__build_dependency_resolvers( conf_file )

    def dependency_shell_commands( self, requirements, **kwds ):
        commands = []
        for requirement in requirements:
            log.debug( "Building dependency shell command for dependency '%s'", requirement.name )
            dependency = INDETERMINATE_DEPENDENCY
            if requirement.type in [ 'package', 'set_environment' ]:
                dependency = self.find_dep( name=requirement.name,
                                            version=requirement.version,
                                            type=requirement.type,
                                            **kwds )
            dependency_commands = dependency.shell_commands( requirement )
            if not dependency_commands:
                log.warn( "Failed to resolve dependency on '%s', ignoring", requirement.name )
            else:
                commands.append( dependency_commands )
        return commands

    def uses_tool_shed_dependencies(self):
        return any( map( lambda r: isinstance( r, ToolShedPackageDependencyResolver ), self.dependency_resolvers ) )

    def find_dep( self, name, version=None, type='package', **kwds ):
        log.debug('Find dependency %s version %s' % (name, version))
        for resolver in self.dependency_resolvers:
            dependency = resolver.resolve( name, version, type, **kwds )
            log.debug('Resolver %s returned %s (isnull? %s)' % (resolver.resolver_type, dependency,
                                                                dependency == INDETERMINATE_DEPENDENCY))
            if dependency != INDETERMINATE_DEPENDENCY:
                return dependency
        return INDETERMINATE_DEPENDENCY

    def __build_dependency_resolvers( self, conf_file ):
        if not conf_file:
            return self.__default_dependency_resolvers()
        if not os.path.exists( conf_file ):
            log.debug( "Unable to find config file '%s'", conf_file)
            return self.__default_dependency_resolvers()
        plugin_source = plugin_config.plugin_source_from_path( conf_file )
        return self.__parse_resolver_conf_xml( plugin_source )

    def __default_dependency_resolvers( self ):
        return [
            ToolShedPackageDependencyResolver(self),
            GalaxyPackageDependencyResolver(self),
            GalaxyPackageDependencyResolver(self, versionless=True),
            CondaDependencyResolver(self),
            CondaDependencyResolver(self, versionless=True),
        ]

    def __parse_resolver_conf_xml(self, plugin_source):
        """
        """
        extra_kwds = dict( dependency_manager=self )
        return plugin_config.load_plugins( self.resolver_classes, plugin_source, extra_kwds )

    def __resolvers_dict( self ):
        import galaxy.tools.deps.resolvers
        return plugin_config.plugins_dict( galaxy.tools.deps.resolvers, 'resolver_type' )
