from mock import MagicMock
from mock import patch
from mock import sentinel

from pytest import fixture
from pytest import yield_fixture
from sqlalchemy.orm.exc import NoResultFound

from ..driver import DriverHolder
from ..driver import ModelDriver
from ..testing import DriverFixture


class ExampleModelDriver(ModelDriver):
    model = sentinel.model


class TestModelDriver(DriverFixture):

    @yield_fixture
    def mfind_by(self, driver):
        patcher = patch.object(driver, 'find_by')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mcreate(self, driver):
        patcher = patch.object(driver, 'create')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mget_by_id(self, driver):
        patcher = patch.object(driver, 'get_by_id')
        with patcher as mock:
            yield mock

    def _cls_driver(self):
        return ExampleModelDriver

    def test_find_all(self, driver, query):
        result = driver.find_all()

        assert query.return_value == result
        query.assert_called_once_with(sentinel.model)

    def test_get_by_id(self, driver, query):
        result = driver.get_by_id('myid')

        expected_result = (
            query.return_value
            .filter_by.return_value
            .one.return_value
        )
        assert result == expected_result

        query.assert_called_once_with(sentinel.model)
        query.return_value.filter_by.assert_called_once_with(id='myid')
        query.return_value.filter_by.return_value.one.assert_called_once_with()

    def test_find_by(self, driver, query):
        result = driver.find_by(something='something')

        expected_result = (
            query.return_value
            .filter_by.return_value
        )
        assert result == expected_result

        query.assert_called_once_with(sentinel.model)
        query.return_value.filter_by.assert_called_once_with(
            something='something',
        )

    def test_upsert_on_existing(self, driver, mfind_by, mcreate):
        result = driver.upsert(kw='something')

        assert result == mfind_by.return_value.one.return_value
        mfind_by.assert_called_once_with(kw='something')
        mfind_by.return_value.one.assert_called_once_with()
        assert mcreate.called is False

    def test_upsert_on_not_existing(self, driver, mfind_by, mcreate):
        mfind_by.side_effect = NoResultFound
        result = driver.upsert(kw='something')

        assert result == mcreate.return_value
        mfind_by.assert_called_once_with(kw='something')
        mcreate.assert_called_once_with(kw='something')
        assert mfind_by.return_value.one.called is False

    def test_create(self, driver, mdatabase):
        driver.model = MagicMock()
        obj = driver.model.return_value

        driver.create(kw='name?')

        driver.model.assert_called_once_with()
        assert obj.kw == 'name?'
        mdatabase.assert_called_once_with()
        mdatabase.return_value.add.assert_called_once_with(obj)

    def test_delete_by_id(self, driver, mget_by_id, mdatabase):
        driver.delete_by_id('myid')

        mget_by_id.assert_called_once_with('myid')
        mdatabase.assert_called_once_with()
        mdatabase.return_value.delete.assert_called_once_with(
            mget_by_id.return_value,
        )

    def test_append_metadata(self, driver):
        driver.model = MagicMock()
        metadatas = set()

        driver._append_metadata(metadatas)

        assert metadatas == set([driver.model.metadata])


class TestDriverHolder(DriverFixture):

    @fixture
    def testable(self, mdatabase):
        return DriverHolder(mdatabase)

    def test_feeded_driver_simple(self, testable, mdatabase):
        obj = MagicMock()
        assert testable.feeded_driver(obj) == obj
        obj.feed_database.assert_called_once_with(mdatabase)
        assert obj in testable._drivers

    def test_feeded_driver_second(self, testable, mdatabase):
        obj = MagicMock()
        assert testable.feeded_driver(obj) == obj
        assert testable.feeded_driver(obj) == obj
        obj.feed_database.assert_called_once_with(mdatabase)
        assert obj in testable._drivers
