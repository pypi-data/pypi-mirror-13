from aerate import ResourceCollection, ResourceItem

middleware = []
app_config = {}


class PetCollection(ResourceCollection):

    def on_get(self):
        return 'on_get for {0}'.format(self.__class__.__name__)

    def on_post(self):
        return 'on_post for {0}'.format(self.__class__.__name__)


class PetItem(ResourceItem):

    def on_get(self):
        return 'on_get for {0}'.format(self.__class__.__name__)

    def on_delete(self):
        return 'on_delete for {0}'.format(self.__class__.__name__)
