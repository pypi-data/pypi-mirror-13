from .driver import DriverHolder


class DataGenerator(object):

    def __init__(self):
        self.data = {}

    def _get_driver_cls(self):
        return DriverHolder

    def feed_database(self, database):
        self.database = database
        self.drivers = self._get_driver_cls()(self.database)

    def create_all(self):
        self.make_all()
        self.database().commit()
        return self.data

    def _create(self, cls, **kwargs):
        driver = self._get_driver(cls)
        obj = driver.upsert(**kwargs)
        self._add_object_to_data(obj, kwargs['name'])
        return obj

    def _create_nameless(self, cls, **kwargs):
        driver = self._get_driver(cls)
        obj = driver.upsert(**kwargs)
        self._add_nameless_object_to_data(obj)
        return obj

    def _add_nameless_object_to_data(self, obj):
        clsname = obj.__class__.__name__
        data = self.data.get(clsname, [])
        data.append(obj)
        self.data[clsname] = data

    def _add_object_to_data(self, obj, name):
        clsname = obj.__class__.__name__
        data = self.data.get(clsname, {})
        data[name] = obj
        self.data[clsname] = data

    def _get_driver(self, cls):
        name = cls if isinstance(cls, str) else cls.__name__
        return getattr(self.drivers, name)
