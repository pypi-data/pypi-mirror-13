from pytest import fixture
from pytest import yield_fixture

from mock import patch
from mock import sentinel

from impaf.application import Application

from ..application import SqlAlchemyApplication


class MockedSqlAlchemyApplication(Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = {}
        self.settings = {}

    def _populte_default_settings(self):
        self.flags['_populte_default_settings'] = True

    def _generate_registry(self, registry):
        self.flags['_generate_registry'] = True


class ExampleSqlAlchemyApplication(
    SqlAlchemyApplication,
    MockedSqlAlchemyApplication,
):
    pass


class TestSqlalchemyApplication(object):

    @fixture
    def application(self):
        return ExampleSqlAlchemyApplication('module')

    @yield_fixture
    def mcreate_engine(self):
        patcher = patch('implugin.sqlalchemy.application.create_engine')
        with patcher as mock:
            yield mock

    @yield_fixture
    def msessionmaker(self):
        patcher = patch('implugin.sqlalchemy.application.sessionmaker')
        with patcher as mock:
            yield mock

    def test_populte_default_settings(self, application):
        application._populte_default_settings()

        dbsettings = application.settings['db']
        dbsettings['login'] = 'login'
        dbsettings['password'] = 'password'
        dbsettings['host'] = 'host'
        dbsettings['port'] = 'port'
        dbsettings['name'] = 'name'

        dbsettings['type'] = 'mysql'
        assert dbsettings['url'] == 'mysql://login:password@host:port/name'

        dbsettings['type'] = 'sqlite'
        dbsettings['paths:sqlite_db'] = 'path'
        assert dbsettings['url'] == 'sqlite:///path'

    def test_generate_registry(
        self,
        application,
        mcreate_engine,
        msessionmaker,
    ):
        registry = {}
        application.settings['db:url'] = sentinel.dburl

        application._generate_registry(registry)

        engine = mcreate_engine.return_value
        session = msessionmaker.return_value

        assert registry['db_engine'] is engine
        assert registry['db'] is session.return_value

        mcreate_engine.assert_called_once_with(sentinel.dburl)
        msessionmaker.assert_called_once_with(bind=engine)
        session.assert_called_once_with()
