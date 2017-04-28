import time
import json
import os
import StringIO
from datetime import datetime, timedelta
from world import world
from nose.tools import eq_, assert_less

from bigml.api import BigML
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.association import Association

from read_association_steps import i_get_the_association


#@step(r'the association name is "(.*)"')
def i_check_association_name(step, name):
    association_name = world.association['name']
    eq_(name, association_name)

#@step(r'I create an association from a dataset$')
def i_create_an_association_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_association(dataset, {'name': 'new association'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.association = resource['object']
    world.associations.append(resource['resource'])


#@step(r'I create an association with search strategy "(.*)" from a dataset$')
def i_create_an_association_with_strategy_from_dataset(step, strategy):
    dataset = world.dataset.get('resource')
    resource = world.api.create_association(
        dataset, {'name': 'new association', 'search_strategy': strategy})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.association = resource['object']
    world.associations.append(resource['resource'])


#@step(r'I update the association name to "(.*)"$')
def i_update_association_name(step, name):
    resource = world.api.update_association(world.association['resource'],
                                            {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.association = resource['object']


#@step(r'I wait until the association status code is either (\d) or (-\d) less than (\d+)')
def wait_until_association_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    association_id = world.association['resource']
    i_get_the_association(step, association_id)
    status = get_status(world.association)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
           i_get_the_association(step, association_id)
           status = get_status(world.association)
    eq_(status['code'], int(code1))


#@step(r'I wait until the association is ready less than (\d+)')
def the_association_is_finished_in_less_than(step, secs):
    wait_until_association_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I create a local association')
def i_create_a_local_association(step):
    world.local_association = Association(world.association)


#@step(r'I get the rules for "(.*?)"$')
def i_get_rules_for_item_list(step, item_list):
    world.association_rules = world.local_association.get_rules(
        item_list=item_list)


#@step(r'the first rule is "(.*?)"$')
def the_first_rule_is(step, rule):
    found_rules = []
    for a_rule in world.association_rules:
        found_rules.append(a_rule.to_json())
    eq_(rule, found_rules[0])
