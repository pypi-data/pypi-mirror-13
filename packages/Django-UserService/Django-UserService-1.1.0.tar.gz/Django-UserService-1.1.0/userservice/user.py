from django.http import HttpRequest
from django.conf import settings
from django.contrib.auth.models import User
import logging

from threading import currentThread


class UninitializedError(Exception):
    pass


class UserService:
    _user_data = {}
    logger = logging.getLogger(__name__)

    def _get_current_user_data(self):
        thread_id = currentThread()
        if not UserService._user_data:
            return {}
        if thread_id in UserService._user_data:
            return UserService._user_data[currentThread()]
        return {}

    def _require_middleware(self):
        if "initialized" not in self._get_current_user_data():
            if settings.DEBUG:
                print("You need to have this in settings.MIDDLEWARE_CLASSES: "
                      "'userservice.user.UserServiceMiddleware'")

            raise UninitializedError("Missing UserServiceMiddleware")

    def get_request(self):
        data = self._get_current_user_data()
        return data["request"]

    def get_user(self):
        self._require_middleware()
        request = self.get_request()
        return get_user(request)

    def get_acting_user(self):
        self._require_middleware()
        request = self.get_request()
        return get_acting_user(request)

    def get_original_user(self):
        self._require_middleware()
        request = self.get_request()
        return get_original_user(request)

    def get_override_user(self):
        self._require_middleware()
        request = self.get_request()
        return get_override_user(request)

    def set_user(self, user):
        user_data = self._get_current_user_data()
        user_data["original_user"] = user
        user_data["session"]["_us_user"] = user

    def set_override_user(self, override):
        self._require_middleware()
        request = self.get_request()
        return set_override_user(request, override)

    def clear_override(self):
        self._require_middleware()
        request = self.get_request()
        return clear_override(request)


class UserServiceMiddleware(object):

    logger = logging.getLogger(__name__)

    def process_request(self, request):
        thread = currentThread()
        UserService._user_data[thread] = {}
        UserService._user_data[thread]["initialized"] = True

        session = request.session
        UserService._user_data[thread]["session"] = session
        UserService._user_data[thread]["request"] = request

    def process_response(self, request, response):
        thread = currentThread()
        UserService._user_data[thread] = {}
        return response


def get_user(request):
    override = get_override_user(request)
    if override and len(override) > 0:
        return override

    actual = get_original_user(request)
    if not actual or len(actual) == 0:
        return None
    return actual


def get_acting_user(request):
    actual = get_original_user(request)
    if not actual or len(actual) > 0:
        return actual

    override = get_override_user(request)
    if override and len(override) == 0:
        return None
    return override


def get_original_user(request):
    if "_us_original_user" in request.session:
        return request.session["_us_original_user"]

    if hasattr(request, 'user'):
        return request.user.username

    return None


def get_override_user(request):
    if "_us_override_user" in request.session:
        return request.session["_us_override_user"]

    return None


def set_override_user(request, username):
    if "_us_original_user" not in request.session:
        request.session["_us_original_user"] = request.user.username

    request.session["_us_override_user"] = username

    new_user, created = User.objects.get_or_create(username=username)
    request.user = new_user


def clear_override(request):
    del request.session["_us_override_user"]

    username = get_original_user(request)
    new_user, created = User.objects.get_or_create(username=username)
    request.user = new_user
