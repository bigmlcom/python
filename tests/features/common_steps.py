from lettuce import *

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import HTTP_BAD_REQUEST
from bigml.api import HTTP_UNAUTHORIZED
from bigml.api import HTTP_NOT_FOUND

@step(r'I get an OK response')
def i_get_an_OK_response(step):
    assert world.status == HTTP_OK

@step(r'I get a created response')
def i_get_a_created_response(step):
    assert world.status == HTTP_CREATED

@step(r'I get an accepted response')
def i_get_an_accepted_response(step):
    assert world.status == HTTP_ACCEPTED

@step(r'I get a bad request response')
def i_get_a_bad_request_response(step):
    assert world.status == HTTP_BAD_REQUEST

@step(r'I get a unauthorized response')
def i_get_a_unauthorized_response(step):
    assert world.status == HTTP_UNAUTHORIZED

@step(r'I get a not found response')
def i_get_a_not_found_response(step):
    assert world.status == HTTP_NOT_FOUND
