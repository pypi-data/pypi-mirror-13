from mock import patch

from pytest import yield_fixture

from implugin.formskit.testing import FormskitControllerFixture

from implugin.auth.testing import AuthControllerFixture
from ..controllers import LogoutController
from .test_login_controller import MockedBaseAuthController


class ExampleLogoutController(LogoutController, MockedBaseAuthController):
    pass


class TestLogoutController(AuthControllerFixture, FormskitControllerFixture):
    _testable_cls = ExampleLogoutController

    @yield_fixture
    def mforget(self):
        patcher = patch('implugin.auth.controllers.forget')
        with patcher as mock:
            yield mock

    def test_make(self, testable, mforget, mrequest, mgoto_login):
        testable.make()

        mforget.assert_called_once_with(mrequest)
        headers = mforget.return_value
        mrequest.response.headerlist.extend(headers)
        mgoto_login.assert_called_once_with()
