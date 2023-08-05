from mock import patch
from mock import sentinel
from mock import MagicMock

from pytest import fixture
from pytest import yield_fixture

from implugin.sqlalchemy.testing import SqlalchemyRequestFixture

from ..requestable import AuthRequestable


class TestAuthRequestable(SqlalchemyRequestFixture):

    @fixture
    def testable(self, mrequest):
        obj = AuthRequestable()
        obj.request = mrequest
        return obj

    @yield_fixture
    def mgenerate_user(self, testable):
        patcher = patch.object(testable, '_generate_user')
        with patcher as mock:
            yield mock

    def test_get_user_when_not_created(self, testable, mgenerate_user):
        assert testable.get_user() == mgenerate_user.return_value

        mgenerate_user.assert_called_once_with()
        assert testable._user == mgenerate_user.return_value

    def test_get_user_when_created(self, testable, mgenerate_user):
        testable._user = sentinel.user
        assert testable.get_user() == sentinel.user

        assert not mgenerate_user.called

    def test_generate_user_when_not_authenticated(self, testable, mrequest):
        mrequest.unauthenticated_userid = None
        testable._not_logged_user_cls = MagicMock()
        not_logged_user = testable._not_logged_user_cls.return_value

        assert testable._generate_user() == not_logged_user

    def test_generate_user_when_authenticated(
        self,
        testable,
        mrequest,
        mdrivers,
    ):
        mrequest.unauthenticated_userid = sentinel.userid
        user_from_db = mdrivers.Auth.get_by_id.return_value

        assert testable._generate_user() == user_from_db
        mdrivers.Auth.get_by_id.assert_called_once_with(sentinel.userid)
