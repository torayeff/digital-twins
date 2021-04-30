"""RDK Simulation abstract class"""
from abc import ABC, abstractmethod
import robolink


class RDKSimulation(ABC):
    """RoboDK simulation class."""
    def __init__(self):
        self.rblink = robolink.Robolink()
        self.simulation_speed = 1
        self.refresh_rate = 0.005

    @abstractmethod
    def run(self):
        """Runs simulation."""
        raise NotImplementedError(f'You have to implement this method!')

    @abstractmethod
    def reset(self):
        """Resets simulation."""
        raise NotImplementedError('You have to implement this method!')