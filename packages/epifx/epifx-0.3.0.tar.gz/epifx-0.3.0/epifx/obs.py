"""Observation models: expected values and log likelihoods."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import numpy as np


def from_model(params, when, unit, period, pr_inf):
    """Determine the expected observation for a given infection probability.

    :param params: The observation model parameters.
    :param when: The end of the observation period.
    :type when: datetime.datetime
    :param unit: The observation units (see classes in :py:module`data`).
    :type unit: str
    :param period: The duration of the observation period (in days).
    :type period: int
    :param pr_inf: The probability of an individual becoming infected during
        the observation period.
    :type pr_inf: float
    """
    return {'date': when,
            'value': expect(params, unit, period, pr_inf),
            'unit': unit,
            'period': period,
            'source': "synthetic-observation"}


def expect(params, unit, period, pr_inf):
    """Determine the expected value for a given infection probability.

    :param params: The observation model parameters.
    :param unit: The observation units (see classes in :py:module`data`).
    :type unit: str
    :param period: The duration of the observation period (in days).
    :type period: int
    :param pr_inf: The probability of an individual becoming infected during
        the observation period.
    :type pr_inf: float
    """
    if unit in params['obs']:
        op = params['obs'][unit]
        return op['expect_fn'](params, op, period, pr_inf)
    else:
        raise ValueError("Unknown observation type '{}'".format(unit))


def log_llhd(params, obs, curr, hist):
    """Calculate the log-likelihood of obtaining one or more observations from
    each particle.

    :param params: The observation model parameters.
    :param obs: The list of observations for the current time-step.
    :param curr: The particle state vectors.
    :type curr: numpy.ndarray
    :param hist: The particle state histories, indexed by observation period.
    :type hist: dict(int, list(float))
    """
    log_llhd = np.zeros(curr.shape[:-1])
    pr_inf = params['model'].pr_inf

    for o in obs:
        # Extract the observation period and the infection probability.
        days = o['period']
        unit = o['unit']
        p_inf = np.maximum(pr_inf(hist[days], curr), 0)
        cpt_indiv = np.array([1 - p_inf, p_inf])

        if unit in params['obs']:
            op = params['obs'][unit]
            log_llhd += op['log_llhd_fn'](params, op, o, cpt_indiv, curr, hist)
        else:
            raise ValueError("Unknown observation type '{}'".format(unit))

    return log_llhd
