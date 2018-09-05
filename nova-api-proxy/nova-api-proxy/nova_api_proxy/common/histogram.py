#
# Copyright (c) 2015 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import math
import array
import datetime

from nova_api_proxy.common import log as logging

LOG = logging.getLogger(__name__)


class Histogram(object):
    """
    Histogram Object
    """
    def __init__(self, name, num_buckets):
        self._name = name
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
            bucket_idx = (sample_as_int-1).bit_length()

        if bucket_idx > self._num_buckets:
            bucket_idx = self._num_buckets-1

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

    def display_data(self):
        """
        Output the histogram to a log.
        """
        date_str = ""
        values_str = ""

        date_str += "  created-date: %s" % self._created_date
        if self._reset_date is not None:
            date_str += "  reset-date: %s" % self._reset_date

        values_str += "  total: %s" % self._num_samples

        if self._average_sample is not None:
            values_str += "  avg: %s" % self._average_sample

        if self._max_sample_date is not None:
            values_str += ("  max: %s (%s)" % (self._max_sample,
                                               self._max_sample_date))

        LOG.info("%s" % '-' * 120)
        LOG.info("Histogram: %s" % self._name)
        LOG.info("%s" % date_str)

        if "" != values_str:
            LOG.info("  %s" % values_str)

        for idx, bucket_value in enumerate(self._buckets):
            if 0 != bucket_value:
                LOG.info("    %03i [up to %03i secs]: %07i %s"
                          % (idx, math.pow(2, idx), bucket_value,
                             '*' * min(60, bucket_value)))
        LOG.info("%s" % '-' * 120)


_histograms = list()


def _find_histogram(name):
    """
    Lookup a histogram with a particular name
    """
    for histogram in _histograms:
        if name == histogram.name:
            return histogram
    return None


def add_histogram_data(name, sample):
    """
    Add a sample to a histogram
    """
    global _histograms

    histogram = _find_histogram(name)
    if histogram is None:
        histogram = Histogram(name, 8)
        _histograms.append(histogram)

    histogram.add_data(sample)


def reset_histogram_data(name=None):
    """
    Reset histogram data
    """
    if name is None:
        for histogram in _histograms:
            histogram.reset_data()
    else:
        histogram = _find_histogram(name)
        if histogram is not None:
            histogram.reset_data()


def display_histogram_data(name=None):
    """
    Display histogram data captured
    """
    if name is None:
        for histogram in _histograms:
            histogram.display_data()
    else:
        histogram = _find_histogram(name)
        if histogram is not None:
            histogram.display_data()
