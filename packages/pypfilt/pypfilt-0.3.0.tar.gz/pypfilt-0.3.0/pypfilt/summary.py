"""Calculation of simulation summary statistics."""

from __future__ import absolute_import, division, print_function
# Note: unicode_literals produces NumPy errors, since dtype field names cannot
#       be unicode (https://github.com/numpy/numpy/issues/2407).
# from __future__ import unicode_literals

import datetime
import h5py
import logging
import numpy as np
import pypfilt


def dtype_date(name='date'):
    """The dtype for columns that store dates."""
    return (name, 'S20')


def dtype_unit(obs_list, name='unit'):
    """ The dtype for columns that store observation units."""
    return (name, 'S{}'.format(max(len(o['unit']) for o in obs_list)))


def dtype_period(name='period'):
    """ The dtype for columns that store observation periods."""
    return (name, np.int8)


class Table(object):
    """
    The base class for summary statistic tables.

    Tables are used to record rows of summary statistics as a simulation
    progresses.

    :param name: the name of the table in the output file.
    """

    def __init__(self, name):
        self.name = name

    def dtype(self, params, obs_list):
        """
        Return the column names and data types, represented as a list of
        ``(name, data type)`` tuples. See the NumPy documentation for details.

        :param params: The simulation parameters.
        :param obs_list: A list of all observations.
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        """
        Return the number of rows required for a single simulation.

        :param start_date: The date at which the simulation starts.
        :param end_date: The date at which the simulation ends.
        :param n_days: The number of days for which the simulation runs.
        :param n_sys: The number of observation systems (i.e., data sources).
        :param forecasting: ``True`` if this is a forecasting simulation,
            otherwise ``False``.
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        """
        Record rows of summary statistics for some portion of a simulation.

        :param hist: The particle history matrix.
        :param weights: The weight of each particle at each date in the
            simulation window; it has dimensions ``(d, p)`` for ``d`` days and
            ``p`` particles.
        :param fs_date: The forecasting date; if this is not a forecasting
            simulation, this is the date at which the simulation ends.
        :param dates: A list of ``(datetime, ix, hist_ix)`` tuples that
            identify each day in the simulation window, the index of that day
            in the simulation window, and the index of that day in the
            particle history matrix.
        :param obs_types: A set of ``(unit, period)`` tuples that identify
            each observation system from which observations have been taken.
        :param insert_fn: A function that inserts one or more rows into the
            underlying data table; see the examples below.
        :raises NotImplementedError: Derived classes *must* implement this
            method.

        The row insertion function can be used as follows:

        .. code-block:: python

           # Insert a single row, represented as a tuple.
           insert_fn((x, y, z))
           # Insert multiple rows, represented as a list of tuples.
           insert_fn([(x0, y0, z0), (x1, y1, z1)], n=2)
        """
        raise NotImplementedError()

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        """
        Record rows of summary statistics at the end of a simulation.

        The parameters are as per :meth:`.add_rows`.

        Derived classes should only implement this method if rows must be
        recorded by this method; the provided method does nothing.
        """
        pass

    def monitors(self):
        """
        Return a list of monitors required by this Table.

        Derived classes should implement this method if they require one or
        more monitors; the provided method returns an empty list.
        """
        return []


