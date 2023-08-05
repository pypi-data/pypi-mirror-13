from mock import patch

from pytest import fixture
from pytest import yield_fixture

from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Deny
from pyramid.security import Everyone

from impaf.testing import RequestFixture

from ..entry import EntryFactory
from ..models import NotLoggedUser
from ..models import Permission


class TestEntryFactory(RequestFixture):

    @yield_fixture
    def mget_user(self):
        patcher = patch.object(EntryFactory, 'get_user')
        with patcher as mock:
            yield mock

    @fixture
    def muser(self, mget_user):
        return mget_user.return_value

    def test_not_logged(self, mget_user, request):
        """
        When user is not logged, then there should be no extra acl entrys.
        """
        mget_user.user = NotLoggedUser()

        obj = EntryFactory(request)

        assert obj.__acl__ == [
            (Allow, Everyone, 'view'),
            (Deny, Authenticated, 'guest'),
            (Allow, Everyone, 'guest'),
            (Allow, Authenticated, 'auth'),
        ]

    def test_logged_in(self, request, muser):
        """
        When user is logged in, all his permissions should be added to the acl
        list.
        """
        permission = Permission(name='myname', group='mygroup')
        muser.permissions = [permission]

        obj = EntryFactory(request)

        assert obj.__acl__ == [
            (Allow, Everyone, 'view'),
            (Deny, Authenticated, 'guest'),
            (Allow, Everyone, 'guest'),
            (Allow, Authenticated, 'auth'),
            (Allow, Authenticated, 'mygroup:myname'),
        ]
