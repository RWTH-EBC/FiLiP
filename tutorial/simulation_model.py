"""
Simulation model to provide dynamic data throughout the tutorial
"""
from math import cos
import numpy as np


class SimulationModel:

    def __init__(self,
                 t_start: int,
                 t_end: int,
                 dt: int,
                 temp_max: float,
                 temp_min: float,
                 temp_start: float):
        self.t_start = t_start
        self.t_end = t_end
        self.dt = dt
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.temp_start = temp_start
        self.kA = 120
        self.C_p = 612.5 * 1000
        self.Q_h = 1000
        self.t_sim = self.t_start
        self.t_amb = temp_min
        self.t_zone = temp_start
        self.on_off: bool = False

    # define the function that returns a virtual ambient temperature depend from the
    # the simulation time using cosinus function
    def do_step(self, t_sim: int):
        for t in range(self.t_sim, t_sim, self.dt):
            self.t_zone = self.t_zone + \
                          self.dt * (self.kA * (self.t_amb - self.t_zone) +
                                     self.on_off * self.Q_h) / self.C_p

            self.t_amb = -(self.temp_max - self.temp_min) / 2 * \
                    cos(2 * np.pi * t /(24 * 60 * 60)) + \
                    self.temp_min + (self.temp_max - self.temp_min) / 2

        self.t_sim = t_sim

        return self.t_sim, self.t_amb, self, self.t_zone

    @property
    def heater_on(self):
        return self.on_off

    @heater_on.setter
    def heater_on(self, switch: bool):
        switch = bool(switch)
        self.on_off = switch
