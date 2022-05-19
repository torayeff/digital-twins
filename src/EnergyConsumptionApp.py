import sqlite3
import numpy as np
import pandas as pd
import json
import os
from fanucpy import RobotApp


class EnergyConsumptionApp(RobotApp):
    def __init__(self) -> None:
        super().__init__()
        self.configure()
    
    def calc_kWh(self, measurements, dstep):
        """
        Args:
            measurements: power measurements in kWh
            dstep: delta time step in seconds

        Returns:
            Power in kWh
        """
        # assuming that step in milliseconds
        p = np.sum(measurements)
        p = p * dstep / 3600
        return p


    def get_ec(self, df, sampling_rate):
        """Gets energy consumption.

        Args:
            df (pandas.DataFrame): Energy consumption dataframe.
            sampling_rate (int): The sampling rate in milliseconds.

        Returns:
            float: Energy consumption in kWh.
        """
        df = df.set_index("time_point")
        df = df.resample(f"{sampling_rate}ms").mean().ffill()

        ec = self.calc_kWh(df["ins_pwr"], dstep=sampling_rate / 1000)
        return ec
    
    def configure(self):
        with open("parameters.json", "r") as f:
            self.params = json.load(f)
            self.sampling_rate = 50
    
    def _main(self, dir=""):
        db_file = os.path.join(dir, "energy.db")
        con = sqlite3.connect(db_file)
        df = pd.read_sql_query("SELECT time_point, ins_pwr FROM energy_consumption;", con, parse_dates=["time_point"])
        ec = self.get_ec(df, self.sampling_rate)

        return ec