#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function
from bs4 import BeautifulSoup
import youtube_dl
import grequests
import argparse
import json
import time
from os import path, listdir, rmdir
from shutil import move
import re

config_path = path.join(
    path.dirname(path.abspath(__file__)),
    'data', 'yt-songs.json'
)

parser = argparse.ArgumentParser(
    description=('YT-Songs searches, downloads and normalizes'
                 ' the titles of a list of songs from youtube'
                 ' using youtube-dl.')
)

parser.add_argument('FILE')
parser.add_argument('PATH')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Print youtube-dl output.')
args = parser.parse_args()

with open(config_path) as config_file:
    config_json = json.load(config_file)
    temp = path.expanduser(config_json['temp_path'])
    perm = path.expanduser(args.FILE)
    ydl_opts = config_json['ydl_opts']
    name = config_json['name_tmpl']


def main():
    start_time = time.time()
    count = [0, 0]

    class Logger():
        def debug(self, msg):
            if args.verbose:
                print(msg)

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

    def norm_title(title):
        replaces = (
            ('(\{|\[)', '('),
            ('(\}|\])', ')'),
            ('\((?:official(?:(?: music| lyric)? video)?'
             '|(?:v[ií]deo(?:clipe)? )?oficial|'
             'hd|(?:v[ií]deo)?clip(?: officiel)?|lyric)\)', '')
        )

        for replace in replaces:
            title = re.sub(replace[0], replace[1], title, flags=re.IGNORECASE)

        return title

    def count_status(download):
        if download['status'] == 'finished':
            count[0] += 1
            count[1] += 1
        elif download['status'] == 'error':
            count[1] += 1

    def download_hook(response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.findAll("a", rel="spf-prefetch")

        if not links:
            print('* Not found')
        else:
            url = 'https://www.youtube.com' + links[0].get('href')
            print('* Calling youtube-dl on "' + url + '"')

            ydl_opts['logger'] = Logger()
            ydl_opts['outtmpl'] = path.join(temp, name)
            ydl_opts['progress_hooks'] = [count_status]
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

    def search(title, hook):
        count[1] += 1
        print('* Searching: "' + title + '"')
        return grequests.get(
                    'https://www.youtube.com/results?search_query=' + title,
                    hooks={'response': hook}
               )

    searches = (
        search(title, download_hook)
        for title in [line.rstrip('\n') for line in open(perm)]
    )

    grequests.map(searches)
    print('-' * 60)

    if not count[0]:
        print('No songs downloaded')
    else:
        print(str(count[0]) + '/' + str(count[1]),
              'songs downloaded successfully')

        for entry in listdir(temp):
            move(
                path.join(temp, entry),
                path.join(path.expanduser(args.PATH), norm_title(entry))
            )
        print('Files moved and normalized successfully')

        rmdir(temp)
        print('(' + str(round(time.time() - start_time)) + ' seconds)')

if __name__ == '__main__':
    main()
