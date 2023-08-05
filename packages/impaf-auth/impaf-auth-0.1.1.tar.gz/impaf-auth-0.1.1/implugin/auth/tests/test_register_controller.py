from implugin.formskit.testing import FormskitControllerFixture

from implugin.auth.testing import AuthControllerFixture
from ..controllers import RegisterController
from .test_login_controller import MockedBaseAuthController


class ExampleRegisterController(RegisterController, MockedBaseAuthController):
    pass


class TestRegisterController(AuthControllerFixture, FormskitControllerFixture):
    _testable_cls = ExampleRegisterController

    def test_create_context(self, testable):
        testable._create_context()

        assert testable.context == {
            'auth': {
                'header': RegisterController.header_text,
            }
        }

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
            RegisterController.form_cls,
            widgetcls=RegisterController.form_widget_cls
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
            RegisterController.form_cls,
            widgetcls=RegisterController.form_widget_cls
        )
        mgoto_home.assert_called_once_with()
