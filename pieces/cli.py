#
# pieces - An experimental BitTorrent client
#
# Copyright 2016 markus.eliasson@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import asyncio
import signal
import logging
import time

from concurrent.futures import CancelledError

from pieces.torrent import Torrent
from pieces.client import TorrentClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('torrent',
                        help='the .torrent to download')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose output')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    client = TorrentClient(Torrent(args.torrent))
    task = loop.create_task(client.start())

    piece_manager=None
    def signal_handler(*_):
        logging.info('Exiting, please wait until everything is shutdown...')
        piece_manager = client.piece_manager
        # client.stop()
        print("Pause")
        time.sleep(15)
        # slep()
        # task.cancel()
        task.done()
        loop.stop()

        print("Resuming after 2.4 seconds.")
        # client.resume()
        # loop.create_task(client.start())
        # piece_manager = client.resume()
        # loop2 = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop2)
        # client2 = TorrentClient(Torrent(args.torrent),piece_manager)
        # task2 = loop2.create_task(client2.start())

    signal.signal(signal.SIGINT, signal_handler)

    try:
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)
        client2 = TorrentClient(Torrent(args.torrent), piece_manager)
        task2 = loop2.create_task(client2.start())
        loop2.run_until_complete(task2)
    except CancelledError:
        logging.warning('Event loop was canceled')
