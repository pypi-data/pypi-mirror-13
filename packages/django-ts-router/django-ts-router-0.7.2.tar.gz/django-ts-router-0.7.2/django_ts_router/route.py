# vim:fileencoding=utf-8
import json
import logging
import re

from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.template.loader import render_to_string
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)

TAB_SPACE_LENGTH = 4
TAB_SPACES = ' ' * TAB_SPACE_LENGTH


class RoutePattern(object):
    def __init__(self, name, pattern, pattern_prefix=''):
        """
        :param str name:
        :param RegexURLPattern pattern:
        :param str base:
        """
        self._name = name
        self._base = pattern_prefix
        self._pattern = pattern

    @cached_property
    def simplified_pattern(self):
        """
        :rtype: str
        """
        pattern = self._base + self._pattern.regex.pattern
        return simplify_regex(pattern)

    @cached_property
    def pattern_args(self):
        """
        :rtype: list[str]
        """
        return re.findall(r'<(.+?)>', self.simplified_pattern)

    def __repr__(self):
        return "<RoutePattern {name} {pattern}".format(name=self._name, pattern=self.simplified_pattern)

    def to_dict(self):
        """
        :rtype: dict
        """
        return {
            self._name: {
                'pattern': self.simplified_pattern,
                'arguments': self.pattern_args,
            }
        }

    def export_name_to_ts(self):
        return 'export var {constant}:string = "{name}";'.format(
            constant=self._get_constant(),
            name=self._name
        )

    def _get_constant(self):
        return self._name.upper().replace(':', '_').replace('-', '_')

    def generate_function(self):
        """Returnes a string of a function "getXxxxURL()" in which
        reverse() function invokes.

        :rtype: str
        """
        function_name = self._get_function_name()
        arguments_with_type = [arg + ':string' for arg in self.pattern_args]
        arguments = ', '.join(arguments_with_type)

        body = 'var args:{[arg: string]: string} = {};\n'
        for arg in self.pattern_args:
            body += 'args["%s"] = %s;\n' % (arg, arg)
        body += 'return reverse(%s, args);' % self._get_constant()
        return 'export function %s(%s):string {\n%s\n}' % (function_name, arguments, body)

    def _get_function_name(self):
        """Generates a function name 'getXxxxURL'.

        Converts snake case (snake_case) to lower camel case (lowerCamelCase).
        http://stackoverflow.com/a/19053800/3073708

        :type: str
        """
        name = self._name.replace(':', '_').replace('-', '_')
        components = name.split('_')
        return 'get%sURL' % ''.join(x.title() for x in components)


class Router(object):
    DEFAULT_MODULE = 'django.tsrouter'

    def __init__(self):
        urlconf = __import__(settings.ROOT_URLCONF, fromlist=['urlpatterns'])
        self._route_patterns = self.parse_urlpatterns(urlconf.urlpatterns)

        router_settings = getattr(settings, 'TS_ROUTER', None)
        if not router_settings:
            raise RuntimeError('TS_ROUTER setting is not found in your settings file.')
        self.module = router_settings.get('MODULE', self.DEFAULT_MODULE)
        self.names = router_settings.get('NAMES')
        if not self.names:
            raise RuntimeError('One or more NAMES should be specified.')

    def find_route_pattern_by_name(self, name):
        """
        :rtype: RoutePattern
        """
        return self._route_patterns[name]

    def find_names_by_namespace(self, namespace):
        names = list(self._route_patterns)
        namespace += ':'
        matched = filter(lambda n: n.startswith(namespace), names)
        return list(matched)

    @classmethod
    def parse_urlpatterns(cls, urlpatterns, pattern_prefix='', namespace=None, route_patterns=None):
        """

        Reference: django.contrib.admindocs.views.extract_views_from_urlpatterns

        :rtype: dict[str, RoutePattern]
        """
        if not route_patterns:
            route_patterns = {}

        for urlpattern in urlpatterns:
            logger.debug(urlpattern)
            if hasattr(urlpattern, 'url_patterns'):
                logger.debug('hey')
                route_patterns = cls.parse_urlpatterns(urlpattern.url_patterns,
                                                       pattern_prefix=(pattern_prefix + urlpattern.regex.pattern),
                                                       namespace=(urlpattern.namespace or namespace),
                                                       route_patterns=route_patterns)

            elif hasattr(urlpattern, 'callback'):
                if namespace:
                    name = "{namespace}:{name}".format(namespace=namespace, name=urlpattern.name)
                else:
                    name = urlpattern.name

                # Ignore URL pattern without name
                if not name:
                    continue

                route_pattern = RoutePattern(pattern_prefix=pattern_prefix, name=name, pattern=urlpattern)
                route_patterns[name] = route_pattern
        return route_patterns

    def generate_router_typescript(self, names, module):
        """Generates a router TypeScript code for URLs of the given names.

        :param list[str] names: URL names to be output
        :param str module: Module name like "com.example.router"
        :return: TypeScript code
        :rtype: str
        """
        the_names = []
        for name in names:
            if ':*' in name:
                namespace = name.split(':*')[0]
                the_names += self.find_names_by_namespace(namespace)
            else:
                the_names.append(name)

        # Remove duplicated names
        names = set(the_names)
        patterns = [self.find_route_pattern_by_name(name) for name in names]

        var_names = []
        functions = []
        d = {}
        for p in patterns:
            d.update(p.to_dict())
            var_names.append(p.export_name_to_ts())
            functions.append(p.generate_function())
        var_names = ('\n' + TAB_SPACES).join(var_names)
        functions = '\n'.join(functions)
        urlpatterns_json = json.dumps(d, indent=4)
        # Format json string for output as TypeScript source.
        urlpatterns_json = '\n'.join(
            [TAB_SPACES + line if index > 0 else line for index, line in
             enumerate(urlpatterns_json.split('\n'))])

        c = {
            'module': module,
            'names': var_names,
            'functions': functions,
            'url_patterns': urlpatterns_json,
        }
        return render_to_string('django_ts_router/router.ts.tmpl', c)

    def export(self, module=None):
        """Generates a router TypeScript code which belongs to the given module.

        When the 'module' argument is not given, self.module is used.

        :param str module: Module name like "com.example.router"
        :return: TypeScript code
        :rtype: str
        """
        if not module:
            module = self.module
        return self.generate_router_typescript(self.names, module)
