"""Models of disease transmission in human populations."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import numpy as np
from pypfilt.model import Base


class SEIR(Base):
    r"""An SEIR compartment model for a single circulating influenza strain,
    under the assumption that recovered individuals are completely protected
    against reinfection.

    .. math::

        \frac{dS}{dt} &= - \alpha \cdot S^\eta I \\[0.5em]
        \frac{dE}{dt} &= \alpha \cdot S^\eta I - \beta \cdot E
            \\[0.5em]
        \frac{dI}{dt} &= \beta \cdot E - \gamma I \\[0.5em]
        \frac{dR}{dt} &= \gamma I

    ==============  ================================
    Parameter       Meaning
    ==============  ================================
    :math:`\alpha`  Force of infection
    :math:`\beta`   Incubation period (day :sup:`-1`)
    :math:`\gamma`  Infectious period (day :sup:`-1`)
    :math:`\eta`    Inhomogeneous social mixing
    :math:`\sigma`  Temporal forcing coefficient
    ==============  ================================

    The force of infection can be subject to temporal forcing :math:`F(t)`, as
    mediated by :math:`\sigma`:

    .. math::

        \alpha'(t) &= \alpha \cdot (1 + \sigma \cdot F(t))

    Note that this requires the forcing function :math:`F(t)` to be defined in
    the simulation parameters (see the `Temporal Forcing`_ documentation).
    """

    __info = [("S", 0), ("E", 1), ("I", 2), ("R", 3),
              ("alpha", 4), ("beta", 5), ("gamma", 6), ("eta", 7),
              ("sigma", 8)]

    @staticmethod
    def init(params, vec):
        """Initialise a state vector.

        :param params: Simulation parameters.
        :param vec: An uninitialised state vector of correct dimensions (see
            :py:func:`~state_size`).
        """
        vec[..., :] = [1, 0, 0, 0, 0, 0, 0, 0, 0]

    @staticmethod
    def state_size():
        """Return the size of the state vector."""
        return 9

    @staticmethod
    def priors(params):
        """
        Return a dictionary of model parameter priors.

        :param params: Simulation parameters.
        """
        return {
            # The basic reproduction number.
            'R0': lambda r, size=None: r.uniform(1.0, 2.0, size=size),
            # Latent period (days).
            'beta_inv': lambda r, size=None: r.uniform(0.5, 3, size=size),
            # Infectiousness period (days).
            'gamma_inv': lambda r, size=None: r.uniform(1, 3, size=size),
            # Power-law scaling of (S/N), found to be ~= 2 in large US cities.
            'eta': lambda r, size=None: r.uniform(1.0, 2.0, size=size),
            # Temporal forcing coefficient, requires a look-up function.
            'sigma': lambda r, size=None: r.uniform(-0.2, 0.2, size=size),
            # Relative scale of the noise in compartment flows.
            'noise_flow': lambda r: np.array(0.025),
            # Relative scale of the noise in model parameters.
            'noise_param': lambda r: np.array(5e-4),
        }

    @classmethod
    def update(cls, params, step_date, dt, is_fs, prev, curr):
        """Perform a single time-step.

        :param params: Simulation parameters.
        :param step_date: The date and time of the current time-step.
        :param dt: The time-step size (days).
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """
        # Use 3 masks to identify which state vectors should be (a) seeded,
        # (b) copied, and (c) stepped forward.
        #
        # This method makes extensive use of NumPy's broadcasting rules.
        # See http://docs.scipy.org/doc/numpy/user/basics.broadcasting.html
        # for details and links to tutorials/examples.
        #
        # Also note that the state vectors are assumed to be stored in a 2D
        # array (hence the use of ``axis=0`` when calculating the masks).
        # To generalise this to N dimensions, the following should be used:
        #
        #     np.all(..., axis=range(len(curr.shape) - 1)
        #
        # We ignore this for now, on the basis that we should only ever need a
        # flat array of particles at each time-step.

        if params['epifx']['independent_prng']:
            rnd = params['epifx']['rnd']
        else:
            rnd = params['rnd']

        # Determine whether temporal forcing is being used.
        forcing = 'forcing' in params['epifx']

        # Scale the seeding probability from daily to per time-step.
        p_exp = params['epifx']['p_exp'] * dt

        # The lower and upper parameter bounds.
        p_min = params['epifx']['param_min']
        p_max = params['epifx']['param_max']

        # This generates more random samples than are strictly necessary, but
        # since it should not affect the likelihood of seeding a new strain,
        # it's only a question of computational cost.
        rand_samples = rnd.random_sample(size=params['size'])
        seed_mask = np.all([cls.can_seed(prev), rand_samples < p_exp], axis=0)
        seed_infs = np.zeros(params['size'])
        seed_infs[seed_mask] = cls.initial_exposures(params,
                                                     shape=np.sum(seed_mask))

        # Determine which particles will be seeded with an initial infection.
        mask_init = np.all([seed_infs > 0, prev[..., 0] == 1], axis=0)
        # Determine which particles remain in their current (initial) state.
        mask_copy = np.all([prev[..., 0] == 1, np.logical_not(mask_init)],
                           axis=0)
        # Determine which particles will need to step forward in time.
        mask_step = np.logical_not(np.any([mask_init, mask_copy], axis=0))

        if np.any(mask_init):
            # Seed initial infections.
            rnd_size = curr[mask_init, 0].shape
            prior = params['prior']
            curr[mask_init, 0] = 1 - seed_infs[mask_init]
            curr[mask_init, 1] = seed_infs[mask_init]
            # Note: the I and R compartments remain at zero.
            curr[mask_init, 5] = 1.0 / prior['beta_inv'](rnd, size=rnd_size)
            curr[mask_init, 6] = 1.0 / prior['gamma_inv'](rnd, size=rnd_size)
            curr[mask_init, 7] = params['prior']['eta'](rnd, size=rnd_size)
            if forcing:
                sigma = params['prior']['sigma'](rnd, size=rnd_size)
                curr[mask_init, 8] = sigma
            else:
                curr[mask_init, 8] = 0
            # Sample R0 and calculate alpha, rather than sampling alpha.
            sampled_R0 = prior['R0'](rnd, size=rnd_size)
            curr[mask_init, 4] = sampled_R0 * curr[mask_init, 6]
            # Enforce invariants on model parameters.
            # Note: a memory leak arose when using the ``out`` parameter.
            curr[mask_init, 4:] = np.clip(curr[mask_init, 4:], p_min, p_max)

        if np.any(mask_copy):
            # Nothing happening, entire population remains susceptible.
            curr[mask_copy, :] = prev[mask_copy, :]

        if np.any(mask_step):
            # Calculate flows between compartments.
            rnd_size = curr[mask_step, 0].shape
            curr[mask_step, :] = prev[mask_step, :]

            # Determine the force of infection.
            if forcing:
                # Apply temporal forcing when it is included in the parameters.
                force = params['epifx']['forcing'](step_date)
                force *= curr[mask_step, 8]
                # Ensure the force of infection is non-negative (can be zero).
                alpha = curr[mask_step, 4] * np.maximum(1.0 + force, 0)
            else:
                # The effective force of infection is the parameter alpha.
                alpha = curr[mask_step, 4]

            s_to_e = dt * (alpha * curr[mask_step, 2] *
                           curr[mask_step, 0] ** curr[mask_step, 7])
            e_to_i = dt * (curr[mask_step, 5] * curr[mask_step, 1])
            i_to_r = dt * (curr[mask_step, 6] * curr[mask_step, 2])
            # Account for stochastic behaviour, if appropriate.
            if params['epifx']['stoch']:
                # Define the relative scales of the noise terms.
                scale = np.empty(shape=8)
                scale[:3] = params['prior']['noise_flow'](rnd)
                scale[3:] = params['prior']['noise_param'](rnd)
                n_size = rnd_size + (8,)
                noise = scale[np.newaxis, :] * dt * rnd.normal(size=n_size)
                # Scale the noise parameters in proportion to the flow rates
                # in to and out of each model compartment (i.e., S, E, I, R),
                # according to the scaling law of Gaussian fluctuations.
                # For more details see doi:10.1016/j.mbs.2012.05.010
                noise[..., 0] *= np.sqrt(s_to_e / dt)
                noise[..., 1] *= np.sqrt(e_to_i / dt)
                noise[..., 2] *= np.sqrt(i_to_r / dt)
                # Add noise to the inter-compartment flows.
                s_to_e += noise[..., 0]
                e_to_i += noise[..., 1]
                i_to_r += noise[..., 2]
                # Add noise to the model parameters.
                curr[mask_step, 4:] += noise[..., 3:]
                # Enforce invariants on model parameters.
                curr[mask_step, 4:] = np.clip(curr[mask_step, 4:],
                                              p_min, p_max)
                if not forcing:
                    # Do not allow sigma to vary if there is no forcing.
                    curr[mask_step, 8] = 0
            # Update compartment sizes.
            curr[mask_step, 0] -= s_to_e
            curr[mask_step, 1] += s_to_e - e_to_i
            curr[mask_step, 2] += e_to_i - i_to_r
            # Enforce invariants on S, E, and I compartments.
            curr[mask_step, :3] = np.clip(curr[mask_step, :3], 0, 1)
            mask_invalid = np.sum(curr[mask_step, :3], axis=-1) > 1
            if np.any(mask_invalid):
                curr_inv = curr[mask_step][mask_invalid]
                div_by = np.sum(curr_inv[..., :3], axis=-1)[:, None]
                curr_inv[..., :3] /= div_by
            # Calculate the size of the R compartment.
            curr[mask_step, 3] = 1.0 - np.sum(curr[mask_step, :3], axis=-1)

    @staticmethod
    def pr_inf(prev, curr):
        """Calculate the likelihood of an individual becoming infected, for
        any number of state vectors.

        :param prev: The model states at the start of the observation period.
        :param curr: The model states at the end of the observation period.
        """
        # Count the number of susceptible / exposed individuals at both ends
        # of the simulation period.
        prev_amt = np.sum(prev[..., 0:2], axis=-1)
        curr_amt = np.sum(curr[..., 0:2], axis=-1)
        return prev_amt - curr_amt

    @staticmethod
    def can_seed(vec):
        """Return True if a new strain can be seeded, otherwise False."""
        return vec[..., 0] == 1

    @staticmethod
    def is_seeded(hist):
        """Identify state vectors where infections have occurred.

        :param hist: A matrix of arbitrary dimensions, whose final dimension
            covers the model state space (i.e., has a length no smaller than
            that returned by :py:func:`state_size`).
        :type hist: numpy.ndarray

        :returns: A matrix of one fewer dimensions than ``hist`` that contains
            ``1`` for state vectors where infections have occurred and ``0``
            for state vectors where they have not.
        :rtype: numpy.ndarray
        """
        return np.ceil(1 - hist[..., 0])

    @classmethod
    def is_valid(cls, hist):
        """Ignore state vectors where no infections have occurred, as their
        properties (such as parameter distributions) are uninformative."""
        return cls.is_seeded(hist)

    @classmethod
    def stat_info(cls):
        """Return the details of each statistic that can be calculated by this
        model. Each such statistic is represented as a ``(name, stat_fn)``
        pair, where ``name`` is a string that identifies the statistic and
        ``stat_fn`` is a function that calculates the statistic (see, e.g.,
        :py:func:`stat_R0`).
        """
        return [("R0", cls.stat_R0), ("Reff", cls.stat_Reff)]

    @staticmethod
    def stat_R0(hist):
        """Calculate the basic reproduction number :math:`R_0` for every
        particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return hist[..., 4] / hist[..., 6]

    @staticmethod
    def stat_Reff(hist):
        """Calculate the effective reproduction number :math:`R_{eff}` for
        every particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return hist[..., 0] * hist[..., 4] / hist[..., 6]

    @classmethod
    def state_info(cls):
        """Return the name and index of each state variable."""
        return cls.__info[:4]

    @classmethod
    def param_info(cls):
        """Return the name and index of each model parameter."""
        return cls.__info[4:]

    @staticmethod
    def initial_exposures(params, shape=None):
        if shape is None:
            return 1.0 / params['epifx']['popn_size']
        else:
            xs = np.empty(shape)
            xs.fill(1.0 / params['epifx']['popn_size'])
        return xs
