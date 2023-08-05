import numpy as np
import Pypsy.signal

__author__ = "Brennon Bortz"


def calculate_sample_rate(signal):
    """
    Calculate the sample rate of a signal.

    Parameters
    ----------
    signal : Pypsy.signal.Signal
        The signal for which to calculate the sample rate

    Returns
    -------
    out : float
        The calculated sample rate

    Raises
    ------
    ValueError
        If the data vector of the signal is less than two samples in length

    Examples
    --------
    >>> time = np.array([0, 0.1, 0.2])
    >>> data = np.array([0., 0, 0])
    >>> signal = Pypsy.signal.Signal(data=data, time=time)
    >>> calculate_sample_rate(signal)
    10.0
    """
    if not signal.time.size > 1:
        raise ValueError('Sample rate is undefined for a signal of length < 2.')
    return 1./np.mean(np.diff(signal.time))


def resample_signal(signal, target_fs):
    """
    Resample the data vector of a signal at the specified sample rate using linear interpolation. This function
    modifies the signal in place.

    Parameters
    ----------
    signal : Pypsy.signal.Signal
        The signal to be resampled
    target_fs : float
        The target sample rate in Hertz

    Returns
    -------
    out : Pypsy.signal.Signal
        The resampled signal

    Examples
    --------
    >>> time = np.array([0., 0.1, 0.2])
    >>> data = np.array([-1., 0., 1.])
    >>> signal = Pypsy.signal.Signal(data, time)
    >>> resampled_signal = resample_signal(signal, 20)
    >>> np.sum(np.array([0, 0.05, 0.1, 0.15, 0.2]) - resampled_signal.time) < 0.001
    True
    >>> np.sum(np.array([-1, -0.5, 0, 0.5, 1]) - resampled_signal.data) < 0.001
    True

    >>> time = np.array([0, 0.04, 0.08, 0.12, 0.16])
    >>> data = np.array([-1., 0, 1, 0, -1])
    >>> signal = Pypsy.signal.Signal(data, time)
    >>> resampled_signal = resample_signal(signal, 25.0)
    >>> resampled_signal.time
    array([ 0.  ,  0.04,  0.08,  0.12,  0.16])
    """
    import sys

    # Calculate target sample period and duration of signal
    target_dt = 1. / target_fs
    start_time = signal.time[0]
    end_time = signal.time[-1]
    duration = end_time - start_time

    # Count number of sample periods in duration
    target_samples = np.int64(duration * target_fs)

    # Create timestamps
    target_timestamps = np.arange(0, target_samples)
    target_timestamps = (target_timestamps * target_dt) + signal.time[0]

    # Add a timestamp for final sample if it falls close enough to an actual timestamp
    if (end_time % target_dt) < sys.float_info.epsilon:
        target_timestamps = np.append(target_timestamps, [end_time])

    # Interpolate signal using linear interpolation
    target_signal = np.interp(target_timestamps, signal.time, signal.data)

    # Update signal vectors and return signal
    signal.time = target_timestamps
    signal.data = target_signal

    return signal


def smooth(data, window_width, windowtype='gauss'):
    """
    Smooth a signal by convolving it with one of a selection of window types.

    Parameters
    ----------
    data : array_like
        The signal to be smoothed
    window_width : int
        The width of the smoothing window in samples
    windowtype : str
        The type of window to use. Available choices are `gauss` (default), `hann` (a Hanning window), `expl`
        (exponential), and `mean` (moving average).

    Returns
    -------
    out : :py:class:`numpy.ndarray`
        A smoothed copy of ``data``

    Raises
    ------
    TypeError
        If ``data`` is not array-like (cannot be converted to a :py:class:`numpy.ndarray` using
        :py:meth:`numpy.array()`)
    """

    from scipy.stats import norm
    from scipy.signal import convolve

    data = np.asarray(data)

    # If the window width isn't > 1, just return the original data
    if window_width < 1.:
        return data

    # Pad data to remove border errors
    data = np.concatenate([[data[0]], data, [data[-1]]])

    # Force an even window length
    window_width = np.floor(window_width / 2) * 2

    # Construct the window
    window = None

    # Hanning window
    if windowtype == 'hann':
        window = 0.5 * (1 - np.cos(2 * np.pi * np.linspace(0, 1, window_width)))

    # Moving average
    elif windowtype == 'mean':
        window = np.ones(window_width)

    # Gaussian window
    elif windowtype == 'gauss':
        window = norm.pdf(np.arange(1, window_width + 1), window_width / 2. + 1, window_width / 8.)

    # Exponential window
    elif windowtype == 'expl':
        head = np.zeros(np.int64(window_width / 2))
        tail = np.exp(-4. * np.linspace(0, 1, num=head.size))
        window = np.concatenate([head, tail])

    else:
        raise ValueError('Unknown window type %r' % windowtype)

    # Normalize window
    window = window / np.sum(window)

    # Extend first and last values in data by half a window width on either side
    head = np.ones(np.int64(window_width / 2)) * data[0]
    tail = np.ones(np.int64(window_width / 2)) * data[-1]
    data_extended = np.concatenate([head, data, tail])

    # Convolute data with window
    smoothed_data_extended = convolve(data_extended, window)

    # Trim to data length
    return smoothed_data_extended[np.int64(window_width) + 1:-np.int64(window_width)]


