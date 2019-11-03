from django.contrib.auth.mixins import AccessMixin


class LoginRequiredNotClientMixin(AccessMixin):
    """Verify that the current user is authenticated and is not a client."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_client:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
