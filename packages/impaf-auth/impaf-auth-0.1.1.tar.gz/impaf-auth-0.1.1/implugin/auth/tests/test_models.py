from mock import MagicMock
from mock import create_autospec
from mock import patch

from pytest import fixture
from pytest import raises
from pytest import yield_fixture

from impaf.controller import Controller
from impaf.testing import RequestFixture

from ..models import User
from ..models import Permission
from ..models import NotLoggedUser


class TestUser(RequestFixture):

    @fixture
    def testable(self):
        return User()

    def test_repr(self, testable):
        testable.id = 10
        testable.name = 'name'
        testable.email = 'myemail@elo.com'
        assert repr(testable) == 'User: name (myemail@elo.com)'

    @yield_fixture
    def mhas_permission(self, testable):
        patcher = patch.object(testable, 'has_permission')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mhas_access_to_controller(self, testable):
        patcher = patch.object(testable, 'has_access_to_controller')
        with patcher as mock:
            yield mock

    def test_password(self, testable):
        """Setted password should be validated. Wrong one should not."""
        testable.set_password('god')

        assert testable.validate_password('god') is True
        assert testable.validate_password('god2') is False

    def test_is_authenticated(self, testable):
        """User should always be logged. Only FakeUser should not be logged."""
        assert testable.is_authenticated() is True

    def test_has_permission_success(self, testable):
        """has_permission should return True if permission is in user
        permissions"""
        permission = MagicMock()
        permission.name = 'name'
        permission.group = 'group'
        testable.permissions.append(permission)
        assert testable.has_permission('group', 'name') is True

    def test_has_permission_fail(self, testable):
        """has_permission should return False if permission is not in user
        permissions"""
        assert testable.has_permission('group', 'name') is False

        permission = MagicMock()
        testable.permissions.append(permission)
        permission.name = 'bad name'
        permission.group = 'group'
        assert testable.has_permission('group', 'name') is False

    def test_has_access_to_route(
        self,
        testable,
        mhas_access_to_controller,
        registry,
    ):
        """has_access_to_route should find controller and use
        has_access_to_controller"""
        registry['route'] = MagicMock()
        registry['route'].routes = {
            'myroute': 'ctrl',
        }
        testable.registry = registry

        result = testable.has_access_to_route('myroute')

        assert result == mhas_access_to_controller.return_value
        mhas_access_to_controller.assert_called_once_with('ctrl')

    def test_has_access_to_controller_success(self, testable, mhas_permission):
        """has_access_to_controller should get permissions from ctrl, and
        return True if user has all permissions"""
        ctrl = MagicMock()
        ctrl.permissions = [('base', 'view')]
        mhas_permission.return_value = True

        assert testable.has_access_to_controller(ctrl) is True

        mhas_permission.assert_called_once_with('base', 'view')

    def test_has_access_to_controller_fail(self, testable, mhas_permission):
        """has_access_to_controller should get permissions from ctrl, and
        return False if user has not one of that permissions"""
        ctrl = MagicMock()
        ctrl.permissions = [('base', 'view')]
        mhas_permission.return_value = False

        assert testable.has_access_to_controller(ctrl) is False

        mhas_permission.assert_called_once_with('base', 'view')


class TestNotLoggedUser(RequestFixture):

    @fixture
    def testable(self, request):
        return NotLoggedUser()

    def test_has_permission(self, testable):
        """FakeUser should not have any permissions."""
        assert testable.has_permission('base', 'view') is False

    def test_set_password(self, testable):
        """FakeUser can not change his password."""
        with raises(NotImplementedError):
            testable.set_password('password',)

    def test_validate_password(self, testable):
        """FakeUser can not check his password."""
        with raises(NotImplementedError):
            testable.validate_password('password',)

    def test_is_authenticated(self, testable):
        """FakeUser is not and can not be logged."""
        assert testable.is_authenticated() is False

    def test_has_access_to_controller(self, testable):
        """FakeUser has access only to controllers without permissions."""
        ctrl = create_autospec(Controller)
        assert testable.has_access_to_controller(ctrl) is True

        ctrl.permissions = [1]
        assert testable.has_access_to_controller(ctrl) is False


class TestPermission(RequestFixture):

    @fixture
    def testable(self):
        return Permission()

    def test_repr(self, testable):
        testable.name = 'n1'
        testable.group = 'g1'
        assert repr(testable) == 'Permission: n1:g1'