def closest_time_index(time, target_time):
    """
    From a vector of monotonically-increasing timestamps, find the index of the timestamp closest to a target timestamp.

    Parameters
    ----------
    time : array_like
        The vector of timestamps
    time0 : float
        The target timestamp

    Returns
    -------
    index : int
        The index of the timestamp in ``time`` that is closest to ``target_time``
    closest_time : float
        The timestamp in ``time`` at this index

    Raises
    ------
    TypeError
        If ``time`` is not array-like (cannot be converted to a :py:class:`numpy.ndarray` using
        :py:meth:`numpy.array()`)

    Examples
    --------
    >>> timestamps = np.array([0, 0.1, 0.2, 0.3])
    >>> index, time = closest_time_index(timestamps, 0.1)
    >>> index
    1
    >>> time == timestamps[index]
    True
    >>> index, time = closest_time_index(timestamps, 0.101)
    >>> index
    1
    >>> time == timestamps[index]
    True
    >>> index, time = closest_time_index(timestamps, 0.1501)
    >>> index
    2
    >>> time == timestamps[index]
    True
    >>> index, time = closest_time_index(timestamps, 0.5)
    >>> index
    3
    >>> time == timestamps[index]
    True
    >>> index, time = closest_time_index(timestamps, -0.1)
    >>> index
    0
    >>> time == timestamps[index]
    True
    >>> timestamps = np.array([-0.1, 0, 0.1])
    >>> index, time = closest_time_index(timestamps, -0.1)
    >>> index
    0
    >>> time == timestamps[index]
    True
    >>> timestamps = np.array([])
    >>> index, time = closest_time_index(timestamps, 2)
    >>> index == None
    True
    >>> time == None
    True
    """

    time = np.asarray(time)

    # Return (None, None) if an empty timestamp vector was passed
    if time.size == 0:
        return None, None

    # Find indices in time that are greater than or equal to the target time
    index = np.nonzero(time >= target_time)[0]

    # If was at least one such index
    if index.size > 0:

        # Set idx to the first of these
        index = np.min(index);

        # Grab the value of time at this index
        closest_time = time[index]

        # If the previous index was closer in time, use it as the index and adjusted time
        if closest_time != time[0]:
            closest_earlier_time = time[index-1]
            if np.abs(target_time - closest_earlier_time) < np.abs(target_time - closest_time):
                index = index - 1
                closest_time = closest_earlier_time

    # Otherwise, take the last index that is less than the target time
    else:
        index = np.nonzero(time <= target_time)[0]
        index = np.max(index)
        closest_time = time[index]

    # Return the index in the original time vector and the time at this index
    return index, closest_time


def subrange_indices(time, start_time, end_time):
    """
    Given start and end times ``start_time`` and ``end_time``, find the indices of the timestamps in ``time`` that are
    within these times.

    Parameters
    ----------
    t : array_like
        A vector of monotonically-increasing timestamps
    t1 : float
        The start time
    t2 : float
        The end time

    Returns
    -------
    out : numpy.ndarray
        The subrange of indices of those timestamps in ``time`` that begins with the time closest to ``start_time`` and
        ends with the time closest to ``start_time``

    Examples
    --------
    >>> times = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    >>> subrange_indices(times, 0, 1)
    array([0, 1, 2, 3, 4, 5])
    >>> subrange_indices(times, 0.05, 0.1)
    array([1])
    >>> subrange_indices(times, 0.1, 0.15)
    array([1])
    >>> subrange_indices(times, 0.05, 0.25)
    array([1, 2, 3])
    >>> subrange_indices(times, 0.45, 0.5)
    array([5])
    """

    # Get the closest indices to the start and stop times (start_time and end_time)
    start_index, _ = closest_time_index(time, start_time)
    end_index, _ = closest_time_index(time, end_time)

    # If there are overlapping timestamps between these two vectors, return a vector of indices into time from
    # start_time up to end_time
    if start_index is not None and end_index is not None:
        indices = np.arange(start_index, end_index + 1)

    # Otherwise, return an empty vector
    else:
        indices = np.array([])

    return indices


def nonzero_portion(data, threshold, exponent, sample_rate):
    """
    Compute the portion of ``data`` that is nonzero. This portion is computed with

    .. math::

        \\frac{\\sum z^f}{d}

    where :math:`z` is the duration of ``data`` where the absolute amplitude is greater than ``threshold``, :math:`f` is
    ``exponent``, and :math:`d` is the total duration of ``data``.

    Parameters
    ----------
    data : array_like
        The vector for which ``portion`` should be computed
    crit : float
        The criterion threshold
    fac : float
        The exponent in the above formula
    sr : float
        The sample rate of ``data``

    Returns
    -------
    out : float
        The result of the above formula

    Examples
    --------
    >>> result = nonzero_portion(np.array([1, 1, 0.1, 0.3, 4, 5, 6, 1, 7, 8, 1, 1, 0.2]), 0.1, 1, 5)
    >>> np.abs(result - 0.92) < 0.005
    True
    """

    # Start with an empty array of non-zero segment lengths
    nonzero_sample_counts = np.array([])

    counter = 0
    data_length = data.size

    # Iterate over data
    for i in range(data.size):

        # If absolute value of sample is greater than criterion
        if np.abs(data[i]) > threshold:

            # Increment counter
            counter = counter + 1

        else:

            # If counter is greater than zero
            if counter > 0:

                # Append counter value to nonzero_sample_counts vector
                nonzero_sample_counts = np.concatenate([nonzero_sample_counts, [counter]])

                # Reset counter
                counter = 0

    # If counter is greater than zero
    if counter > 0:

        # Append counter value to nonzero_sample_counts vector
        nonzero_sample_counts = np.concatenate([nonzero_sample_counts, [counter]])

    # If nonzero_sample_counts is non-empty
    if nonzero_sample_counts.size > 0:

        # Compute portion as 'nonzero time (sec)'^exponent / 'total time'
        portion = np.sum((nonzero_sample_counts / sample_rate) ** exponent) / (data_length / sample_rate);

    else:

        # Otherwise, return 0
        portion = 0

    return portion

