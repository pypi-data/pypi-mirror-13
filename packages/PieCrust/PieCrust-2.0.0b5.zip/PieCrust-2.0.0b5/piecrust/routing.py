import re
import os.path
import copy
import logging
import urllib.parse
import unidecode


logger = logging.getLogger(__name__)


route_re = re.compile(r'%((?P<qual>path):)?(?P<name>\w+)%')
route_esc_re = re.compile(r'\\%((?P<qual>path)\\:)?(?P<name>\w+)\\%')
template_func_re = re.compile(r'^(?P<name>\w+)\((?P<first_arg>\w+)'
                              r'(?P<other_args>.*)\)\s*$')
template_func_arg_re = re.compile(r',\s*(?P<arg>\w+)')
ugly_url_cleaner = re.compile(r'\.html$')


class RouteNotFoundError(Exception):
    pass


def create_route_metadata(page):
    route_metadata = copy.deepcopy(page.source_metadata)
    route_metadata.update(page.getRouteMetadata())

    # TODO: fix this hard-coded shit
    for key in ['year', 'month', 'day']:
        if key in route_metadata and isinstance(route_metadata[key], str):
            route_metadata[key] = int(route_metadata[key])

    return route_metadata


class IRouteMetadataProvider(object):
    def getRouteMetadata(self):
        raise NotImplementedError()


SLUGIFY_ENCODE = 1
SLUGIFY_TRANSLITERATE = 2
SLUGIFY_LOWERCASE = 4
SLUGIFY_DOT_TO_DASH = 8
SLUGIFY_SPACE_TO_DASH = 16


re_first_dot_to_dash = re.compile(r'^\.+')
re_dot_to_dash = re.compile(r'\.+')
re_space_to_dash = re.compile(r'\s+')


def _parse_slugify_mode(value):
    mapping = {
            'encode': SLUGIFY_ENCODE,
            'transliterate': SLUGIFY_TRANSLITERATE,
            'lowercase': SLUGIFY_LOWERCASE,
            'dot_to_dash': SLUGIFY_DOT_TO_DASH,
            'space_to_dash': SLUGIFY_SPACE_TO_DASH}
    mode = 0
    for v in value.split(','):
        f = mapping.get(v.strip())
        if f is None:
            if v == 'iconv':
                raise Exception("'iconv' is not supported as a slugify mode "
                                "in PieCrust2. Use 'transliterate'.")
            raise Exception("Unknown slugify flag: %s" % v)
        mode |= f
    return mode


