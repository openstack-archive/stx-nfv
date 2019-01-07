#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import array
import datetime
import math

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.histogram')


class Histogram(object):
    """
    Histogram Object
    """
    def __init__(self, name, num_buckets, units):
        self._name = name
        self._units = units
        self._num_buckets = num_buckets
        self._created_date = datetime.datetime.now()
        self._reset_date = self._created_date
        self._sample_total = 0
        self._num_samples = 0
        self._average_sample = None
        self._max_sample = -1
        self._max_sample_date = None
        self._buckets = array.array("L", [0] * num_buckets)

    @property
    def name(self):
        """
        Returns the name of the histogram
        """
        return self._name

    def add_data(self, sample):
        """
        Convert data given to the nearest power of two.
        """
        sample_as_int = int(sample)
        if 0 == sample_as_int:
            bucket_idx = sample_as_int.bit_length()
        else:
            bucket_idx = (sample_as_int - 1).bit_length()

        if bucket_idx > self._num_buckets:
            bucket_idx = self._num_buckets - 1

        if sample_as_int > self._max_sample:
            self._max_sample = sample_as_int
            self._max_sample_date = datetime.datetime.now()

        self._sample_total += sample_as_int
        self._num_samples += 1
        self._average_sample = (self._sample_total / self._num_samples)

        self._buckets[bucket_idx] += 1

    def reset_data(self):
        """
        Clear out the collected samples.
        """
        self._reset_date = datetime.datetime.now()
        self._sample_total = 0
        self._num_samples = 0
        self._average_sample = None
        self._max_sample = -1
        self._max_sample_date = None
        for idx, _ in enumerate(self._buckets):
            self._buckets[idx] = 0

    @staticmethod
    def _scale_sample(scale_min, scale_max, sample_min, sample_max, sample):
        """
        Normalize sample to be compared with other samples
        """
        if scale_min == scale_max:
            return sample

        if sample_min == sample_max:
            return sample

        return ((((scale_max - scale_min) * (sample - sample_min)) /
                 (sample_max - sample_min)) + sample_max)

    def display_data(self, pretty_format=True):
        """
        Output the histogram to a log.
        """
        date_str = ""
        values_str = ""

        if pretty_format:
            date_str += "  created-date: %s" % self._created_date
            if self._reset_date is not None:
                date_str += "  reset-date: %s" % self._reset_date

            values_str += "  total: %s" % self._num_samples

            if self._average_sample is not None:
                values_str += "  avg: %s" % self._average_sample

            if self._max_sample_date is not None:
                values_str += ("  max: %s (%s)" % (self._max_sample,
                                                   self._max_sample_date))

            DLOG.info("%s" % '-' * 120)

        DLOG.info("Histogram: %s" % self._name)

        if "" != date_str:
            DLOG.info("%s" % date_str)

        if "" != values_str:
            DLOG.info("  %s" % values_str)

        for idx, bucket_value in enumerate(self._buckets):
            if 0 != bucket_value:
                if pretty_format:
                    scaled_bucket_value \
                        = self._scale_sample(0, 60, 0, self._max_sample,
                                             bucket_value)

                    DLOG.info("    %03i [up to %03i %s]: %07i %s"
                              % (idx, math.pow(2, idx), self._units, bucket_value,
                                 '*' * min(60, scaled_bucket_value)))
                else:
                    DLOG.info("    %03i [up to %03i %s]: %07i"
                              % (idx, math.pow(2, idx), self._units, bucket_value))

        if pretty_format:
            DLOG.info("%s" % '-' * 120)


_histograms = dict()


def _find_histogram(name):
    """
    Lookup a histogram with a particular name
    """
    if name in _histograms:
        return _histograms[name]
    return None


def add_histogram_data(name, sample, units):
    """
    Add a sample to a histogram
    """
    global _histograms

    histogram = _find_histogram(name)
    if histogram is None:
        histogram = Histogram(name, 16, units)
        _histograms[name] = histogram

    histogram.add_data(sample)


def reset_histogram_data(name=None):
    """
    Reset histogram data
    """
    if name is None:
        for histogram in _histograms.values():
            histogram.reset_data()
    else:
        histogram = _find_histogram(name)
        if histogram is not None:
            histogram.reset_data()


def display_histogram_data(name=None, pretty_format=True):
    """
    Display histogram data captured
    """
    if name is None:
        for histogram in _histograms.values():
            histogram.display_data(pretty_format)
    else:
        histogram = _find_histogram(name)
        if histogram is not None:
            histogram.display_data(pretty_format)
