from implugin.formskit.widget import FormWidget


class LoginFormWidget(FormWidget):

    class Templates(FormWidget.Templates):
        password = 'implugin.auth.widgets:/templates/forms/password.jinja2'
        text = 'implugin.auth.widgets:/templates/forms/text.jinja2'
