from implugin.formskit.testing import FormskitControllerFixture

from implugin.auth.testing import AuthControllerFixture
from ..controllers import LoginController
from ..controllers import BaseAuthController


class MockedBaseAuthController(BaseAuthController):

    def _create_context(self):
        self.context = {
            'auth': {},
        }


class ExampleLoginController(LoginController, MockedBaseAuthController):
    pass


class TestLoginController(AuthControllerFixture, FormskitControllerFixture):
    _testable_cls = ExampleLoginController

    def test_create_context(self, testable):
        testable._create_context()

        assert testable.context == {
            'auth': {
                'header': LoginController.header_text,
                'enable_register_link': LoginController.enable_register_link,
            }
        }

    def test_make_on_authenticated_user(self, testable, mgoto_home, fuser):
        fuser.is_authenticated.return_value = True

        testable.make()

        mgoto_home.assert_called_once_with()

    def test_make_on_unauthenticated_user(
        self,
        testable,
        mgoto_home,
        fuser,
        fform,
        madd_form,
    ):
        fuser.is_authenticated.return_value = False
        fform.validate.return_value = False

        testable.make()

        madd_form.assert_called_once_with(
            LoginController.form_cls,
            widgetcls=LoginController.form_widget_cls
        )
        assert mgoto_home.called is False

    def test_make_on_unauthenticated_user_submit(
        self,
        testable,
        mgoto_home,
        fuser,
        fform,
        madd_form,
    ):
        fuser.is_authenticated.return_value = False
        fform.validate.return_value = True

        testable.make()

        madd_form.assert_called_once_with(
            LoginController.form_cls,
            widgetcls=LoginController.form_widget_cls
        )
        mgoto_home.assert_called_once_with()
