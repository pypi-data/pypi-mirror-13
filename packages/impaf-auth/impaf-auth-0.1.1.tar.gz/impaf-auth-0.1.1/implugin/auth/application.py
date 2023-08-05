from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from impaf.application import Application


class AuthApplication(Application):
    _authorization_policy = ACLAuthorizationPolicy

    def _get_config_kwargs(self):
        data = super()._get_config_kwargs()

        data['authentication_policy'] = AuthTktAuthenticationPolicy(
            self.settings['auth_secret'],
            hashalg=self.settings.get('auth_hashalg', 'sha512'),
        )
        data['authorization_policy'] = self._authorization_policy()

        return data
