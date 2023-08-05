from aerate import ResourceCollection, ResourceItem
from aerate.auth import Auth
middleware = []
app_config = {}


class PetCollection(ResourceCollection):

    def on_get(self, req, resp):
        return 'on_get for {0}'.format(self.__class__.__name__)

    def on_post(self, req, resp):
        return 'on_post for {0}'.format(self.__class__.__name__)


class PetItem(ResourceItem):

    def on_get(self, req, resp, id):
        return 'on_get for {0} with id {1}'.format(
            self.__class__.__name__, id)

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
