import json
import shutil
import time
import os
from datetime import datetime
from fanucpy import Robot
from fanucpy import RobotApp
from PickAndPlaceApp import PickAndPlaceApp
from LoggerApp import LoggerApp
from EnergyConsumptionApp import EnergyConsumptionApp


class MainApp(RobotApp):
    def __init__(self):
        self.configure()

    def configure(self):
        with open("parameters.json", "r") as f:
            self.params = json.load(f)

        self.robot = Robot(
            robot_model=self.params["robot_params"]["robot_model"],
            host=self.params["robot_params"]["robot_host"],
            port=self.params["robot_params"]["robot_port"],
            ee_DO_type=self.params["robot_params"]["robot_ee_DO_type"],
            ee_DO_num=self.params["robot_params"]["robot_ee_DO_num"],
            socket_timeout=86400,
        )

    def _main(self, **kwargs):
        # experiment app
        exp_app = PickAndPlaceApp(robot=self.robot)

        # logger app
        logger_app = LoggerApp()
        logger_app.start_logging()

        # run experiment
        exp_app.run(
            static_params=self.params["exp_params"]["static_params"],
            tunable_params=kwargs["tunable_params"],
        )

        # stop logger
        logger_app.stop_logging()

        # energy consumption app
        ec_app = EnergyConsumptionApp()
        _, _, ec = ec_app.run()

        # prepare directories
        exp_dir = f"data/{self.params['experiment_name']}"
        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)
        
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        save_dir = os.path.join(exp_dir, ts)
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        # save data
        time.sleep(1)
        shutil.move("energy.db", os.path.join(save_dir, "energy.db"))

        with open(os.path.join(save_dir, "static_params.json"), "w") as f:
            json.dump(self.params["exp_params"]["static_params"], f)

        with open(os.path.join(save_dir, "tunable_params.json"), "w") as f:
            json.dump(kwargs["tunable_params"], f)

        return ec

