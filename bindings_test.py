from bigml.api import BigML
from bigml.ensemble import Ensemble

print("Creating source...")
api = BigML(storage='./storage')
resource = api.create_source('./data/iris.csv')

print("Creating dataset...")
dataset = api.create_dataset(resource)
api.ok(dataset)

print("Creating ensemble...")
ensemble = api.create_ensemble(dataset, {"objective_weights":
                                         [["Iris-versicolor", 1],
                                          ["Iris-virginica", 2],
                                          ["Iris-setosa", 4]],
                                         "ensemble_sample": {'seed': 'test'}})
api.ok(ensemble)

print("Ensemble ID: %s" % ensemble['resource'])
print("Downloading ensemble..." % ensemble)
local_ensemble = Ensemble(ensemble)

print("Creating predictions...")
flower = {"petal width": 0.5, "sepal width": 1.0}
remote = api.create_prediction(ensemble, flower)['object']['probabilities']
remote = {p[0]: p[1] for p in remote}
local = local_ensemble.predict_probability(flower)
local = {p['prediction']: p['probability'] for p in local}

classes = local.keys()

for rp, lp in zip([remote[c] for c in classes], [local[c] for c in classes]):
    assert abs(rp - lp) < 1e-5, str((rp, lp))
