"""A bootstrap particle filter for epidemic forecasting."""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import datetime
import h5py
import logging
import numpy as np
import tempfile

__package_name__ = u'pypfilt'
__author__ = u'Rob Moss'
__email__ = u'rgmoss@unimelb.edu.au'
__copyright__ = u'2014-2015, Rob Moss'
__license__ = u'BSD 3-Clause License'
__version__ = u'0.3.0'


# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def resample(params, px):
    """Resample a particle population.

    :param params: The simulation parameters.
    :param px: An array of particle state vectors.

    The supported resampling methods are:

    - ``'basic'``:         uniform random numbers from [0, 1].
    - ``'stratified'``:    uniform random numbers from [j / m, (j + 1) / m).
    - ``'deterministic'``: select (j - a) / m for some fixed a.

    Where m is the number of particles and j = 0, ..., m - 1.

    These algorithms are described in G Kitagawa, J Comp Graph Stat
    5(1):1-25, 1996.
    `doi:10.2307/1390750 <http://dx.doi.org/10.2307/1390750>`_
    """
    # Sort the particle indices according to weight (in descending order), so
    # that we can determine the original index of each resampled particle.
    # Use the merge sort algorithm because it is stable (thus preserving the
    # behaviour of Python's built-in `sorted` function).
    sorted_ix = np.argsort(- px[:, -2], kind='mergesort')
    # Sort the weights in descending order.
    sorted_ws = px[sorted_ix, -2]
    # Calculate the upper bounds for each interval.
    bounds = np.cumsum(sorted_ws)
    # Generate the random samples using the specified resampling method.
    count = px.shape[0]
    method = params['resample']['method']
    rnd = params['resample']['rnd']
    if method == 'basic':
        choices = rnd.uniform(size=count)
    elif method == 'stratified':
        choices = (rnd.uniform(size=count) + np.arange(count)) / count
    elif method == 'deterministic':
        choices = (rnd.uniform() + np.arange(count)) / count
    else:
        # This is an error.
        raise ValueError("Invalid resampling method '{}'".format(method))
    # Resample the particles.
    new_px = np.copy(px)
    # Since the intervals and random samples are both monotonic increasing, we
    # only need step through the samples and record the current interval.
    bix = 0
    for (j, rand_val) in enumerate(choices):
        while bounds[bix] < rand_val:
            bix += 1
        new_px[j, 0:-2] = px[sorted_ix[bix]][0:-2]
        new_px[j, -1] = sorted_ix[bix]
    # Renormalise the weights.
    new_px[:, -2] = 1.0 / count
    # Copy the resampled particles back into the original array.
    px[:, :] = new_px[:, :]


def reweight(params, hist, hist_ix, obs, max_back=None):
    """Adjust particle weights in response to some observation(s).

    :param params: The simulation parameters.
    :param hist: The particle history matrix.
    :param hist_ix: The index of the current time-step in the history matrix.
    :param obs: The observation(s) that have been made.
    :param max_back: The number of time-steps into the past when the most
        recent resampling occurred (i.e., how far back the current particle
        ordering is guaranteed to persist; default is ``None``, no limit).

    :returns: A tuple; the first element (*bool*) indicates whether resampling
        is required, the second element (*float*) is the **effective** number
        of particles (i.e., accounting for weights).
    """
    periods = set(o['period'] for o in obs)
    steps_per_day = params['steps_per_day']
    log_llhd = params['log_llhd_fn']

    # Extract the particle histories at every relevant prior step.
    # It may or may not be necessary to use earlier_states().
    def hist_for(period):
        """Return past state vectors in the appropriate order."""
        steps_back = steps_per_day * period
        same_ixs = max_back is None or max_back >= steps_back
        if same_ixs:
            if steps_back > hist_ix:
                # If the observation period starts before the beginning of the
                # the simulation period, the initial state should be returned.
                return hist[0]
            else:
                return hist[hist_ix - steps_back]
        else:
            return earlier_states(hist, hist_ix, steps_back)
    period_hists = {period: hist_for(period) for period in periods}

    # Calculate the log-likelihood of obtaining the given observation, for
    # each particle.
    sc = params['hist']['state_cols']
    logs = log_llhd(params, obs, hist[hist_ix, :, 0:sc], period_hists)

    # Scale the log-likelihoods so that the maximum is 0 (i.e., has a
    # likelihood of 1) to increase the chance of smaller likelihoods
    # being within the range of double-precision floating-point.
    logs = logs - np.max(logs)
    # Calculate the effective number of particles, prior to reweighting.
    prev_eff = 1.0 / sum(w * w for w in hist[hist_ix, :, -2])
    # Update the current weights.
    hist[hist_ix, :, -2] *= np.exp(logs)
    ws_sum = np.sum(sorted(hist[hist_ix, :, -2]))
    # Renormalise the weights.
    hist[hist_ix, :, -2] /= ws_sum
    if np.any(np.isnan(hist[hist_ix, :, -2])):
        # Either the new weights were all zero, or every new non-zero weight
        # is associated with a particle whose previous weight was zero.
        nans = np.sum(np.isnan(hist[hist_ix, :, -2]))
        raise ValueError("{} NaN weights; ws_sum = {}".format(nans, ws_sum))
    # Determine whether resampling is required.
    num_eff = 1.0 / sum(w * w for w in hist[hist_ix, :, -2])
    req_resample = num_eff / params['size'] < params['resample']['threshold']

    # Detect when the effective number of particles has greatly decreased.
    eff_decr = num_eff / prev_eff
    if (eff_decr < 0.1):
        # Note: this could be mitigated by replacing the weights with their
        # square roots (for example) until the decrease is sufficiently small.
        logger = logging.getLogger(__name__)
        logger.debug("Effective particles decreased by {}".format(eff_decr))

    return (req_resample, num_eff)


