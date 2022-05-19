from datetime import datetime
import json
from ntpath import join
import pipes
import sqlite3
from fanucpy import Robot
from fanucpy import RobotApp
import time


class LoggerHandlerApp(RobotApp):
    def __init__(self) -> None:
        super().__init__()
        self.configure()

    def configure(self):
        with open("parameters.json", "r") as f:
            self.params = json.load(f)

        self.erase_prev = self.params["robot_logger_params"]["erase_prev"]

        self.robot_logger = Robot(
            robot_model=self.params["robot_logger_params"]["robot_model"],
            host=self.params["robot_logger_params"]["robot_host"],
            port=self.params["robot_logger_params"]["robot_port"],
            socket_timeout=86400,
        )

        self.sampling_rate = self.params["robot_logger_params"]["sampling_rate"]

        # create database
        self.con = sqlite3.connect(f"energy.db")
        self.cur = self.con.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS energy_consumption ( 
            id                   integer NOT NULL  PRIMARY KEY  ,
            time_point           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP   ,
            ins_pwr              float NOT NULL ,
            J1                   float NOT NULL ,
            J2                   float NOT NULL ,
            J3                   float NOT NULL ,
            J4                   float NOT NULL ,
            J5                   float NOT NULL ,
            J6                   float NOT NULL   
        );"""
        )

        if self.erase_prev:
            self.cur.execute("DELETE FROM energy_consumption;")
            self.con.commit()

    def _main(self):
        self.robot_logger.connect()

        # this runs until logger_status file is written
        t = pipes.Template()
        t.open("logger_status", "w")
        pipefile = t.open("logger_status", "r")
        while not pipefile.read():
            ins_pwr = self.robot_logger.get_ins_power()
            joints = self.robot_logger.get_curjpos()
            j1, j2, j3, j4, j5, j6 = joints
            time_point = datetime.now()
            self.cur.execute(
                "INSERT INTO energy_consumption (time_point, ins_pwr, J1, J2, J3, J4, J5, J6) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                (time_point, ins_pwr, j1, j2, j3, j4, j5, j6),
            )
            self.con.commit()
            time.sleep(self.sampling_rate / 1000)

        # close
        self.robot_logger.disconnect()
        self.cur.close()
        self.con.close()


if __name__ == "__main__":
    app = LoggerHandlerApp()
    status, message, _ = app.run()
    print("LoggerHandlerApp: ", status, message)
