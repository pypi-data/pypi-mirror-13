from pyramid.security import forget

from implugin.formskit.controller import FormskitController

from .forms import LoginForm
from .forms import RegisterForm
from .requestable import AuthRequestable
from .widgets import LoginFormWidget


class BaseAuthController(FormskitController, AuthRequestable):

    def goto_login(self):
        self.redirect('auth:login')

    def goto_home(self):
        self.redirect('home')

    def get_main_template(self):
        return ''

    def _create_context(self):
        super()._create_context()
        self.context['auth'] = {
            'main_template': self.get_main_template(),
        }


class LoginController(BaseAuthController):

    renderer = 'implugin.auth.controllers:templates/login.jinja2'
    form_widget_cls = LoginFormWidget
    form_cls = LoginForm
    permission = 'guest'
    header_text = 'Login'
    enable_register_link = True

    def _create_context(self):
        super()._create_context()
        self.context['auth']['header'] = self.header_text
        self.context['auth']['enable_register_link'] = (
            self.enable_register_link
        )

    def make(self):
        if self.get_user().is_authenticated:
            self.goto_home()
            return

        form = self.add_form(self.form_cls, widgetcls=self.form_widget_cls)
        if form.validate():
            self.goto_home()
            return


class ForbiddenController(BaseAuthController):

    renderer = 'implugin.auth.controllers:templates/forbidden.jinja2'
    header_text = 'Forbidden'

    def _create_context(self):
        super()._create_context()
        self.context['auth']['header'] = self.header_text

    def make(self):
        if not self.get_user().is_authenticated:
            self.goto_login()
            return


class LogoutController(BaseAuthController):
    permission = 'auth'

    def make(self):
        headers = forget(self.request)
        self.request.response.headerlist.extend(headers)
        self.goto_login()


class RegisterController(BaseAuthController):
    renderer = 'implugin.auth.controllers:templates/register.jinja2'
    form_widget_cls = LoginFormWidget
    form_cls = RegisterForm
    permission = 'guest'
    header_text = 'Register'

    def _create_context(self):
        super()._create_context()
        self.context['auth']['header'] = self.header_text

    def make(self):
        form = self.add_form(self.form_cls, widgetcls=self.form_widget_cls)
        if form.validate():
            self.goto_home()
            return
