from django.contrib import auth
from django.contrib.auth.middleware import AuthenticationMiddleware

import base64


class AutologinAuthenticationMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        if 'autologin' not in request.COOKIES:
            return
        if request.COOKIES['autologin'] == '':
            auth.logout(request)
            return
        autologin_cookie_value = base64.b64decode(request.COOKIES['autologin'])
        # Py3 uses a bytes string here, so we need to decode to utf-8
        autologin_cookie_value = autologin_cookie_value.decode('utf-8')
        username = autologin_cookie_value.split(':')[0]
        password = autologin_cookie_value.split(':')[1]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
