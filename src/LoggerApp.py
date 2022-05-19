import subprocess
from fanucpy import RobotApp


class LoggerApp(RobotApp):
    def __init__(self) -> None:
        pass

    def configure(self):
        pass

    def _main(self, **kwargs):
        print("Call start_logging() or stop_logging()")

    def start_logging(self):
        subprocess.Popen(["python", "LoggerHandlerApp.py"])

    def stop_logging(self):
        # send signal to stop logging
        with open("logger_status", "w") as f:
            f.write("1")