class Monitor(object):
    """
    The base class for simulation monitors.

    Monitors are used to calculate quantities that:

    * Are used by multiple Tables (i.e., avoiding repeated computation); or
    * Require a complete simulation for calculation (as distinct from Tables,
      which incrementally record rows as a simulation progresses).

    The quantities calculated by a Monitor can then be recorded by
    :meth:`.Table.add_rows` and/or :meth:`.Table.finished`.
    """

    def prepare(self, params, obs_list):
        """
        Perform any required preparation prior to a set of simulations.

        :param params: The simulation parameters.
        :param obs_list: A list of all observations.
        """
        pass

    def begin_sim(self, start_date, end_date, n_days, n_sys, forecasting):
        """
        Perform any required preparation at the start of a simulation.

        :param start_date: The date at which the simulation starts.
        :param end_date: The date at which the simulation ends.
        :param n_days: The number of days for which the simulation runs.
        :param n_sys: The number of observation systems (i.e., data sources).
        :param forecasting: ``True`` if this is a forecasting simulation,
            otherwise ``False``.
        """
        pass

    def monitor(self, hist, weights, fs_date, dates, obs_types):
        """
        Monitor the simulation progress.

        :param hist: The particle history matrix.
        :param weights: The weight of each particle at each date in the
            simulation window; it has dimensions ``(d, p)`` for ``d`` days and
            ``p`` particles.
        :param fs_date: The forecasting date; if this is not a forecasting
            simulation, this is the date at which the simulation ends.
        :param dates: A list of ``(datetime, ix, hist_ix)`` tuples that
            identify each day in the simulation window, the index of that day
            in the simulation window, and the index of that day in the
            particle history matrix.
        :param obs_types: A set of ``(unit, period)`` tuples that identify
            each observation system from which observations have been taken.
        :raises NotImplementedError: Derived classes *must* implement this
            method.
        """
        raise NotImplementedError()

    def end_sim(self, hist, weights, fs_date, dates, obs_types):
        """
        Finalise the data as required for the relevant summary statistics.

        The parameters are as per :meth:`.monitor`.

        Derived classes should only implement this method if finalisation of
        the monitored data is required; the provided method does nothing.
        """
        pass


class ParamCovar(Table):
    """
    Calculate the covariance between all pairs of model parameters during each
    simulation.

    :param name: the name of the table in the output file.
    """

    def __init__(self, name='param_covar'):
        Table.__init__(self, name)

    def dtype(self, params, obs_list):
        self.__params = params
        self.__param_info = params['model'].param_info()
        self.__num_params = len(self.__param_info)
        nlen = max(len(info[0]) for info in self.__param_info)

        fs_date = dtype_date('fs_date')
        date = dtype_date()
        param1 = ('param1', 'S{}'.format(nlen))
        param2 = ('param2', 'S{}'.format(nlen))
        covar = ('covar', np.float64)
        return [fs_date, date, param1, param2, covar]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        num_params = len(self.__param_info)
        return n_days * num_params * (num_params - 1) / 2

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        from . import stats

        num_params = len(self.__param_info)

        for date, ix, hist_ix in dates:
            date_str = str(date)
            min_ix = min(info[1] for info in self.__param_info)
            max_ix = max(info[1] for info in self.__param_info)
            x = hist[hist_ix, :, min_ix:max_ix + 1]
            covars = stats.cov_wt(x, weights[ix, :])
            for ix1 in range(num_params):
                name1 = self.__param_info[ix1][0]
                for ix2 in range(ix1 + 1, num_params):
                    name2 = self.__param_info[ix2][0]
                    row = (fs_date, date_str, name1, name2, covars[ix1, ix2])
                    insert_fn(row)