class Route(object):
    """ Information about a route for a PieCrust application.
        Each route defines the "shape" of an URL and how it maps to
        sources and taxonomies.
    """
    def __init__(self, app, cfg):
        self.app = app

        self.source_name = cfg['source']
        self.taxonomy_name = cfg.get('taxonomy')
        self.taxonomy_term_sep = cfg.get('term_separator', '/')

        sm = cfg.get('slugify_mode')
        if not sm:
            sm = app.config.get('site/slugify_mode', 'encode')
        self.slugify_mode = _parse_slugify_mode(sm)

        self.pretty_urls = app.config.get('site/pretty_urls')
        self.trailing_slash = app.config.get('site/trailing_slash')
        self.show_debug_info = app.config.get('site/show_debug_info')
        self.pagination_suffix_format = app.config.get(
                '__cache/pagination_suffix_format')
        self.uri_root = app.config.get('site/root')

        uri = cfg['url']
        self.uri_pattern = uri.lstrip('/')
        self.uri_format = route_re.sub(self._uriFormatRepl, self.uri_pattern)

        # Get the straight-forward regex for matching this URI pattern.
        p = route_esc_re.sub(self._uriPatternRepl,
                             re.escape(self.uri_pattern)) + '$'
        self.uri_re = re.compile(p)

        # If the URI pattern has a 'path'-type component, we'll need to match
        # the versions for which that component is empty. So for instance if
        # we have `/foo/%path:bar%`, we may need to match `/foo` (note the
        # lack of a trailing slash). We have to build a special pattern (in
        # this case without that trailing slash) to match those situations.
        # (maybe there's a better way to do it but I can't think of any
        # right now)
        uri_pattern_no_path = (
                route_re.sub(self._uriNoPathRepl, self.uri_pattern)
                .replace('//', '/')
                .rstrip('/'))
        if uri_pattern_no_path != self.uri_pattern:
            p = route_esc_re.sub(self._uriPatternRepl,
                                 re.escape(uri_pattern_no_path)) + '$'
            self.uri_re_no_path = re.compile(p)
        else:
            self.uri_re_no_path = None

        self.required_route_metadata = set()
        for m in route_re.finditer(self.uri_pattern):
            self.required_route_metadata.add(m.group('name'))

        self.template_func = None
        self.template_func_name = None
        self.template_func_args = []
        self._createTemplateFunc(cfg.get('func'))

    @property
    def is_taxonomy_route(self):
        return self.taxonomy_name is not None

    @property
    def source(self):
        for src in self.app.sources:
            if src.name == self.source_name:
                return src
        raise Exception("Can't find source '%s' for route '%'." % (
                self.source_name, self.uri))

    @property
    def source_realm(self):
        return self.source.realm

    def matchesMetadata(self, route_metadata):
        return self.required_route_metadata.issubset(route_metadata.keys())

    def matchUri(self, uri, strict=False):
        if not uri.startswith(self.uri_root):
            raise Exception("The given URI is not absolute: %s" % uri)
        uri = uri[len(self.uri_root):]

        if not self.pretty_urls:
            uri = ugly_url_cleaner.sub('', uri)
        elif self.trailing_slash:
            uri = uri.rstrip('/')

        route_metadata = None
        m = self.uri_re.match(uri)
        if m:
            route_metadata = m.groupdict()
        if self.uri_re_no_path:
            m = self.uri_re_no_path.match(uri)
            if m:
                route_metadata = m.groupdict()
        if route_metadata is None:
            return None

        if not strict:
            # When matching URIs, if the URI is a match but is missing some
            # metadata, fill those up with empty strings. This can happen if,
            # say, a route's pattern is `/foo/%slug%`, and we're matching an
            # URL like `/foo`.
            matched_keys = set(route_metadata.keys())
            missing_keys = self.required_route_metadata - matched_keys
            for k in missing_keys:
                route_metadata[k] = ''

        # TODO: fix this hard-coded shit
        for key in ['year', 'month', 'day']:
            if key in route_metadata and isinstance(route_metadata[key], str):
                try:
                    route_metadata[key] = int(route_metadata[key])
                except ValueError:
                    pass

        return route_metadata

    def getUri(self, route_metadata, *, sub_num=1):
        uri = self.uri_format % route_metadata
        suffix = None
        if sub_num > 1:
            # Note that we know the pagination suffix starts with a slash.
            suffix = self.pagination_suffix_format % {'num': sub_num}

        if self.pretty_urls:
            # Output will be:
            # - `subdir/name`
            # - `subdir/name/2`
            # - `subdir/name.ext`
            # - `subdir/name.ext/2`
            if suffix:
                if uri == '':
                    uri = suffix.lstrip('/')
                else:
                    uri = uri.rstrip('/') + suffix
            if self.trailing_slash and uri != '':
                uri = uri.rstrip('/') + '/'
        else:
            # Output will be:
            # - `subdir/name.html`
            # - `subdir/name/2.html`
            # - `subdir/name.ext`
            # - `subdir/name/2.ext`
            if uri == '':
                if suffix:
                    uri = suffix.lstrip('/') + '.html'
            else:
                base_uri, ext = os.path.splitext(uri)
                if not ext:
                    ext = '.html'
                if suffix:
                    uri = base_uri + suffix + ext
                else:
                    uri = base_uri + ext

        uri = self.uri_root + urllib.parse.quote(uri)

        if self.show_debug_info:
            uri += '?!debug'

        return uri

    def getTaxonomyTerms(self, route_metadata):
        if not self.is_taxonomy_route:
            raise Exception("This route isn't a taxonomy route.")

        tax = self.app.getTaxonomy(self.taxonomy_name)
        all_values = route_metadata.get(tax.term_name)
        if all_values is None:
            raise Exception("'%s' values couldn't be found in route metadata" %
                            tax.term_name)

        if self.taxonomy_term_sep in all_values:
            return tuple(all_values.split(self.taxonomy_term_sep))
        return all_values

    def slugifyTaxonomyTerm(self, term):
        if isinstance(term, tuple):
            return self.taxonomy_term_sep.join(
                    map(self._slugifyOne, term))
        return self._slugifyOne(term)

    def _slugifyOne(self, term):
        if self.slugify_mode & SLUGIFY_TRANSLITERATE:
            term = unidecode.unidecode(term)
        if self.slugify_mode & SLUGIFY_LOWERCASE:
            term = term.lower()
        if self.slugify_mode & SLUGIFY_DOT_TO_DASH:
            term = re_first_dot_to_dash.sub('', term)
            term = re_dot_to_dash.sub('-', term)
        if self.slugify_mode & SLUGIFY_SPACE_TO_DASH:
            term = re_space_to_dash.sub('-', term)
        return term

    def _uriFormatRepl(self, m):
        name = m.group('name')
        #TODO: fix this hard-coded shit
        if name == 'year':
            return '%(year)04d'
        if name == 'month':
            return '%(month)02d'
        if name == 'day':
            return '%(day)02d'
        return '%(' + name + ')s'

    def _uriPatternRepl(self, m):
        name = m.group('name')
        qualifier = m.group('qual')
        if qualifier == 'path' or self.taxonomy_name:
            return r'(?P<%s>[^\?]*)' % name
        return r'(?P<%s>[^/\?]+)' % name

    def _uriNoPathRepl(self, m):
        name = m.group('name')
        qualifier = m.group('qual')
        if qualifier == 'path':
            return ''
        return r'(?P<%s>[^/\?]+)' % name

    def _createTemplateFunc(self, func_def):
        if func_def is None:
            return

        m = template_func_re.match(func_def)
        if m is None:
            raise Exception("Template function definition for route '%s' "
                            "has invalid syntax: %s" %
                            (self.uri_pattern, func_def))

        self.template_func_name = m.group('name')
        self.template_func_args.append(m.group('first_arg'))
        arg_list = m.group('other_args')
        if arg_list:
            self.template_func_args += template_func_arg_re.findall(arg_list)

        if self.taxonomy_name:
            # This will be a taxonomy route function... this means we can
            # have a variable number of parameters, but only one parameter
            # definition, which is the value.
            if len(self.template_func_args) != 1:
                raise Exception("Route '%s' is a taxonomy route and must have "
                                "only one argument, which is the term value." %
                                self.uri_pattern)

            def template_func(*args):
                if len(args) == 0:
                    raise Exception(
                            "Route function '%s' expected at least one "
                            "argument." % func_def)

                # Term combinations can be passed as an array, or as multiple
                # arguments.
                values = args
                if len(args) == 1 and isinstance(args[0], list):
                    values = args[0]

                # We need to register this use of a taxonomy term.
                if len(values) == 1:
                    registered_values = values[0]
                else:
                    registered_values = tuple(values)
                eis = self.app.env.exec_info_stack
                cpi = eis.current_page_info.render_ctx.current_pass_info
                if cpi:
                    cpi.used_taxonomy_terms.add(
                            (self.source_name, self.taxonomy_name,
                                registered_values))

                str_values = self.slugifyTaxonomyTerm(registered_values)
                term_name = self.template_func_args[0]
                metadata = {term_name: str_values}

                return self.getUri(metadata)

        else:
            # Normal route function.
            def template_func(*args):
                if len(args) != len(self.template_func_args):
                    raise Exception(
                            "Route function '%s' expected %d arguments, "
                            "got %d." %
                            (func_def, len(self.template_func_args),
                                len(args)))
                metadata = {}
                for arg_name, arg_val in zip(self.template_func_args, args):
                    #TODO: fix this hard-coded shit.
                    if arg_name in ['year', 'month', 'day']:
                        arg_val = int(arg_val)
                    metadata[arg_name] = arg_val
                return self.getUri(metadata)

        self.template_func = template_func


class CompositeRouteFunction(object):
    def __init__(self):
        self._funcs = []
        self._arg_names = None

    def addFunc(self, route):
        if self._arg_names is None:
            self._arg_names = sorted(route.template_func_args)

        if sorted(route.template_func_args) != self._arg_names:
            raise Exception("Cannot merge route function with arguments '%s' "
                            "with route function with arguments '%s'." %
                            (route.template_func_args, self._arg_names))
        self._funcs.append((route, route.template_func))

    def __call__(self, *args, **kwargs):
        if len(self._funcs) == 1 or len(args) == len(self._arg_names):
            f = self._funcs[0][1]
            return f(*args, **kwargs)

        if len(args) == len(self._arg_names) + 1:
            f_args = args[:-1]
            for r, f in self._funcs:
                if r.source_name == args[-1]:
                    return f(f_args, **kwargs)
            raise Exception("No such source: %s" % args[-1])

        raise Exception("Incorrect number of arguments for route function. "
                        "Expected '%s', got '%s'" % (self._arg_names, args))