def __log_step(when, do_resample, num_eff=None):
    """Log the state of the particle filter when an observation is made or
    when particles have been resampled.

    :param when: The current simulation time.
    :type when: datetime.datetime
    :param do_resample: Whether particles were resampled at this time-step.
    :type do_resample: bool
    :param num_eff: The effective number of particles (default is ``None``).
    :type num_eff: float
    """
    logger = logging.getLogger(__name__)
    resp = {True: 'Y', False: 'N'}
    if num_eff is not None:
        logger.debug('{} RS: {}, #px: {:7.1f}'.format(
            when.strftime('%Y-%m-%d %H:%M'), resp[do_resample], num_eff))
    elif do_resample:
        logger.debug('{} RS: {}'.format(
            when.strftime('%Y-%m-%d %H:%M'), resp[do_resample]))


def step(params, hist, hist_ix, step_num, when, step_obs, max_back, is_fs):
    """Perform a single time-step for every particle.

    :param params: The simulation parameters.
    :param hist: The particle history matrix.
    :param hist_ix: The index of the current time-step in the history matrix.
    :param step_num: The time-step number.
    :param when: The current simulation time.
    :param step_obs: The list of observations for this time-step.
    :param max_back: The number of time-steps into the past when the most
        recent resampling occurred; must be either a positive integer or
        ``None`` (no limit).
    :param is_fs: Indicate whether this is a forecasting simulation (i.e., no
        observations).
        For deterministic models it is useful to add some random noise when
        estimating, to allow identical particles to differ in their behaviour,
        but this is not desirable when forecasting.

    :return: ``True`` if resampling was performed, otherwise ``False``.
    """
    d_t = params['dt']

    # Allocate an array that enumerates the particles, if it isn't present.
    if params['px_range'] is None:
        params['px_range'] = np.arange(params['size'])

    # Matrices of previous and current state vectors.
    sc = params['hist']['state_cols']
    prev = hist[hist_ix - 1, :, 0:sc]
    curr = hist[hist_ix, :, 0:sc]

    # Step each particle forward by one time-step.
    params['model'].update(params, when, d_t, is_fs, prev, curr)

    # Copy the particle weights from the previous time-step.
    # These will be updated by ``reweight`` as necessary.
    hist[hist_ix, :, -2] = hist[hist_ix - 1, :, -2]

    # The particle ordering is (as yet) unchanged.
    # This will be updated by ``resample`` as necessary.
    hist[hist_ix, :, -1] = params['px_range']

    # Account for observations, if any.
    num_eff = None
    do_resample = False
    if step_obs:
        do_resample, num_eff = reweight(params, hist, hist_ix, step_obs,
                                        max_back)

    __log_step(when, do_resample, num_eff)

    # Perform resampling when required.
    if do_resample:
        resample(params, hist[hist_ix])
        __log_step(when, True, params['size'])
    # Indicate whether resampling occurred at this time-step.
    return do_resample