class ModelCIs(Table):
    """
    Calculate fixed-probability central credible intervals for all state
    variables and model parameters.

    :param probs: an array of probabilities that define the size of each
        central credible interval.
        The default value is ``numpy.uint8([0, 50, 90, 95, 99, 100])``.
    :param name: the name of the table in the output file.
    """

    def __init__(self, probs=None, name='model_cints'):
        Table.__init__(self, name)
        if probs is None:
            probs = np.uint8([0, 50, 90, 95, 99, 100])
        self.__probs = probs

    def dtype(self, params, obs_list):
        self.__params = params
        self.__vars_info = params['model'].state_info()
        self.__param_info = params['model'].param_info()
        self.__stat_info = params['model'].stat_info()
        self.__num_stats = len(self.__param_info) + len(self.__stat_info)
        self.__num_stats += len(self.__vars_info)

        # Determine the length of the longest name.
        var_names = [info[0] for info in self.__vars_info]
        param_names = [info[0] for info in self.__param_info]
        stat_names = [info[0] for info in self.__stat_info]
        nlen = max(len(name) for name in var_names + param_names + stat_names)

        fs_date = dtype_date('fs_date')
        date = dtype_date()
        prob = ('prob', np.int8)
        ymin = ('ymin', np.float64)
        ymax = ('ymax', np.float64)
        # Variables ('var'), parameters ('param') or statistics ('stat').
        param_type = ('type', 'S5')
        name = ('name', 'S{}'.format(nlen))
        return [fs_date, date, prob, ymin, ymax, param_type, name]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        # Need a row for each interval, for each day, for each parameter,
        # variable and statistic.
        return len(self.__probs) * n_days * self.__num_stats

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        from . import stats

        for date, ix, hist_ix in dates:
            date_str = str(date)

            # Identify which state vectors to examine.
            valid = self.__params['model'].is_valid(hist[hist_ix])
            # Note that np.where() returns a *tuple*  of arrays (one for
            # each dimension) and we're only scanning a 1D array.
            mask = np.where(valid)[0]

            if np.count_nonzero(mask):
                ws = weights[ix, mask]
                for (lbl, pix) in self.__param_info:
                    sub_hist = hist[hist_ix, mask, pix]
                    cred_ints = stats.cred_wt(sub_hist, ws, self.__probs)
                    for cix, pctl in enumerate(self.__probs):
                        row = (fs_date, date_str, pctl, cred_ints[pctl][0],
                               cred_ints[pctl][1], 'param', lbl)
                        insert_fn(row)
                for (lbl, stat_fn) in self.__stat_info:
                    stat_vec = stat_fn(hist[hist_ix, mask])
                    cred_ints = stats.cred_wt(stat_vec, ws, self.__probs)
                    for cix, pctl in enumerate(self.__probs):
                        row = (fs_date, date_str, pctl, cred_ints[pctl][0],
                               cred_ints[pctl][1], 'stat', lbl)
                        insert_fn(row)
                for (lbl, vix) in self.__vars_info:
                    sub_hist = hist[hist_ix, mask, vix]
                    cred_ints = stats.cred_wt(sub_hist, ws, self.__probs)
                    for cix, pctl in enumerate(self.__probs):
                        row = (fs_date, date_str, pctl, cred_ints[pctl][0],
                               cred_ints[pctl][1], 'var', lbl)
                        insert_fn(row)
            else:
                for pctl in self.__probs:
                    for (lbl, _) in self.__param_info:
                        row = (fs_date, date_str, pctl, 0, 0, 'param', lbl)
                        insert_fn(row)
                    for (lbl, _) in self.__stat_info:
                        row = (fs_date, date_str, pctl, 0, 0, 'stat', lbl)
                        insert_fn(row)
                    for (lbl, _) in self.__vars_info:
                        row = (fs_date, date_str, pctl, 0, 0, 'var', lbl)
                        insert_fn(row)


