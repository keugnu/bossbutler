import os
import logging

from pytube import YouTube


def setup_log():
    log = logging.getLogger('bossbutler')
    log.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler('/var/log/bossbutler.log', when='d')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def download_yt(link=None):
    if not link:
        yt = YouTube('https://www.youtube.com/watch?v=eh7lp9umG2I')
        return yt.title, yt.streams.first().download()
    yt = YouTube('https://www.youtube.com/watch?v=eh7lp9umG2I')
    return yt.title, yt.streams.first().download()


def find(path, name):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
