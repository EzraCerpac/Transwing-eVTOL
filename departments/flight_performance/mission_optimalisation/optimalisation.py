from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import aerosandbox as asb
import aerosandbox.numpy as np
import pandas as pd
from aerosandbox.dynamics.point_mass.common_point_mass import _DynamicsPointMassBaseClass
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import AC
from sizing_tools.model import Model
from utility.log import logger
from utility.plotting import show


class OptParam(Enum):
    MIN_TIME = 'minimum time'
    MIN_DISTANCE = 'minimum distance'
    MAX_TIME = 'maximum time'
    MAX_DISTANCE = 'maximum distance'
    ENERGY = 'energy'
    MAX_POWER = 'maximum power'
    TRADE_OFF = 'time * energy'


class Optimalisation(Model, ABC):

    def __init__(self,
                 aircraft: AC,
                 opt_param: OptParam,
                 n_timesteps=100,
                 max_iter=1000,
                 n_logs=50):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        self.parametric_fn = aircraft.parametric_fn

        self.opti = asb.Opti()
        self.opt_param = opt_param
        self.n_timesteps = n_timesteps
        self.max_iter = max_iter
        self.n_logs = n_logs

        self.end_time: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.time: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.dyn: Optional[_DynamicsPointMassBaseClass] = None
        self.elevator_deflection: Optional[float | np.ndarray
                                           | asb.Opti.variable] = None
        self.CL: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.thrust_level: Optional[float | np.ndarray
                                    | asb.Opti.variable] = None
        self.thrust: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.max_power: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.power: Optional[float | np.ndarray | asb.Opti.variable] = None
        self.total_energy: Optional[float | np.ndarray
                                    | asb.Opti.variable] = None

        self.init()

        self.params: dict[str, float | np.ndarray] = {
            k: v
            for k, v in {
                # 'end time': self.end_time,
                'time':
                self.time,
                'x':
                self.dyn.x_e,
                # 'z': self.dyn.z_e,
                'altitude':
                self.dyn.altitude,
                'u':
                self.dyn.u_b if hasattr(self.dyn, 'u_b') else self.dyn.u_e,
                'w':
                self.dyn.w_b if hasattr(self.dyn, 'w_b') else self.dyn.w_e,
                'gamma':
                self.dyn.theta -
                self.dyn.alpha if hasattr(self.dyn, 'theta') else None,
                'alpha':
                self.dyn.alpha,
                'theta':
                self.dyn.theta if hasattr(self.dyn, 'theta') else None,
                'q':
                self.dyn.q if hasattr(self.dyn, 'q') else None,
                'speed':
                self.dyn.speed,
                'elevator deflection':
                self.elevator_deflection,
                'CL':
                self.CL,
                # 'thrust level': self.thrust_level,
                'thrust':
                self.thrust,
                'max power':
                self.max_power,
                'power':
                self.power,
                'total energy':
                self.total_energy,
            }.items() if v is not None
        }

        self.logs: list[dict[str, list[float]]] = []

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def log_values(self, iteration: int):
        if iteration % (self.max_iter / self.n_logs) == 0:
            logger.info(f"Logging iteration {iteration}")
            self.logs.append({
                k: self.opti.debug.value(v)
                for k, v in self.params.items()
            })

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def constraints(self):
        pass

    @abstractmethod
    def dynamics(self):
        pass

    def run(self, verbose: bool = True):
        opt_param = {
            OptParam.MIN_TIME: self.time[-1],
            OptParam.MIN_DISTANCE: self.dyn.x_e[-1],
            OptParam.MAX_TIME: -self.time[-1],
            OptParam.MAX_DISTANCE: -self.dyn.x_e[-1],
            OptParam.ENERGY: self.total_energy,
            OptParam.MAX_POWER: self.max_power,
            OptParam.TRADE_OFF: self.time[-1] * self.total_energy,
        }[self.opt_param]
        # Optimize
        self.opti.minimize(opt_param)

        # Post-process
        sol = self.opti.solve(
            verbose=verbose,
            max_iter=self.max_iter,
            callback=self.log_values,
            behavior_on_failure='return_last',
        )
        self.params = {k: sol(v) for k, v in self.params.items()}
        self.time = sol(self.time)
        self.dyn = sol(self.dyn)
        if verbose:
            self.print_results()

    def print_results(self):
        logger.info(f"\nOptimized for {self.opt_param.value}:")
        logger.info(
            f"Total energy: {self.params['total energy'] / 3600000:.1f} kWh")
        logger.info(f"Total time: {self.params['time'][-1]:.1f} s")
        logger.info(f"Total distance: {self.params['x'][-1] / 1000:.1f} km")
        logger.info(f"Max power: {self.params['max power'] / 1000:.1f} kW")

    def to_dataframe(self, i_log: int = None) -> pd.DataFrame:
        if i_log is None:
            param_dict = self.params
        else:
            assert i_log < len(
                self.logs
            ), f"Only {len(self.logs)} iterations have been logged"
            param_dict = self.logs[i_log]
        return pd.DataFrame.from_dict({
            k: v
            for k, v in param_dict.items()
            if isinstance(v, np.ndarray) and v.size > 1
        })

    def plot_over(self, x_name: str) -> tuple[plt.Figure, plt.Axes]:
        df = self.to_dataframe()
        xx = df[x_name]
        df = df.drop(columns=[x_name])
        n_plots = len(df.columns) - 1
        n_rows = 3
        n_cols = n_plots // n_rows + 1
        fig, axs = plt.subplots(n_rows, n_cols, sharex=True, figsize=(15, 10))
        axs = axs.flatten()
        for i, (col, values) in enumerate(df.items()):
            if col == x_name:
                continue
            axs[i].plot(xx, values)
            axs[i].set_xlim(xx.min(), xx.max())
            # axs[i].set_ylim(values.min(), values.max())
            axs[i].set_title(col)
            axs[i].set_xlabel(x_name)
        return fig, axs

    @show
    def plot_over_distance(self) -> tuple[plt.Figure, plt.Axes]:
        return self.plot_over('x')

    @show
    def plot_over_time(self) -> tuple[plt.Figure, plt.Axes]:
        return self.plot_over('time')

    def plot_logs_over(self, x_name: str) -> tuple[plt.Figure, plt.Axes]:
        n_logs = len(self.logs)
        fig, axs = self.plot_over(x_name)
        for i_log in range(n_logs):
            alpha = (i_log / n_logs)
            df = self.to_dataframe(i_log)
            xx = df[x_name]
            df = df.drop(columns=[x_name])
            for i, (col, values) in enumerate(df.items()):
                if col == x_name:
                    continue
                axs[i].plot(xx, values, alpha=alpha)
                axs[i].set_xlim(xx.min(), xx.max())
                # axs[i].set_ylim(values.min(), values.max())
        return fig, axs

    @show
    def plot_logs_over_distance(self) -> tuple[plt.Figure, plt.Axes]:
        return self.plot_logs_over('x')

    @show
    def plot_logs_over_time(self) -> tuple[plt.Figure, plt.Axes]:
        return self.plot_logs_over('time')
