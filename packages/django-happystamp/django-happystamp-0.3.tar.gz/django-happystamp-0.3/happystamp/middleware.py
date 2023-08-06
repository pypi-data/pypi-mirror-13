from mezzanine.core.middleware import TemplateForHostMiddleware
from mezzanine.core.middleware import TemplateForDeviceMiddleware
from rest_framework.response import Response

class SmileTemplateForHostMiddleware(TemplateForHostMiddleware):    
    def process_template_response(self, request, response):
        if not isinstance(response, Response):
            return super().process_template_response(request, response)
        
        return response
    
    
class SmileTemplateForDeviceMiddleware(TemplateForDeviceMiddleware):
    def process_template_response(self, request, response):
        if not isinstance(response, Response):
            return super().process_template_response(request, response)
        
        return response