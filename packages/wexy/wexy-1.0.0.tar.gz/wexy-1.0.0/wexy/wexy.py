# coding:utf-8

from .rom import Rom


class Wexy(object):
    def __init__(self, environ):
        self._environ = Rom(environ)

    @property
    def environ(self):
        return self._environ

    def get(self, key, default=None):
        return self.environ.get(key, default)

    def get_http(self, key, default=None):
        return self.get('HTTP_' + key.upper(), default)

    def get_wsgi(self, key, default=None):
        return self.get('wsgi.' + key, default)

    """ https://www.python.org/dev/peps/pep-0333/ """
    @property
    def request_method(self):
        return self.get('REQUEST_METHOD')

    @property
    def script_name(self):
        return self.get('SCRIPT_NAME')

    @property
    def path_info(self):
        return self.get('PATH_INFO')

    @property
    def query_string(self):
        return self.get('QUERY_STRING')

    @property
    def content_type(self):
        return self.get('CONTENT_TYPE')

    @property
    def content_length(self):
        return self.get('CONTENT_LENGTH')

    @property
    def server_name(self):
        return self.get('SERVER_NAME')

    @property
    def server_port(self):
        return self.get('SERVER_PORT')

    @property
    def server_protocol(self):
        return self.get('SERVER_PROTOCOL')

    @property
    def wsgi_version(self):
        return self.get_wsgi('version')

    @property
    def wsgi_url_scheme(self):
        return self.get_wsgi('url_scheme')

    @property
    def wsgi_input(self):
        return self.get_wsgi('input')

    @property
    def wsgi_errors(self):
        return self.get_wsgi('errors')

    @property
    def wsgi_multithread(self):
        return self.get_wsgi('multithread')

    @property
    def wsgi_multiprocess(self):
        return self.get_wsgi('multiprocess')

    @property
    def wsgi_run_once(self):
        return self.get_wsgi('run_once')

    """ https://en.wikipedia.org/wiki/List_of_HTTP_header_fields """
    @property
    def http_accept(self):
        return self.get_http('accept')

    @property
    def http_accept_charset(self):
        return self.get_http('accept_charset')

    @property
    def http_accept_encoding(self):
        return self.get_http('accept_encoding')

    @property
    def http_accept_language(self):
        return self.get_http('accept_language')

    @property
    def http_accept_datetime(self):
        return self.get_http('accept_datetime')

    @property
    def http_authorization(self):
        return self.get_http('authorization')

    @property
    def http_connection(self):
        return self.get_http('connection')

    @property
    def http_expect(self):
        return self.get_http('expect')

    @property
    def http_forwarded(self):
        return self.get_http('forwarded')

    @property
    def http_from(self):
        return self.get_http('from')

    @property
    def http_if_modified_since(self):
        return self.get_http('if_modified_since')

    @property
    def http_if_range(self):
        return self.get_http('if_range')

    @property
    def http_if_unmodified_since(self):
        return self.get_http('if_unmodified_since')

    @property
    def http_via(self):
        return self.get_http('via')

    @property
    def http_warning(self):
        return self.get_http('warning')

    @property
    def http_x_forwarded_for(self):
        return self.get_http('x_forwarded_for')

    @property
    def http_x_forwarded_host(self):
        return self.get_http('x_forwarded_host')

    @property
    def http_front_end_https(self):
        return self.get_http('front_end_https')

    @property
    def http_x_att_deviceid(self):
        return self.get_http('x_att_deviceid')

    @property
    def http_x_wap_profile(self):
        return self.get_http('x_wap_profile')
