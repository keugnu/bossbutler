import os
import logging
import sys

from logging import handlers

from pytube import YouTube


def setup_log():
    log = logging.getLogger('bossbutler')
    formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s:%(message)s')

    if not sys.stdin.isatty():
        handler = handlers.TimedRotatingFileHandler('/var/log/bossbutler/bossbutler.log', when='d')
        handler.setLevel(logging.INFO)
        log.setLevel(logging.INFO)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def download_yt(link=None):
    log = logging.getLogger('bossbutler')
    path = os.path.join(os.path.dirname(__file__), 'videos')
    yt = YouTube(link) if link else YouTube('https://www.youtube.com/watch?v=ZZ5LpwO-An4')
    if not os.path.exists(os.path.join(path, yt.title)):
        stream = yt.streams.first().download(output_path=path)
        log.info(f'Downloaded {yt.title} successfully.')
    return yt.watch_url, yt.title, stream


def find(path, name):
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
