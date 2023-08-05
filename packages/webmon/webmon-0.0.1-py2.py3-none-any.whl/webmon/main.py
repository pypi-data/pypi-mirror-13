import os, shutil, math
from datetime import datetime
from splinter import Browser
from PIL import Image
from PIL import ImageChops
from tqdm import tqdm
from itertools import combinations
    

URLS = [
    'http://www.mc706.com',
    'http://www.google.com',
    'http://www.reddit.com',
    'http://www.msn.com',
]

PHOTOS_DIR = 'screenshots'
SAMPLES = 10


def _clean_filename(name):
    return name.strip('http://').strip('/')


def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data) / n  # in Python 2 use sum(data)/float(n)


def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss


def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss / n  # the population variance
    return pvar ** 0.5


def rmsdiff(image1, image2):
    "Calculate the root-mean-square difference between two images"
    im1 = Image.open(image1)
    im2 = Image.open(image2)

    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * (idx ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    return rms


def directory_stdev(directory):
    """Calculates the average and standard deviation of images in a directory"""
    files = os.listdir(directory)[-SAMPLES:-1]
    rms = []
    pairs = combinations(files, 2)
    for pair in pairs:
        rms.append(rmsdiff(os.path.join(directory, pair[0]), os.path.join(directory, pair[1])))
    return mean(rms), pstdev(rms)


def run():
    created = []
    changed = []
    today = str(datetime.now())
    photos_dir = os.path.join(os.getcwd(), PHOTOS_DIR)
    print "Taking Screenshots"
    with Browser() as browser:
        for url in tqdm(URLS):
            browser.visit(url)
            screenshot = browser.screenshot('screenshot.png')
            if screenshot:
                dest = os.path.join(photos_dir, _clean_filename(url))
                if not os.path.exists(dest):
                    os.makedirs(dest)
                name = os.path.join(dest, 'screenshot-{0}.png'.format(today))
                created.append(name)
                shutil.move(screenshot, name)
    print "Calculating Differences"
    for directory in tqdm(os.listdir(photos_dir)):
        if os.path.isdir(os.path.join(photos_dir, directory)):
            for image in created:
                if directory in image:
                    active = image
            if active:
                files = os.listdir(os.path.join(photos_dir, directory))
                mean, std = directory_stdev(os.path.join(photos_dir, directory))
                current = rmsdiff(os.path.join(photos_dir, directory, files[-1]), active)
                if current < mean - std or current > mean + std:
                    changed.append((directory, current, mean, std))
    if changed:
        for change in changed:
            print "{0} has changed by more than the average, {1} !~ {2}+/-{3}".format(*change)
    else:
        print "None of the websites have changed"