class HDF5(object):
    """
    Save tables of summary statistics to an HDF5 file.

    :param params: The simulation parameters.
    :param obs_list: A list of all observations.
    :param meta: The simulation metadata; by default the output of
        :func:`.metadata` is used.
    :param first_day: If ``False`` (the default) statistics are calculated
       from the date of the first *observation*. If ``True``, statistics are
       calculated from the very beginning of the simulation period.
    """

    def __init__(self, params, all_obs, meta=None, first_day=False):
        # Store simulation metadata.
        if meta is None:
            self.__metadata = metadata(params)
        else:
            self.__metadata = meta

        # Store the observations and simulation parameters.
        self.__all_obs = all_obs
        self.__params = params

        # Allocate variables to store the details of each summary table.
        self.__tbl_dict = {}
        self.__dtypes = {}
        # When a simulation commences, this will be a dictionary that maps
        # table names to NumPy structured arrays; the value of ``None``
        # indicates that no tables have been allocated.
        self.__df = None

        self.__monitors = set()

        self.__data_group = 'data'

        # If True, start statistics at the beginning of the simulation period,
        # otherwise start statistics at the date of the first observation.
        self.__first_day = first_day

        # Identify all combinations for observation periods and units.
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in self.__all_obs))

    def add_tables(self, *tables):
        """
        Add summary statistic tables that will be included in the output file.
        """
        for tbl in tables:
            if tbl.name in self.__tbl_dict:
                raise ValueError("Table '{}' already exists".format(tbl.name))
            # Add the table to the relevant internal variables.
            self.__tbl_dict[tbl.name] = tbl
            self.__dtypes[tbl.name] = tbl.dtype(self.__params, self.__all_obs)

            # Add the required monitors for this table, if any.
            for mon in tbl.monitors():
                if mon not in self.__monitors:
                    self.__monitors.add(mon)
                    mon.prepare(self.__params, self.__all_obs)

    def allocate(self, start_date, end_date, forecasting=False):
        """Allocate space for the simulation statistics."""
        if self.__df is not None:
            raise ValueError("Tables have already been allocated")

        logger = logging.getLogger(__name__)

        self.__start_date = start_date
        self.__end_date = end_date
        if forecasting:
            # Forecasting from the start of the simulation period.
            self.__fs_date = start_date
        else:
            # Not forecasting, so all observations are included.
            self.__fs_date = end_date

        # Retain only observations that occur during the simulation period.
        min_date = datetime.datetime.fromordinal(start_date.toordinal())
        max_date = datetime.datetime.fromordinal(end_date.toordinal())

        def include_obs(d):
            try:
                return min_date <= d <= max_date
            except TypeError:
                raise ValueError("invalid observation date '{}'".format(d))

        fs_obs = [o for o in self.__all_obs if include_obs(o['date'])]

        # Calculate the number of days from the first observation date to the
        # end of the simulation
        obs_dates = sorted(set(o['date'] for o in fs_obs))
        # Either use observation dates *or* all dates.
        if self.__first_day:
            n_days = 1 + (end_date - start_date).days
            self.__all_dates = [start_date + datetime.timedelta(i)
                                for i in range(n_days)]
        else:
            obs_start = min(obs_dates)
            n_days = 1 + (end_date - obs_start).days
            self.__all_dates = [obs_start + datetime.timedelta(i)
                                for i in range(n_days)]
        n_sys = len(self.__obs_types)

        # Notify each monitor.
        for mon in self.__monitors:
            mon.begin_sim(start_date, end_date, n_days, n_sys, forecasting)

        # Determine the number of rows to allocate for each table.
        # Note: the items() method returns a list in Python 2 and a view
        # object in Python 3; since the number of tables will always be small
        # (on the order of 10) the overhead of using items() in Python 2 and
        # not iteritems() --- which returns an interator --- is negligible.
        n_rows = {n: t.n_rows(start_date, end_date, n_days, n_sys,
                              forecasting)
                  for (n, t) in self.__tbl_dict.items()}
        # Allocate tables that require at least one row.
        self.__df = {tbl: np.empty(n_rows[tbl], dtype=self.__dtypes[tbl])
                     for tbl in n_rows if n_rows[tbl] > 0}
        # Initialise a row counter for each allocated table.
        self.__ix = {tbl: 0 for tbl in self.__df}
        # Create a row insertion function for each allocated table.
        self.__insert = {tbl: self.__insert_row_fn(tbl) for tbl in self.__df}

        logger.debug("Summary.allocate({}, {}): {} points".format(
            start_date, end_date, n_days))

    def __insert_row_fn(self, tbl):
        def insert(fields, n=1):
            row_ix = self.__ix[tbl]
            self.__df[tbl][row_ix:row_ix + n] = fields
            self.__ix[tbl] += n
        return insert

    def summarise(self, hist, sim_time, start_date, end_date, offset):
        """
        Calculate statistics for some portion of the simulation period.

        :param hist: The particle history matrix.
        :param sim_time: The entire simulation period.
        :param start_date: The start of the period to be summarised.
        :param end_date: The end of the period to be summarised.
        :param offset: The history matrix time-step offset.
        """
        if self.__df is None:
            raise ValueError("Tables have not been allocated")

        if self.__start_date > start_date or self.__end_date < end_date:
            raise ValueError("Summary.summarise() called for invalid period")

        logger = logging.getLogger(__name__)

        dates = [(d, ix, sim_time.step_of(d) + offset)
                 for (ix, d) in enumerate(d for d in self.__all_dates
                                          if start_date <= d <= end_date)]
        num_dates = len(dates)

        logger.debug("Summary.summarise({}, {}): {} dates".format(
            start_date, end_date, num_dates))

        # Record the particle weights.
        weights = np.zeros((num_dates, hist.shape[1]))
        for date, ix, hist_ix in dates:
            weights[ix, :] = hist[hist_ix, :, -2]

        fs_date = self.__fs_date
        obs_types = self.__obs_types

        for mon in self.__monitors:
            mon.monitor(hist, weights, fs_date, dates, obs_types)

        for tbl in self.__df:
            insert_fn = self.__insert[tbl]
            self.__tbl_dict[tbl].add_rows(
                hist, weights, fs_date, dates, obs_types, insert_fn)

        if end_date == self.__end_date:
            for mon in self.__monitors:
                mon.end_sim(hist, weights, fs_date, dates, obs_types)

            for tbl in self.__df:
                insert_fn = self.__insert[tbl]
                self.__tbl_dict[tbl].finished(
                    hist, weights, fs_date, dates, obs_types, insert_fn)

    def get_stats(self):
        """Return the calculated statistics for a single simulation."""
        if self.__df is None:
            raise ValueError("Tables have not been created")

        logger = logging.getLogger(__name__)
        logger.debug("Summary.get()")

        # Check all table rows are filled (and no further).
        for tbl in self.__df:
            alloc = self.__df[tbl].shape[0]
            used = self.__ix[tbl]
            if alloc != used:
                msg = "Table '{}' allocated {} rows but filled {}"
                raise ValueError(msg.format(tbl, alloc, used))

        # Return the summary tables and remove them from this class instance.
        stats = self.__df
        self.__df = None
        return stats

    def __obs_table(self, all_obs):
        ulen = max(len(o['unit']) for o in all_obs)
        slen = max(len(o['source']) for o in all_obs)
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        source = ('source', 'S{}'.format(slen))
        date = dtype_date()
        value = ('value', np.float64)
        obs_df = np.empty(len(all_obs),
                          dtype=[unit, period, source, date, value])
        for ix, o in enumerate(all_obs):
            obs_df[ix] = (o['unit'], o['period'], o['source'],
                          str(o['date']), o['value'])
        return obs_df

    def save_forecasts(self, fs, filename):
        """
        Save forecast summaries to disk in the HDF5 binary data format.

        This function creates the following datasets that summarise the
        estimation and forecasting outputs:

        - ``'data/TABLE'`` for each table.

        The provided metadata will be recorded under ``'meta/'``.

        If dataset creation timestamps are enabled, two simulations that
        produce identical outputs will not result in identical files.
        Timestamps will be disabled where possible (requires h5py >= 2.2):

        - ``'hdf5_track_times'``: Presence of creation timestamps.

        :param fs: Simulation outputs, as returned by ``pypfilt.forecast()``.
        :param filename: The filename to which the data will be written.
        """
        fs_dates = [d for d in fs.keys() if isinstance(d, datetime.date)]
        fs_dates.sort()
        fs_compl = fs_dates[:]
        fs_compl.append('complete')

        # Create the data table of observations.
        tbl_dict = {'obs': self.__obs_table(self.__all_obs)}
        # Construct aggregate data tables.
        # Note that some tables may not exist for every simulation.
        tbl_names = set(ns for fd in fs_compl for ns in fs[fd]['summary'])
        for n in tbl_names:
            in_fs = [fdate for fdate in fs_compl
                     if n in fs[fdate]['summary']]
            tbl_dict[n] = np.concatenate([fs[fdate]['summary'][n]
                                          for fdate in in_fs])

        # Attempt to avoid tracking times (not supported by h5py < 2.2).
        kwargs = {'track_times': False}

        def save_data(g, key, value):
            name = str(key).encode("utf-8")
            if isinstance(value, dict):
                sub_g = g.create_group(name)
                for sub_key, sub_value in sorted(value.items()):
                    save_data(sub_g, sub_key, sub_value)
            else:
                g.create_dataset(name, data=value, **kwargs)

        with h5py.File(filename, 'w') as f:
            # Record whether tracking times have been disabled.
            try:
                f.create_dataset('hdf5_track_times', data=False, **kwargs)
            except TypeError:
                # Cannot disable tracking times (h5py < 2.2).
                kwargs = {}
                f.create_dataset('hdf5_track_times', data=True, **kwargs)

            # Save the associated metadata, if any.
            if self.__metadata:
                meta_grp = f.create_group('meta')
                for k, v in sorted(self.__metadata.items()):
                    save_data(meta_grp, k, v)

            # Compress and checksum the data tables.
            kwargs['compression'] = 'gzip'
            kwargs['shuffle'] = True
            kwargs['fletcher32'] = True

            # Save the data tables.
            df_grp = f.create_group(self.__data_group)
            for tbl in tbl_dict:
                df_grp.create_dataset(tbl, data=tbl_dict[tbl], **kwargs)


