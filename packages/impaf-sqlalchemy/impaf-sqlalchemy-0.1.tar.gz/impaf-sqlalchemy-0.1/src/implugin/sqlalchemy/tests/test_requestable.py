from mock import MagicMock
from mock import patch

from pytest import fixture
from pytest import yield_fixture

from impaf.testing import RequestFixture

from ..requestable import DatabaseConnection


class TestDatabaseConnection(RequestFixture):

    @fixture
    def obj(self, settings, registry):
        settings['db'] = {}
        connection = DatabaseConnection(settings, registry)
        return connection

    @yield_fixture
    def msessionmaker(self):
        patcher = patch('implugin.sqlalchemy.requestable.sessionmaker')
        with patcher as mock:
            yield mock

    def test_postgresql(self, obj, settings, registry):
        settings['db']['type'] = 'postgresql'
        registry['db'] = MagicMock()

        assert obj.database() == registry['db']
        registry['db'].expire_all.assert_called_once_with()

    def test_sqlite(self, obj, settings, registry, msessionmaker):
        settings['db']['type'] = 'sqlite'
        engine = MagicMock()
        registry['db_engine'] = engine

        assert obj.database() == msessionmaker.return_value.return_value
        msessionmaker.assert_called_once_with(bind=engine)
