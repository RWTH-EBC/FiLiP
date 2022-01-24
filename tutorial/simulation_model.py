"""
Simulation model to provide dynamic data throughout the tutorial
"""
from math import cos
import numpy as np


class SimulationModel:

    def __init__(self,
                 t_start: int = 0,
                 t_end: int = 24 * 60 * 60,
                 dt: int = 1,
                 temp_max: float = 10,
                 temp_min: float = -5,
                 temp_start: float = 20):
        """
        Simulation model for a thermal zone and periodic ambient temperature
        simulation.

        The ambient temperature is simulated as daily periodic cosine ranging
        between `temp_max` and `temp_min`.

        The thermal zone is roughly parametrized as follows:
        Zone volume: 10m x 10m x 5m
        Outer wall area plus roof ares: 4 x 10m x 5m + 10m x 10m
        Thermal insulation factor U: 0.4 W/(m^2 K)

        Args:
            t_start: simulation start time in seconds
            t_end: simulation end time in seconds
            dt: model integration step in seconds
            temp_max: maximal ambient temperature in °C
            temp_min: minimal ambient temperature in °C
            temp_start: initial zone temperature in °C
        """
        self.t_start = t_start
        self.t_end = t_end
        self.dt = dt
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.temp_start = temp_start
        self.UA = 120
        self.C_p = 612.5 * 1000
        self.Q_h = 1000
        self.t_sim = self.t_start
        self.t_amb = temp_min
        self.t_zone = temp_start
        self.on_off: bool = False

    # define the function that returns a virtual ambient temperature depend from the
    # the simulation time using cosinus function
    def do_step(self, t_sim: int):
        """
        Performs a simulation step of length `t_sim`

        Args:
            t_sim: simulation step in seconds

        Returns:
            t_sim: simulation step end time in °C
            t_amb: ambient temperature in °C
            t_zone: zone temperature in °C
        """
        for t in range(self.t_sim, t_sim, self.dt):
            self.t_zone = self.t_zone + \
                          self.dt * (self.UA * (self.t_amb - self.t_zone) +
                                     self.on_off * self.Q_h) / self.C_p

            self.t_amb = -(self.temp_max - self.temp_min) / 2 * \
                    cos(2 * np.pi * t /(24 * 60 * 60)) + \
                    self.temp_min + (self.temp_max - self.temp_min) / 2

        self.t_sim = t_sim

        return self.t_sim, self.t_amb, self, self.t_zone

    @property
    def heater_on(self):
        """
        Returns heater state
        """
        return self.on_off

    @heater_on.setter
    def heater_on(self, switch: bool):
        """
        Sets heater state

        Args:
            switch: heater state `True` for on and `False` for off
        """
        switch = bool(switch)
        self.on_off = switch