class FakeRNG(object):
    """
    A fake random number generator whose methods return strings that describe
    each method call.
    """

    def __init__(self, prefix="random."):
        self.__prefix = prefix

    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        name = self.__prefix + name

        def log_call(*args, **kwargs):
            """Return a string representation of a method call."""
            # Ignore the 'size' keyword argument if its value is None.
            kw_iter = [(k, v) for (k, v) in kwargs.items()
                       if k != 'size' or v is not None]
            return "{}({})".format(
                name,
                ", ".join(
                    [repr(a) for a in args] +
                    ["{}={}".format(k, repr(v)) for k, v in kw_iter]
                ))

        return log_call


def metadata_priors(params):
    """
    Return a dictionary that describes the model parameter priors.

    Each key identifies a parameter (by name); the corresponding value is a
    string representation of the prior distribution, which is typically a
    ``numpy.random.RandomState`` method call.

    For example:

    .. code-block:: python

       {'alpha': "random.uniform(0.1, 1.0)"}
    """
    priors = params['prior'].items()
    rng = FakeRNG()
    return {k: str(v(rng)).encode("utf-8") for k, v in priors}


def filter_dict(values, ignore, encode_fn):
    """
    Recursively filter items from a dictionary, used to remove parameters from
    the metadata dictionary that, e.g., have no meaningful representation.

    :param values: The original dictionary.
    :param ignore: A dictionary that specifies which values to ignore.
    :param encode_fn: A function that encodes the remaining values (see
        :func:`.encode_value`).

    For example, to ignore ``['px_range']``,  ``['resample']['rnd']``, and
    ``'expect_fn'`` and ``'log_llhd_fn'`` for *every* observation system:

    .. code-block:: python

       ignore = {
           'px_range': None,
           'resample': {'rnd': None},
           # Note the use of ``None`` to match any key under 'obs'.
           'obs': {None: {'expect_fn': None, 'log_llhd_fn': None}}
       }
       filter_dict(params, ignore, encode_value)
    """
    retval = {}
    for k, v in values.items():
        if k in ignore and ignore[k] is None:
            # Ignore this parameter.
            continue
        elif k in ignore and isinstance(v, dict):
            # Recursively encode this dictionary, maybe ignoring values.
            retval[k] = filter_dict(v, ignore[k], encode_fn)
        elif None in ignore and isinstance(v, dict):
            # Recursively encode this dictionary, maybe ignoring values.
            retval[k] = filter_dict(v, ignore[None], encode_fn)
        elif isinstance(v, dict):
            # Recursively encode this dictionary without ignoring values.
            retval[k] = filter_dict(v, {}, encode_fn)
        else:
            retval[k] = encode_fn(v)
    return retval


