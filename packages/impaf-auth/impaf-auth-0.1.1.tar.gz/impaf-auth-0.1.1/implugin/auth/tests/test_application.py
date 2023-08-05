from mock import patch
from mock import MagicMock

from pytest import fixture
from pytest import yield_fixture

from impaf.application import Application

from ..application import AuthApplication


class MockedAuthApplication(Application):

    def _get_config_kwargs(self):
        self._data = {}
        return self._data


class ExampleAuthApplication(
    AuthApplication,
    MockedAuthApplication,
):
    pass


class TestAuthApplication(object):

    @fixture
    def testable(self):
        return ExampleAuthApplication('module')

    @yield_fixture
    def mAuthTktAuthenticationPolicy(self):
        patcher = patch(
            'implugin.auth.application.AuthTktAuthenticationPolicy'
        )
        with patcher as mock:
            yield mock

    def test_get_config_kwargs(self, testable, mAuthTktAuthenticationPolicy):
        testable.settings = {
            'auth_secret': 'secret',
        }
        auth_policy = MagicMock()
        testable._authorization_policy = auth_policy

        data = testable._get_config_kwargs()

        assert data == {
            'authentication_policy': mAuthTktAuthenticationPolicy.return_value,
            'authorization_policy': auth_policy.return_value,
        }
        mAuthTktAuthenticationPolicy.assert_called_once_with(
            'secret',
            hashalg='sha512',
        )
        auth_policy.assert_called_once_with()
