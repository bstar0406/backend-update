from rest_framework.parsers import BaseParser

class ValidationMiddleware(BaseParser):
    """
    Parse body of requests and validate against a set of required and optional fields
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """

        logging.info(f'middleware saw request')
        return stream.read()



#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#         logging.info(f'middleware initialized!')
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#
#         response = self.get_response(request)
#
#         logging.info(f'middleware ran!')
#
#         # Code to be executed for each request/response after
#         # the view is called.
#
#         return response