def encode_value(value):
    """
    Encode values in a form suitable for serialisation in HDF5 files.

    * Integer values are converted to ``numpy.int32`` values.
    * Floating-point values and arrays retain their data type.
    * All other (i.e., non-numerical) values are converted to UTF-8 strings.
    """
    if isinstance(value, (int, np.int64)):
        # Avoid storing 64-bit integers since R doesn't support them.
        return np.int32(value)
    elif isinstance(value, (float, np.ndarray)):
        # Ensure that numerical values retain their data type.
        return value
    else:
        # Convert non-numerical values to UTF-8 strings.
        return str(value).encode("utf-8")


def metadata(params, pkgs=None):
    """
    Construct a metadata dictionary that documents the simulation parameters
    and system environment. Note that this should be generated at the
    **start** of the simulation, and that the git metadata will only be valid
    if the working directory is located within a git repository.

    :param params: The simulation parameters.
    :param pkgs: A dictionary that maps package names to modules that define
        appropriate ``__version__`` attributes, used to record the versions of
        additional relevant packages; see below for an example:

    By default, the versions of ``pypfilt``, ``h5py``, ``numpy`` and ``scipy``
    are recorded. The following example demonstrates how to also record the
    installed version of the ``epifx`` package:

    .. code-block:: python

       import epifx
       import pypfilt.summary
       params = ...
       metadata = pypfilt.summary.metadata(params, {'epifx': epifx})
    """

    # Import modules for extracting system-specific details.
    import platform
    import subprocess
    import sys

    # Import modules for extracting package versions.
    import scipy

    def cmd(args, all_lines=False, err_val=''):
        """
        Run a command and return the output. By default, only the first line
        is returned; set ``all_lines=True`` to receive all of the output as a
        list of strings. If the command returns a non-zero exit status, return
        ``err_val`` instead.
        """
        try:
            # With ``universal_newlines=True`` the output will be returned
            # as a string with all line endings converted to '\n'; without
            # this setting, Python 3 will return binary data, not text.
            lines = subprocess.check_output(args,
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=True)
        except subprocess.CalledProcessError:
            return err_val
        lines = [line for line in lines.split("\n") if line]
        if all_lines:
            return lines
        else:
            return lines[0]

    git_head = cmd(['git', 'rev-parse', 'HEAD'])
    git_branch = cmd(['git', 'symbolic-ref', '--short', 'HEAD'])
    git_mod_files = cmd(['git', 'ls-files', '--modified'], all_lines=True,
                        err_val=[])
    git_mod_files.sort()
    git_mod = len(git_mod_files) > 0

    def get_version(module):
        """Attempt to obtain the version of a Python module."""
        try:
            return module.__version__.encode("utf-8")
        except AttributeError:
            try:
                # Older versions of h5py store the version number here.
                return module.version.version.encode("utf-8")
            except AttributeError:
                return "unknown".encode("utf-8")

    # Ignore the following parameters; some will be replaced by better
    # descriptions (e.g., 'prior') and some should always be ignored because
    # they have no meaningful representation (e.g., 'log_llhd_fn').
    ignore_dict = {
        'prior': None,
        'log_llhd_fn': None,
        'px_range': None,
        'resample': {'rnd': None},
        'epifx': {'rnd': None},
        'obs': {None: {'expect_fn': None, 'log_llhd_fn': None}}
    }

    meta = {
        'package': {
            'python': platform.python_version().encode("utf-8"),
            'h5py': get_version(h5py),
            'pypfilt': get_version(pypfilt),
            'numpy': get_version(np),
            'scipy': get_version(scipy),
        },
        'sim': {
            'cmdline': str(" ".join(sys.argv)).encode("utf-8"),
        },
        'git': {
            'HEAD': git_head.encode("utf-8"),
            'branch': git_branch.encode("utf-8"),
            'modified': git_mod,
            'modified_files': [f.encode("utf-8") for f in git_mod_files],
        },
        'param': filter_dict(params, ignore_dict, encode_value),
        'prior': metadata_priors(params),
    }

    # Record the versions of user-specified packages (if any).
    if pkgs:
        for pkg in pkgs:
            meta['package'][pkg] = get_version(pkgs[pkg])

    # Record the fully qualified name of the infection model.
    meta['param']['model'] = "{}.{}".format(
        params['model'].__module__,
        params['model'].__name__).encode("utf-8")

    return meta
