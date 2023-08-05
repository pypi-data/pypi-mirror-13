import os, shutil, math
from datetime import datetime
from splinter import Browser
from itertools import combinations

from webmon.utils import _clean_filename, _rmsdiff

URLS = [
    'http://www.mc706.com',
    'http://www.google.com',
    'http://www.reddit.com',
    'http://www.msn.com',
]

PHOTOS_DIR = 'screenshots'
SAMPLES = 10


def directory_stdev(directory):
    """Calculates the average and standard deviation of images in a directory"""
    files = os.listdir(directory)[-SAMPLES:-1]
    rms = []
    pairs = combinations(files, 2)
    for pair in pairs:
        rms.append(_rmsdiff(os.path.join(directory, pair[0]), os.path.join(directory, pair[1])))
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
                current = _rmsdiff(os.path.join(photos_dir, directory, files[-1]), active)
                if current < mean - std or current > mean + std:
                    changed.append((directory, current, mean, std))
    if changed:
        for change in changed:
            print "{0} has changed by more than the average, {1} !~ {2}+/-{3}".format(*change)
    else:
        print "None of the websites have changed"
