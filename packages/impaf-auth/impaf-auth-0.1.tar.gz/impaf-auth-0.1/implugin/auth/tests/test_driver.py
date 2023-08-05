from mock import MagicMock
from mock import patch
from pytest import fixture
from pytest import yield_fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..driver import AuthDriver
from ..driver import AuthDriverHolder


class DriverFixture(object):

    @fixture
    def engine(self):
        engine = create_engine('sqlite://')
        metadata = self._testable_cls.model.metadata
        metadata.bind = engine
        metadata.create_all()
        return engine

    @fixture
    def database(self, engine):
        db = sessionmaker(bind=engine)()
        return lambda: db

    @fixture
    def testable(self, engine, database):
        driver = self._testable_cls()
        driver.feed_database(database)
        return driver


class TestAuthDriver(DriverFixture):
    _testable_cls = AuthDriver

    def test_get_by_email(self, testable, database):
        obj = testable.create(
            name='Marek',
            email='mytest@email.com',
        )
        database().commit()

        assert testable.get_by_email('mytest@email.com').id == obj.id

    def test_password_setting(self, testable):
        obj = testable.create(
            name='Marek',
            email='mytest@email.com',
            password='mysuperx',
        )

        assert obj.validate_password('mysuperx')
        assert not obj.validate_password('error')

    def test_permission_setting(self, testable):
        obj = testable.create(
            name='Marek',
            email='mytest@email.com',
            permissions=[
                ('group', 'name'),
            ]
        )

        assert obj.has_permission('group', 'name')
        assert not obj.has_permission('bad', 'group')

    def test_removing_permission(self, testable):
        obj = testable.create(
            name='Marek',
            email='mytest@email.com',
            permissions=[
                ('group', 'name'),
                ('group', 'name2'),
                ('group', 'name3'),
            ]
        )

        testable.remove_permission(obj, 'group', 'name2')

        assert obj.has_permission('group', 'name')
        assert not obj.has_permission('group', 'name2')
        assert obj.has_permission('group', 'name3')

        # sanity check, this should not raise an error
        testable.remove_permission(obj, 'group', 'name2')


class TestAuthDriverHolder(object):
    _testable_cls = AuthDriverHolder

    @fixture
    def testable(self):
        return self._testable_cls(MagicMock())

    @yield_fixture
    def mfeeded_driver(self, testable):
        with patch.object(testable, 'feeded_driver') as mock:
            yield mock

    @yield_fixture
    def mauth_driver(self):
        with patch('implugin.auth.driver.AuthDriver') as mock:
            yield mock

    def test_auth(self, testable, mfeeded_driver, mauth_driver):
        assert testable.Auth == mfeeded_driver.return_value
        mfeeded_driver.assert_called_once_with(mauth_driver.return_value)
        mauth_driver.assert_called_once_with()
