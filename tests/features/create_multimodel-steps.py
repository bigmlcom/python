from lettuce import step, world

@step(r'I store the dataset id in a list')
def i_store_dataset_id(step):
    world.dataset_ids.append(world.dataset['resource'])

@step(r'I check the model stems from the original dataset list')
def i_check_model_datasets_and_datasets_ids(step):
    model = world.model
    if 'datasets' in model and model['datasets'] == world.dataset_ids:
        assert True
    else:
        assert False, ("The model contains only %s "
                       "and the dataset ids are %s" %
                       (",".join(model['datasets']),
                        ",".join(world.dataset_ids)))                  
