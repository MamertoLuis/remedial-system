from .models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Assume a URL structure like /t/<tenant_code>/...
        path_parts = request.path.split('/')
        if len(path_parts) > 2 and path_parts[1] == 't':
            tenant_code = path_parts[2]
            try:
                tenant = Tenant.objects.get(code=tenant_code)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None
        
        response = self.get_response(request)
        return response
