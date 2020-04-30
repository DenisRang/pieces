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
import pickle

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

    piece_manager = None
    try:
        with open('piece_manager.pickle', 'rb') as f:
            piece_manager = pickle.load(f)
    except:
        pass

    client = TorrentClient(Torrent(args.torrent), piece_manager)

    task = loop.create_task(client.start())

    def signal_handler(*_):
        print("Pausing and closing all connections")
        client.stop()
        task.cancel()
        piece_manager = client.piece_manager
        with open('piece_manager.pickle', 'wb') as f:
            pickle.dump(piece_manager, f)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # new_loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(new_loop)
        # new_client = TorrentClient(Torrent(args.torrent), piece_manager)
        # new_task = new_loop.create_task(new_client.start())
        loop.run_until_complete(task)
    except CancelledError:
        logging.warning('Event loop was canceled')
