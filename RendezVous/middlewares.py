from django.http import HttpResponse, HttpResponseBadRequest
from RendezVous.utils import AnonymizeIP

class CustomMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        remote_addr = request.META.get('REMOTE_ADDR')
        remote_addr = AnonymizeIP(remote_addr)[:16]
        requested_path = request.path
        if requested_path in ['/admin/','/admin'] and remote_addr == '127.0.0.1':

            return HttpResponseBadRequest()

        response = self.get_response(request)

        return response
