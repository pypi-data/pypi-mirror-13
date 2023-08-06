from aerate.tests.test_fixtures import PetCollection
from aerate.auth import BasicAuth
from aerate import Aerate
from aerate.validate import validate_object

app = Aerate(
    spec_file='./aerate/tests/petstore_simple.json',
    auth=[BasicAuth()]
)
res = PetCollection()
app.add_resource(res)

obj = {'name': 'fido', 'id': 23, 'tag': 'this tag'}
validate_object(res.schema, obj)
