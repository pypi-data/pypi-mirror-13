from __future__ import absolute_import


class CORSMiddleware(object):
    """The middleware used for CORS (Cross-Origin Resource Sharing).

    The CORS behaviors are implemented according to the guidelines from
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS
    """

    #: Access control options
    cors_allow_origin = '*'  # any domain
    cors_allow_credentials = False
    cors_allow_methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
    cors_allow_headers = ()  # any headers
    cors_max_age = 864000  # 10 days

    def make_preflight_headers(self, request_headers, allow_origin=None,
                               allow_credentials=None, allow_methods=None,
                               allow_headers=None, max_age=None):
        """Make reasonable CORS response headers for preflight requests.
        """
        allow_origin = allow_origin or self.cors_allow_origin
        allow_credentials = allow_credentials or self.cors_allow_credentials
        allow_methods = allow_methods or self.cors_allow_methods
        allow_headers = allow_headers or self.cors_allow_headers
        # If the `Access-Control-Allow-Headers` header is specified as
        # an empty tuple (i.e. `()`), then allow the headers specified in
        # the `Access-Control-Request-Headers` header (if exists)
        if not allow_headers and request_headers is not None:
            allow_headers = request_headers.split(', ')
        max_age = max_age or self.cors_max_age

        headers = {
            'Access-Control-Allow-Origin': allow_origin,
            'Access-Control-Allow-Methods': ', '.join(allow_methods),
            'Access-Control-Max-Age': '%d' % max_age,
        }
        if allow_headers:
            headers.update({
                'Access-Control-Allow-Headers': ', '.join(allow_headers)
            })
        if allow_credentials:
            headers.update({'Access-Control-Allow-Credentials': 'true'})
        if allow_origin != '*':
            headers.update({'Vary': 'Origin'})

        return headers

    def make_actual_headers(self, request_origin, allow_origin=None,
                            allow_credentials=None):
        """Make reasonable CORS response headers for actual requests.
        """
        allow_origin = allow_origin or self.cors_allow_origin
        # If the `Access-Control-Allow-Origin` header is specified as
        # a wildcard (i.e. `*`), then only allow the origin of the
        # current request (if exists)
        if allow_origin == '*' and request_origin is not None:
            allow_origin = request_origin
        allow_credentials = allow_credentials or self.cors_allow_credentials

        headers = {'Access-Control-Allow-Origin': allow_origin}
        if allow_credentials:
            headers.update({'Access-Control-Allow-Credentials': 'true'})
        if allow_origin != '*':
            headers.update({'Vary': 'Origin'})

        return headers

    def is_preflight_request(self, request):
        """Judge if the `request` object is a preflight request."""
        return (request.method == 'OPTIONS' and
                'Origin' in request.headers and
                'Access-Control-Request-Method' in request.headers)

    def process_request(self, request):
        """Handle the preflight request correctly.

        :param request: the request object.
        """
        if self.is_preflight_request(request):
            request_headers = request.headers.get(
                'Access-Control-Request-Headers'
            )
            headers = self.make_preflight_headers(request_headers)
            return '', 200, headers

    def process_response(self, request, response):
        """Add appropriate response headers for the actual request.

        :param request: the request object.
        :param response: the response object.
        """
        if not self.is_preflight_request(request):
            request_origin = request.headers.get('Origin')
            headers = self.make_actual_headers(request_origin)
            response.headers.update(headers)
        return response
