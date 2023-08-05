from django.contrib.auth.views import redirect_to_login


class IsStaffOrSuperUserMixin(object):
    """
    CBV mixin which verifies that the current user is authenticated. and has staff or superuser rights
    """
    login_url = None
    redirect_field_name = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            # continue to url
            return super(IsStaffOrSuperUserMixin, self).dispatch(request, *args, **kwargs)
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(),
                                 self.get_redirect_field_name())

    def get_login_url(self):
        return self.login_url

    def get_redirect_field_name(self):
        return self.redirect_field_name
