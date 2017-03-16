import logging
import json
import inspect
import os
from jsonschema import validate, ValidationError
from orchestrator_core.exception import UserValidationError

class UserValidate(object):

    schema_name = 'user_schema.json'

    def validate(self, login):
        schema = self.get_schema()
        try:
            validate(login, schema)
        except ValidationError as err:
            logging.info(err.message)
            raise UserValidationError(err.message)

    def get_schema(self):
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
        fd = open(base_folder+'/'+self.schema_name, 'r')
        return json.loads(fd.read())



