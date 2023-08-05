#!/usr/bin/env python

"""
Diego Martins de Siqueira
MIT License
DSDownload - DSDownload is a fully featured download library with focus on performance
"""

import Queue
import downloadthread
import sys
import argparse
from config import version, description

def DSDownload(urlList, workers = 5, folderPath = 'downloads'):
    queue = Queue.Queue()

    for url in urlList:
        queue.put(url)

    for i in range(workers):
        t = downloadthread.downloadthread(queue, folderPath)
        t.start()

    queue.join()

def main(argv=sys.argv[0]):
    description =   "DSDownload is a fully featured download library with focus on performance"
    parser = argparse.ArgumentParser(
        description = description)
    parser.add_argument("--version", action="version", version=version,
        help="Version Info")
    parser.add_argument("--workers", type=int, default=5, 
        help="Number of parallel downloads. The default is 5.")
    parser.add_argument("--output", type=str, default="downloads", 
        help="Output folder")
    parser.add_argument('urls', type=str, nargs='+',
        help='URLs to be downloaded')

    args = parser.parse_args()

    try:
        DSDownload(args.urls, args.workers, args.output)
        print 'All files were downloaded.'
    except KeyboardInterrupt:
        print 'Interrupt received, stopping downloads'

    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])