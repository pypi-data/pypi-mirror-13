from impaf.testing import ControllerFixture
from implugin.formskit.controller import FormskitController

from ..controllers import BaseAuthController


class MockedAuthController(FormskitController):

    def _create_context(self):
        self.context = {}


class ExampleAuthController(BaseAuthController, MockedAuthController):
    pass


class TestBaseUathController(ControllerFixture):

    _testable_cls = ExampleAuthController

    def test_goto_login(self, testable, mredirect):
        testable.goto_login()

        mredirect.assert_called_once_with('auth:login')

    def test_goto_home(self, testable, mredirect):
        testable.goto_home()

        mredirect.assert_called_once_with('home')

    def test_get_main_template(self, testable):
        assert testable.get_main_template() == ''

    def test_create_context(self, testable):
        testable._create_context()

        assert testable.context == {
            'auth': {
                'main_template': '',
            }
        }
