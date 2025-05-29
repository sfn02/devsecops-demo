from django.http import HttpResponse, HttpResponseBadRequest
from RendezVous.utils import AnonymizeIP

class CustomMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        remote_addr = request.META.get('REMOTE_ADDR')
        remote_addr = AnonymizeIP(remote_addr)[:16]
        requested_path = request.path
        print(f"user {request.user} requested {requested_path} from {remote_addr}")
        if requested_path in ['/admin/','/admin'] and remote_addr == '127.0.0.1':
            return HttpResponseBadRequest()

        # the view (and later middleware) are called.

        response = self.get_response(request)
        print(f"user {request.user} requested {requested_path} from {remote_addr}")
        # Code to be executed for each request/response after
        # the view is called.

        return response
