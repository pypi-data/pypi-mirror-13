from urllib import urlencode

# Event format:
# event = {
#     "body": {},
#     "headers": {
#         "Via": "1.1 e604e934e9195aaf3e36195adbcb3e18.cloudfront.net (CloudFront)",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip",
#         "CloudFront-Is-SmartTV-Viewer": "false",
#         "CloudFront-Forwarded-Proto": "https",
#         "X-Forwarded-For": "109.81.209.118, 216.137.58.43",
#         "CloudFront-Viewer-Country": "CZ",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#         "X-Forwarded-Proto": "https",
#         "X-Amz-Cf-Id": "LZeP_TZxBgkDt56slNUr_H9CHu1Us5cqhmRSswOh1_3dEGpks5uW-g==",
#         "CloudFront-Is-Tablet-Viewer": "false",
#         "X-Forwarded-Port": "443",
#         "CloudFront-Is-Mobile-Viewer": "false",
#         "CloudFront-Is-Desktop-Viewer": "true"
#     },
#     "params": {
#         "a_path": "asdf1",
#         "b_path": "asdf2",
#     },
#     "method": "GET",
#     "query": { 
#         "dead": "beef" 
#     }
# }

def create_wsgi_request(event_info, server_name='zappa'):
        """
        Given some event_info,
        create and return a valid WSGI request environ.
        """

        method = event_info['method']
        body = event_info['body']
        params = event_info['params']
        query = event_info['query']

        path = "/"
        for key in sorted(params.keys()):
            path = path + params[key] + "/"

        query_string = urlencode(query)

        environ = {
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'REMOTE_ADDR': str('127.0.0.1'),
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': str(''),
            'SERVER_NAME': str(server_name),
            'SERVER_PORT': str('80'),
            'SERVER_PROTOCOL': str('HTTP/1.1'),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': str('http'),
            'wsgi.input': str(body),
            'wsgi.errors': str(''),
            'wsgi.multiprocess': False,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
        }

        for header in event_info["headers"]:
            wsgi_name = "HTTP_" + header.upper().replace('-', '_')
            environ[wsgi_name] = event_info["headers"][header]

        return environ