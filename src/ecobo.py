import numpy as np
import json
import time
import pickle

# ax optimizer
from ax.service.managed_loop import optimize

# evaluation function
from MainApp import MainApp


def evaluation_function(parametrization):
    time.sleep(1)

    app = MainApp()
    status, message, result = app.run(tunable_params=parametrization)
    if status:
        print("EC: ", result)
        return {"ec": (result, 0.0)}
    else:
        print(message)
        raise RuntimeError("Experiment error!. Check the robot or values!")

with open("parameters.json", "r") as f:
    params = json.load(f)


start = time.time()
best_parameters, values, experiment, model = optimize(
    parameters=params["exp_params"]["tunable_params"],
    experiment_name="bayesian_eco",
    evaluation_function=evaluation_function,
    objective_name="ec",
    minimize=True,
    total_trials=params["exp_params"]["cycles"],
)
print(time.time() - start)


exp_out = best_parameters, values, experiment
with open(f"data/{params['experiment_name']}/experiment.pkl", "wb") as f:
    pickle.dump(exp_out, f)

print(values)
print(best_parameters)