from mock import patch

from pytest import yield_fixture
from pytest import fixture

from impaf.testing import ControllerFixture


class AuthControllerFixture(ControllerFixture):

    @yield_fixture
    def mgoto_home(self, testable):
        patcher = patch.object(testable, 'goto_home')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mgoto_login(self, testable):
        patcher = patch.object(testable, 'goto_login')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mget_user(self, testable):
        patcher = patch.object(testable, 'get_user')
        with patcher as mock:
            yield mock

    @fixture
    def fuser(self, mget_user):
        return mget_user.return_value
