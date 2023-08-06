"""Base class for simulation models."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import numpy as np


class Base(object):
    """
    The base class for simulation models, which defines the minimal set of
    methods that are required.
    """

    @staticmethod
    def init(params, vec):
        """
        Initialise a state vector.

        :param params: Simulation parameters.
        :param vec: An uninitialised state vector of correct dimensions (see
            :py:func:`~state_size`).
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @staticmethod
    def state_size():
        """
        Return the size of the state vector.

        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @staticmethod
    def priors(params):
        """
        Return a dictionary of model parameter priors. Each key must
        identify a parameter by name. Each value must be a function that
        returns samples from the associated prior distribution, and should
        have the following form:

        .. code-block:: python

           lambda r, size=None: r.uniform(1.0, 2.0, size=size)

        Here, the argument ``r`` is a PRNG instance and ``size`` specifies the
        output shape (by default, a single value).

        :param params: Simulation parameters.
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @classmethod
    def update(cls, params, step_date, dt, is_fs, prev, curr):
        """
        Perform a single time-step.

        :param params: Simulation parameters.
        :param step_date: The date and time of the current time-step.
        :param dt: The time-step size (days).
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @classmethod
    def state_info(cls):
        """
        Describe each state variable as a ``(name, index)`` tuple, where
        ``name`` is a descriptive name for the variable and ``index`` is the
        index of that variable in the state vector.

        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @classmethod
    def param_info(cls):
        """
        Describe each model parameter as a ``(name, index)`` tuple, where
        ``name`` is a descriptive name for the parameter and ``index`` is the
        index of that parameter in the state vector.

        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @classmethod
    def stat_info(cls):
        """
        Describe each statistic that can be calculated by this model as a
        ``(name, stat_fn)`` tuple, where ``name`` is a string that identifies
        the statistic and ``stat_fn`` is a function that calculates the value
        of the statistic.

        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    @staticmethod
    def is_valid(hist):
        """
        Identify particles whose state and parameters can be inspected. By
        default, this function returns ``True`` for all particles. Override
        this function to ensure that inchoate particles are correctly
        ignored.
        """
        return np.ones((hist.shape[-2],), dtype=bool)
