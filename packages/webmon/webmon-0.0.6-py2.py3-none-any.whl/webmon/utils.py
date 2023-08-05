"""
Utilties files for webmon
"""
import math
from PIL import Image
from PIL import ImageChops
from tqdm import tqdm


def _clean_filename(name):
    return name.strip('http://').strip('/')


def _mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data) / n  # in Python 2 use sum(data)/float(n)


def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = _mean(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss


def _pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss / n  # the population variance
    return pvar ** 0.5


def _rmsdiff(image1, image2):
    "Calculate the root-mean-square difference between two images"
    im1 = Image.open(image1)
    im2 = Image.open(image2)

    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * (idx ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    return rms
