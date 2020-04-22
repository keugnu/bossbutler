import os
import logging
import sys

from logging import handlers

from pytube import YouTube


def setup_log():
    log = logging.getLogger('bossbutler')
    log.setLevel(logging.DEBUG)
    try:
        handler = handlers.TimedRotatingFileHandler('/var/log/bossbutler/bossbutler.log', when='d')
    except FileNotFoundError:
        handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def download_yt(link=None):
    log = logging.getLogger('bossbutler')
    path = os.path.join(os.path.dirname(__file__), 'videos')
    yt = YouTube(link) if link else YouTube('https://www.youtube.com/watch?v=ZZ5LpwO-An4')
    stream = yt.streams.first().download(output_path=path)
    log.info(f'Downloaded {yt.title} successfully.')
    return yt.watch_url, yt.title, stream


def find(path, name):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
