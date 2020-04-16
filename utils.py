import os

from pytube import YouTube


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
