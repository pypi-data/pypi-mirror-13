from aerate import ResourceCollection, ResourceItem
from aerate.io import DataLayer

middleware = []
app_config = {}


class FakeDb(DataLayer):

    def init_driver(self):
        pass


class PetCollection(ResourceCollection):

    def on_get(self, req, resp):
        return 'on_get for {0}'.format(self.__class__.__name__)

    def on_post(self, req, resp):
        return 'on_post for {0}'.format(self.__class__.__name__)


class PetItem(ResourceItem):

    def on_get(self, req, resp, id):
        return 'on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)

    def authorize_on_get(self, req, resp, **kwargs):
        return True

    def on_delete(self, req, resp, id):
        return 'on_delete for {0} with id {1}'.format(
            self.__class__.__name__, id)


class Foo(ResourceItem):
    def on_get(self, req, resp, id):
        return 'on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)


class XXX(ResourceItem):
    def on_post(self, req, resp, id):
        return 'on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)


class TestAuthorize(ResourceItem):

    def on_post(self, req, resp, id):
        return 'on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)

    def authorize_on_post(self):
        return 'after_on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)
