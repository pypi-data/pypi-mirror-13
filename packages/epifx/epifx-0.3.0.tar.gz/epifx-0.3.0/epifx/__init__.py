"""Epidemic forecasts from Google Flu Trends data."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import datetime
import logging
import numpy as np
import pypfilt

import epifx.model
import epifx.obs
import epifx.summary

__package_name__ = u'epifx'
__author__ = u'Rob Moss'
__email__ = u'rgmoss@unimelb.edu.au'
__copyright__ = u'2014-2015, Rob Moss'
__license__ = u'BSD 3-Clause License'
__version__ = u'0.3.0'


SEIR = epifx.model.SEIR

# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def default_params(p_exp, px_scale, model=SEIR):
    """The default simulation parameters.

    :param p_exp: The daily probability of seeding an exposure event in a
        naive population.
    :param px_scale: The ratio of particles to seeded exposures.
    :param model: The infection model.
    """
    # Calculate the required number of particles.
    px_count = int(np.ceil(px_scale / p_exp))
    # Enforce a minimal history matrix.
    params = pypfilt.default_params(model, max_days=7, px_count=px_count)
    # The observation model.
    params['log_llhd_fn'] = epifx.obs.log_llhd

    # Model-specific parameters.
    params['epifx'] = {
        # The daily probability of seeding an exposure event.
        'p_exp': p_exp,
        # The ratio of particles to the seeding probability.
        'px_scale': px_scale,
        # The metropolitan Melbourne population.
        'popn_size': 4108541,
        # Allow stochastic variation in model parameters and state variables.
        'stoch': True,
        # Use the default pypfilt PRNG seed, whatever that might be.
        'prng_seed': params['resample']['prng_seed'],
        # Use an independent PRNG instance by default.
        'independent_prng': True,
        # Model parameter invariants:
        # * Infection rate alpha in [1/3, 2] (based on R0 and gamma priors);
        # * Latent period of 0.5 to 3 days (1/beta);
        # * Infectious period of 1 to 3 days (1/gamma);
        # * Homogenous or selective mixing, exponent eta in [1.0, 2.0]; and
        # * Temporal forcing coefficient sigma in [-0.2, 0.2].
        'param_min': np.array([1.0 / 3, 1.0 / 3, 1.0 / 3, 1.0, -0.2]),
        'param_max': np.array([2.0, 1 / 0.5, 1.0 / 1, 2.0, 0.2]),
    }

    # Construct the default PRNG object.
    params['epifx']['rnd'] = np.random.RandomState(
        params['epifx']['prng_seed'])

    # Observation model parameters.
    params['obs'] = {}

    return params


def init_prng(params, seed):
    """Initialise the ``epifx`` PRNG instance (``params['epifx']['rnd']``).

    :param params: The simulation parameters.
    :param seed: The PRNG seed; see the ``numpy.random.RandomState``
        documentation for details.
    """
    params['epifx']['prng_seed'] = seed
    params['epifx']['rnd'] = np.random.RandomState(seed)


def daily_forcing(filename, date_fmt='%Y-%m-%d'):
    """Return a temporal forcing look-up function, which should be stored in
    ``params['epifx']['forcing']`` in order to enable temporal forcing.

    :param filename: A file that contains two columns separated by whitespace,
        the column first being the date and the second being the force of the
        temporal modulation.
        Note that the first line of this file is assumed to contain column
        headings and will be **ignored**.
    :param date_fmt: The format in which dates are stored.
    """

    def _date_col(text, fmt='%Y-%m-%d'):
        """Convert date strings to datetime.date instances."""
        return datetime.datetime.strptime(text.decode('utf-8'), fmt).date()

    # See https://github.com/numpy/numpy/issues/2407 for an explanation of the
    # reason why the `str(...)` calls are necessary with unicode literals.
    col_types = [(str('Date'), '|O4'), (str('Force'), np.float)]
    df = np.genfromtxt(filename, skip_header=1, dtype=col_types,
                       converters={0: _date_col})

    def forcing(when):
        """Return the (daily) temporal forcing factor."""
        today = when.date()
        if when.hour == when.minute == 0:
            # The time-step covered the final portion of the previous day.
            today = today - datetime.timedelta(days=1)
        return df['Force'][df['Date'] == today][0]

    return forcing
