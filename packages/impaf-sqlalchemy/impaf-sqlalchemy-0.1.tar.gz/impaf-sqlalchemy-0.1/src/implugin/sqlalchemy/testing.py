from mock import MagicMock

from pytest import fixture

from impaf.testing import ControllerFixture
from impaf.testing import RequestCase
from impaf.testing import RequestFixture
from impaf.testing import cache

from .requestable import DatabaseConnection


class SqlalchemyRequestFixture(RequestFixture):

    @fixture
    def mdatabase(self, mrequest):
        mrequest.database = MagicMock()
        return mrequest.database

    @fixture
    def mdrivers(self, testable):
        testable.drivers = MagicMock()
        return testable.drivers


class SqlalchemyControllerFixture(
    SqlalchemyRequestFixture,
    ControllerFixture,
):
    pass


class DriverFixture(object):

    @fixture
    def mdatabase(self):
        return MagicMock()

    @fixture
    def query(self, mdatabase):
        return mdatabase().query

    @fixture
    def driver(self, mdatabase):
        driver = self._cls_driver()()
        driver.feed_database(mdatabase)
        return driver


class SqlalchemyCase(RequestCase):

    @cache
    def mdatabase(self):
        self.mrequest()._database = MagicMock()
        return self.mrequest()._database

    @cache
    def mdrivers(self):
        return self.pobject(self.object(), 'drivers')


class DriverCase(object):

    @cache
    def application(self):
        app = self._application_cls()
        app.run_tests()
        return app

    @cache
    def database(self):
        connection = DatabaseConnection(self.settings(), self.registry())
        return connection.database()

    @cache
    def registry(self):
        return self.application().config.registry

    @cache
    def settings(self):
        return self.application().settings

    @cache
    def object(self):
        driver = self._object_cls()
        driver.feed_database(self.database)
        return driver

    def flush_table_from_object(self, *args):
        engine = self.registry()['db_engine']
        for obj in args:
            obj.metadata.create_all(engine)
            self.database().query(obj).delete()
