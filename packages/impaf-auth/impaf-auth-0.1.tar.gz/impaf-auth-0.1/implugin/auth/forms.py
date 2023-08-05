from pyramid.security import remember

from formskit.formvalidators import FormValidator
from formskit.validators import NotEmpty

from implugin.formskit.models import PostForm

from .requestable import AuthRequestable


class LoginMixin(AuthRequestable):

    def _force_login(self, user_id):
        headers = remember(self.request, str(user_id))
        self.request.response.headers.extend(headers)


class EmailMustExists(FormValidator):

    message = "EmailMustExists"

    def validate(self):
        email = self.form.get_value('email')
        self.form._user = self.form.drivers.auth.get_by_email(email)
        return self.form._user is not None


class EmailMustNotExists(EmailMustExists):
    message = "EmailMustNotExists"

    def validate(self):
        return not super().validate()


class ValidateUserPassword(FormValidator):

    message = "ValidateUserPassword"

    def validate(self):
        password = self.form.get_value('password')
        return self.form._user.validate_password(password)


class PasswordsMustMatch(FormValidator):

    message = "PasswordsMustMatch"

    def validate(self):
        password = self.form.get_value('password')
        confirm_password = self.form.get_value('confirm_password')
        return password == confirm_password


class LoginForm(PostForm, LoginMixin):

    def create_form(self):
        self.add_field('email', label='E-mail', validators=[NotEmpty()])
        self.add_field('password', label='Hasło', validators=[NotEmpty()])

        self.add_form_validator(EmailMustExists())
        self.add_form_validator(ValidateUserPassword())

    def on_success(self):
        self._force_login(self._user.id)


class RegisterForm(PostForm, LoginMixin):

    def create_form(self):
        self.add_field(
            'name',
            label='Imię',
            validators=[NotEmpty()],
        )
        self.add_field(
            'email',
            label='E-mail',
            validators=[NotEmpty()],
        )
        self.add_field(
            'password',
            label='Hasło',
            validators=[NotEmpty()],
        )
        self.add_field(
            'confirm_password',
            label='Powtórz hasło',
            validators=[NotEmpty()],
        )

        self.add_form_validator(EmailMustNotExists())
        self.add_form_validator(PasswordsMustMatch())

    def on_success(self):
        user = self.drivers.auth.create(
            name=self.get_value('name'),
            email=self.get_value('email'),
            password=self.get_value('password'),
        )
        self.database().commit()
        self._force_login(user.id)
