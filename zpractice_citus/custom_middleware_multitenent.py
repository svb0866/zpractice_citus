from django_multitenant.utils import set_current_tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # one time configuration and initialisation

    def __call__(self, request):
        if request.user.is_authenticated:
            current_tenant = request.user.get_tenant_for_user()
            set_current_tenant(current_tenant)
            print(current_tenant)

        response = self.get_response(request)
        return response
