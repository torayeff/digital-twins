import numpy as np
import json
import time
import pickle

# evaluation function
from MainApp import MainApp


with open("parameters.json", "r") as f:
    params = json.load(f)

# optimal parameters found by BO
parametrization = {
    "home_velocity": 46,
    "home_acceleration": 16,
    "pick_approach_velocity": 96,
    "pick_approach_acceleration": 79,
    "pick_velocity": 21,
    "pick_acceleration": 22,
    "pick_retract_velocity": 26,
    "pick_retract_acceleration": 35,
    "place_approach_velocity": 56,
    "place_approach_acceleration": 81,
    "place_velocity": 10,
    "place_acceleration": 27,
    "place_retract_velocity": 49,
    "place_retract_acceleration": 62,
}

# parameters for max values
# parametrization = {
#     "home_velocity": 100,
#     "home_acceleration": 100,
#     "pick_approach_velocity": 100,
#     "pick_approach_acceleration": 100,
#     "pick_velocity": 40,
#     "pick_acceleration": 40,
#     "pick_retract_velocity": 40,
#     "pick_retract_acceleration": 40,
#     "place_approach_velocity": 100,
#     "place_approach_acceleration": 100,
#     "place_velocity": 40,
#     "place_acceleration": 40,
#     "place_retract_velocity": 100,
#     "place_retract_acceleration": 100,
# }

start = time.time()
ecs = []
for i in range(1, params["exp_params"]["cycles"] + 1):
    time.sleep(1)

    app = MainApp()
    status, message, result = app.run(tunable_params=parametrization)
    if status:
        print("EC: ", result)
        ecs.append(result)
    else:
        print(message)
        raise RuntimeError("Experiment error!. Check the robot or values!")
print(time.time() - start)


with open(f"data/{params['experiment_name']}/experiment.pkl", "wb") as f:
    pickle.dump(ecs, f)

print(f"Average EC: {np.mean(ecs):.4f}")