def run(params, start, end, streams, summary, state=None,
        save_when=None, save_to=None):
    """Run the particle filter against any number of data streams.

    :param params: The simulation parameters.
    :type params: dict
    :param start: The start of the simulation period.
    :type start: datetime.date
    :param end: The (**exclusive**) end of the simulation period.
    :type end: datetime.date
    :param streams: A list of observation streams (see
        :py:func:`~pypfilt.Time.with_observations`).
    :param summary: An object that generates summaries of each simulation.
    :param state: A previous simulation state as returned by, e.g., this
        function.
    :param save_when: Dates at which to save the particle history matrix.
    :param save_to: The filename for saving the particle history matrix.

    :returns: The resulting simulation state: a dictionary that contains the
        simulation parameters (``'params'``), the particle history matrix
        (``'hist'``), and the summary statistics (``'summary'``).
    """
    # Construct the time-step generator.
    params['dt'] = 1.0 / params['steps_per_day']
    seed = params['resample']['prng_seed']
    params['resample']['rnd'] = np.random.RandomState(seed)
    sim_time = Time(start, end, params['steps_per_day'])
    steps = sim_time.with_observations(*streams)
    # Determine whether this is a forecasting run, by checking whether there
    # are any observation streams.
    is_fs = not streams
    # We allow the history matrix to be provided in order to allow, e.g., for
    # forecasting from any point in a completed simulation.
    if state is None:
        hist = history_matrix(params, sim_time)
        offset = 0
    else:
        hist = state['hist']
        offset = state['offset']
        # Ensure that the number of particles is recorded as a parameter.
        params['size'] = hist.shape[1]
    # Allocate space for the summary statistics.
    summary.allocate(start, end, forecasting=is_fs)
    win_start = start
    most_recent = None
    last_rs = None
    # Simulate each time-step.
    for (step_num, when, obs) in steps:
        hist_ix = step_num + offset
        if not win_start:
            win_start = most_recent
        # Check whether the end of the history matrix has been reached.
        # If so, shift the sliding window forward in time.
        if hist_ix == hist.shape[0]:
            # Calculate summary statistics in blocks.
            if most_recent is not None:
                # The current simulation has covered a well-defined block of
                # the history matrix.
                summary.summarise(hist, sim_time, win_start, most_recent,
                                  offset)
            else:
                # If most_recent is None, no time-steps have been simulated.
                # This means, e.g., a forecasting simulation has begun at the
                # final time-step in the matrix; the correct response is to
                # calculate summary statistics only for this one time-step.
                summary.summarise(hist, sim_time, win_start, win_start,
                                  offset)
            win_start = None
            shift = params['hist']['wind_shift'] * params['steps_per_day']
            offset -= shift
            hist_ix = step_num + offset
            # Shift the sliding window forward.
            hist[:-shift, :, :] = hist[shift:, :, :]
            hist[hist_ix, :, :-2] = 0
        if last_rs is None:
            max_back = None
        else:
            max_back = (step_num - last_rs)
        resampled = step(params, hist, hist_ix, step_num, when, obs,
                         max_back, is_fs)
        if resampled:
            last_rs = step_num
        most_recent = when
        # Check whether to save the particle history matrix to disk.
        if save_when is not None and save_to is not None:
            if when in save_when:
                # Note: we only need to save the current matrix block!
                with h5py.File(save_to, 'a') as f:
                    grp = f.create_group(str(when).encode("utf-8"))
                    grp.create_dataset('offset', data=np.int32(hist_ix))
                    grp.create_dataset('hist', data=np.float64(hist))

    # Calculate summary statistics for the remaining time-steps.
    if win_start is not None and most_recent is not None:
        summary.summarise(hist, sim_time, win_start, most_recent, offset)

    # Return the complete simulation state.
    return {'params': params.copy(), 'hist': hist,
            'summary': summary.get_stats()}


def __cleanup(files, dirs):
    """Delete temporary files and directories.
    This is intended for use with ``atexit.register()``.

    :param files: The list of files to delete.
    :param dirs: The list of directories to delete (*after* all of the files
        have been deleted). Note that these directories must be empty in order
        to be deleted.
    """
    import os.path

    logger = logging.getLogger(__name__)

    for tmp_file in files:
        if os.path.isfile(tmp_file):
            try:
                os.remove(tmp_file)
                logger.debug("Deleted '{}'".format(tmp_file))
            except OSError as e:
                msg = "Can not delete '{}': {}".format(tmp_file, e.strerror)
                logger.warning(msg)
        elif os.path.exists(tmp_file):
            logger.warning("'{}' is not a file".format(tmp_file))
        else:
            logger.debug("File '{}' already deleted".format(tmp_file))

    for tmp_dir in dirs:
        if os.path.isdir(tmp_dir):
            try:
                os.rmdir(tmp_dir)
                logger.debug("Deleted '{}'".format(tmp_dir))
            except OSError as e:
                msg = "Can not delete '{}': {}".format(tmp_dir, e.strerror)
                logger.warning(msg)
        elif os.path.exists(tmp_dir):
            logger.warning("'{}' is not a directory".format(tmp_dir))
        else:
            logger.debug("Directory '{}' already deleted".format(tmp_dir))


