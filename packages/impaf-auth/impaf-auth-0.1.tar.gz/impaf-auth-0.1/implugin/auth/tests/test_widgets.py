from mock import patch
from mock import sentinel
from mock import MagicMock

from pytest import fixture
from pytest import yield_fixture

from implugin.sqlalchemy.testing import SqlalchemyRequestFixture

from ..widgets import LoginFormWidget


class TestLoginFormWidget(SqlalchemyRequestFixture):

    @fixture
    def form(self):
        return MagicMock()

    @fixture
    def testable(self, mrequest, form):
        return LoginFormWidget(form)

    def test_init(self, testable):
        assert (
            testable.templates['text']
            == 'implugin.auth.widgets:/templates/forms/text.jinja2'
        )