def forecast(params, start, end, streams, dates, summary, filename):
    """Generate forecasts from various dates during a simulation.

    :param params: The simulation parameters.
    :type params: dict
    :param start: The start of the simulation period.
    :type start: datetime.date
    :param end: The (**exclusive**) end of the simulation period.
    :type end: datetime.date
    :param streams: A list of observation streams.
    :param dates: The dates at which forecasts should be generated.
    :param summary: An object that generates summaries of each simulation.
    :param filename: The output file to generate (can be ``None``).

    :returns: The simulation state for each forecast date.
    """
    import atexit
    import os
    import os.path

    # Ensure that the forecasting dates lie within the simulation period.
    invalid_fs = [str(d) for d in dates if d < start or d >= end]
    if invalid_fs:
        raise ValueError("Invalid forecasting date(s) {}".format(invalid_fs))

    logger = logging.getLogger(__name__)
    logger.info("  {}  Estimating  from {} to {}".format(
        datetime.datetime.now().strftime("%H:%M:%S"), start, end))

    # Generate forecasts in order from earliest to latest forecasting date.
    # Note that forecasting from the start date will duplicate the complete
    # simulation (below) and is therefore redundant.
    forecast_dates = [d for d in sorted(dates) if d > start]

    # Note: it would be more efficient to only simulate to the final forecast
    # date, rather than to the end of the entire simulation period.
    tmp_dir = tempfile.mkdtemp(dir=params['tmp_dir'])
    tmp_file = os.path.join(tmp_dir, "history.hdf5")
    # Ensure these files are always deleted upon termination.
    atexit.register(__cleanup, files=[tmp_file], dirs=[tmp_dir])
    logger.debug("Temporary file for history matrix: '{}'".format(tmp_file))
    state = run(params, start, end, streams, summary,
                save_when=forecast_dates, save_to=tmp_file)
    # Save the complete simulation, which incorporated every observation
    # throughout the entire simulation period.
    forecasts = {'complete': state}

    # Ensure the dates are ordered from latest to earliest.
    for start_date in forecast_dates:
        logger.info("  {}  Forecasting from {} to {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), start_date, end))
        # We can reuse the history matrix for each forecast, since all of the
        # pertinent details are recorded in the summary.
        with h5py.File(tmp_file, 'r') as f:
            grp = f[str(start_date).encode("utf-8")]
            state['offset'] = grp['offset'][()]
            state['hist'] = grp['hist'][:, :, :]

        fstate = run(state['params'], start_date, end, [], summary,
                     state=state)

        forecasts[start_date] = fstate

    # Save the observations (flattened into a single list).
    forecasts['obs'] = sum(streams, [])

    # Save the forecasting results to disk.
    if filename is not None:
        logger.info("  {}  Saving to:  {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), filename))
        # Save the results in the output directory.
        filepath = os.path.join(params['out_dir'], filename)
        summary.save_forecasts(forecasts, filepath)

    # Remove the temporary file and directory.
    __cleanup(files=[tmp_file], dirs=[tmp_dir])

    return forecasts


def default_params(model, max_days=0, px_count=0):
    """The default particle filter parameters.

    Memory usage can reach extreme levels with a large number of particles,
    and so it may be necessary to keep only a sliding window of the entire
    particle history matrix in memory.

    :param model: The system model.
    :param max_days: The number of contiguous days that must be kept in memory
        (e.g., the largest observation period).
    :param px_count: The number of particles.
    """
    params = {
        'resample': {
            # Resample when the effective number of particles is 25%.
            'threshold': 0.25,
            # The deterministic method is the best resampling method, see the
            # appendix of Kitagawa 1996 (DOI:10.2307/1390750).
            'method': 'deterministic',
            # Use the default initial PRNG state, whatever that might be.
            'prng_seed': None,
        },
        'hist': {
            # The sliding window size, in days.
            'wind_size': 2 * max_days,
            # The amount to shift the sliding window, in days.
            'wind_shift': max_days,
            # The number of particles.
            'px_count': px_count,
        },
        # Simulate 5 time-steps per day.
        'steps_per_day': 5,
        # An array that enumerates the particles.
        'px_range': None,
        # The simulation model.
        'model': model,
        # Directory for storing output files.
        'out_dir': '.',
        # Directory for storing temporary files.
        'tmp_dir': tempfile.gettempdir(),
    }
    # Define the simulation model parameter priors.
    params['prior'] = model.priors(params)
    return params


def history_matrix(params, sim_time, extra=2):
    """Allocate a particle history matrix of sufficient size to store an
    entire particle filter simulation.

    :param params: The simulation parameters.
    :type params: dict
    :param sim_time: The simulation period.
    :type sim_time: :py:class:`~pypfilt.Time`
    :param extra: The number of additional columns.
    :type extra: int

    :returns: A particle history matrix.
    :rtype: numpy.ndarray
    """
    # Determine the size of the state vector; provide an index of -1 to
    # indicate that this is not a true model instantiation (i.e., that we
    # won't use the return value beyond checking its dimensions).
    state_size = params['model'].state_size()
    # Ensure sufficient columns to record particle weights and parents.
    if extra < 2:
        raise ValueError("Too few extra columns: {} < 2".format(extra))
    # Determine the number of particles and their initial weights.
    px_count = params['hist']['px_count']
    # Ensure there is a strictly-positive number of particles.
    if px_count < 1:
        raise ValueError("Too few particles: {}".format(px_count))
    init_weight = 1.0 / px_count
    # Record the number of particles.
    logger = logging.getLogger(__name__)
    logger.debug("Size = {}".format(px_count))
    # Determine the number of time-steps for which to allocate space.
    if params['hist']['wind_size'] > 0 and params['hist']['wind_shift'] > 0:
        num_steps = params['hist']['wind_size'] * params['steps_per_day'] + 1
    else:
        num_steps = sim_time.step_count() + 1
    # Allocate an array that enumerates the particles.
    params['px_range'] = np.arange(px_count)
    # Allocate the particle history matrix and record the initial states.
    hist = np.zeros((num_steps, px_count, state_size + extra))
    logger.debug("Hist.nbytes = {}".format(hist.nbytes))
    params['model'].init(params, hist[0, :, 0:state_size])
    hist[0, :, -2] = init_weight
    hist[0, :, -1] = params['px_range']
    # Record the number of particles.
    params['size'] = px_count
    # Record the number of state columns and extra columns.
    params['hist']['state_cols'] = state_size
    params['hist']['extra_cols'] = extra
    # Return the allocated (and initialised) particle history matrix.
    return hist


def earlier_states(hist, ix, steps):
    """Return the particle states at a previous time-step, ordered with
    respect to their current arrangement.

    :param hist: The particle history matrix.
    :param ix: The current time-step index.
    :param steps: The number of steps back in time.
    """
    parent_ixs = np.arange(hist.shape[1])
    # Don't go too far back (negative indices jump into the future).
    steps = min(steps, ix)
    for i in range(steps):
        parent_ixs = hist[ix - i, parent_ixs, -1].astype(int)
    return hist[ix - steps, parent_ixs, :]


class Time(object):
    """A mapping between real-world and model timescales."""

    def __init__(self, start, end, steps_per_day):
        """Define the key connections between real-world and model timescales.

        :param start: The start of the simulation period.
        :type start: datetime.datetime
        :param end: The end of the simulation period.
        :type end: datetime.datetime
        :param steps_per_day: The number of time-steps per (real-world) day.
        :type steps_per_day: int
        """
        if isinstance(start, datetime.datetime):
            self.start = start
        else:
            raise ValueError("Invalid start: {}".format(start))
        if isinstance(end, datetime.datetime):
            self.end = end
        else:
            raise ValueError("Invalid end: {}".format(end))
        self.steps_per_day = steps_per_day

    def __eq__(self, other):
        """Test for equality."""
        if type(other) is type(self):
            result = self.steps_per_day == other.steps_per_day
            result = result and self.start == other.start
            result = result and self.end == other.end
            return result
        else:
            return False

    def __ne__(self, other):
        """Test for inequality."""
        return not self.__eq__(other)

    def __str__(self):
        """Return a simple description of the simulation period."""
        return "{} from {} to {} ({} steps/day)".format(
            type(self).__name__, self.start, self.end, self.steps_per_day)

    def __repr__(self):
        """Return a readable representation of the simulation period."""
        return "{}.{}({}, {}, {})".format(
            type(self).__module__, type(self).__name__,
            repr(self.start), repr(self.end), self.steps_per_day)

    def steps(self, nth=1, offset=0):
        """Return a generator that yields a sequence of time-step numbers
        spanning the simulation period.

        :param nth: Return every nth time-step.
        :type nth: int
        :param offset: The number of time-steps after the simulation start
            from which the time-steps will be generated.
        """
        total_steps = self.step_of(self.end)
        step = 0 + offset
        while step <= total_steps:
            yield step
            step += nth

    def step_count(self):
        """Return the number of time-steps required for the simulation period.
        """
        return self.step_of(self.end)

    def step_of(self, d):
        """Return the time-step associated with a date or datetime.

        - For ``date`` objects, the time-step number marks the **start of that
          day**.
        - For ``datetime`` objects, the time-step number is rounded to the
          **most recent** time-step.

        :param d: The moment for which a time-step number is desired.
        :type d: datetime.datetime
        """
        if not isinstance(d, datetime.datetime):
            if isinstance(d, datetime.date):
                d = datetime.datetime(d.year, d.month, d.day)

        if isinstance(d, datetime.datetime):
            diff = d - self.start
            frac_diff = diff - datetime.timedelta(diff.days)
            frac_day = frac_diff.total_seconds()
            frac_day /= datetime.timedelta(days=1).total_seconds()
            day_steps = diff.days * self.steps_per_day
            day_frac = frac_day * float(self.steps_per_day)
            # Note that day_frac is rounded down to the most recent time-step.
            # This prevents the step number exceeding the final time-step.
            return day_steps + int(day_frac)
        else:
            raise ValueError("{}.step_of() does not understand {}".format(
                type(self).__name__, type(d)))

    def with_observations(self, *streams):
        """Return a generator that yields a sequence of time-step numbers, the
        date and time associated with each time-step, and a list of any
        observations made during each time-step.

        :param streams: Any number of observations streams.
        :type streams: list(list(Observation))

        :rtype: (int, datetime.datetime, list(Observation))
        """

        def obs_date(obs):
            """Return the date of an observation."""
            d = obs['date']
            if isinstance(d, datetime.datetime):
                return d
            else:
                raise ValueError("{}.{}() does not understand{}".format(
                    type(self).__name__, "with_observations", type(d)))

        def obs_tuple(stream):
            """Return the next observation from a stream, represented as a
            ```(date, observation, stream)``` tuple, or ```None``` if there
            are no further observations."""
            if len(stream) == 0:
                return None
            else:
                obs, stream = stream[0], stream[1:]
                # Skip observations before the start of the simulation.
                while obs_date(obs) <= self.start:
                    if len(stream) == 0:
                        return None
                    else:
                        obs, stream = stream[0], stream[1:]
                return (obs_date(obs), obs, stream)

        def update(dt, obs_str):
            """Consume observations and update observation streams, as
            appropriate."""
            if obs_str[0] <= dt:
                return obs_tuple(obs_str[2])
            else:
                return obs_str

        # Maintain a list of (date, observation, stream) pairs.
        obs_streams = [obs_tuple(stream) for stream in streams]
        # Remove any streams that yielded no relevant observations.
        obs_streams = [o for o in obs_streams if o is not None]
        # Build a generator that returns (timestep, datetime) pairs *except*
        # for the starting time (i.e., before the first time-step).
        delta = datetime.timedelta(days=1.0 / self.steps_per_day)
        one_day = datetime.timedelta(days=1)

        step = 1
        d = self.start + delta
        while d <= self.end:
            # Collect the observations for this time-step, if any.
            curr_obs = [obs for (date, obs, _) in obs_streams if date <= d]
            # Update the list of observation streams.
            if len(curr_obs) > 0:
                obs_streams = [update(d, obs_str) for obs_str in obs_streams]
                # Only retain non-empty observation streams.
                obs_streams = [o for o in obs_streams if o is not None]
            # Yield a (step_number, datetime, observations) tuple.
            yield (step, d, curr_obs)
            # Proceed to the next time-step.
            step += 1
            curr_day = step // self.steps_per_day
            curr_off = step % self.steps_per_day
            d = self.start + curr_day * one_day + curr_off * delta
