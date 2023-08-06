# sinsy-cli, Sinsy Command Line Interface
# Copyright (C) 2016  Olivier Jolly
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import argparse
import logging
import sys
import time

import bs4 as BeautifulSoup
import os
import requests
import tempfile

__date__ = '2016-02-16'
__updated__ = '2016-02-16'
__author__ = 'olivier@pcedev.com'

BASE_URL = "http://sinsy.sp.nitech.ac.jp/"
SINSY_TIMESTAMP = "sinsy-cli-timestamp"


def throttle_down():
    """read the timestamp and sleep to wait until the timestamp is reached"""
    try:
        with open(os.path.join(tempfile.gettempdir(), SINSY_TIMESTAMP), 'r') as f:
            next_request_timestamp = float(f.readline())

        wait_time = next_request_timestamp - time.time()
        if wait_time > 0:
            logging.debug("Sleeping %f second(s)", wait_time)
            time.sleep(wait_time)

    except:
        pass


def save_throttle_down_timestamp(synthesis_duration):
    with open(os.path.join(tempfile.gettempdir(), SINSY_TIMESTAMP), 'w') as f:
        f.write(repr(time.time() + synthesis_duration))


def send_score(score_filename, opts):
    """send a score to be processed by sinsy"""

    headers = {"User-Agent": "synsi-cli/0.5 (+https://gitlab.com/zeograd/sinsy-cli)"}

    request_data = {"LANG": "en",
                    "SPKR_LANG": opts.SPKR_LANG,
                    "SPKR": opts.SPKR,
                    "SYNALPHA": opts.SYNALPHA,
                    "VIBPOWER": opts.VIBPOWER,
                    "F0SHIFT": opts.F0SHIFT}

    throttle_down()

    logging.info("Synthetizing ...")

    synthesis_duration = - time.time()

    r = requests.post(BASE_URL + 'index.php', data=request_data,
                      files={'SYNSRC': (score_filename, open(score_filename, 'rb'), 'application')},
                      headers=headers)

    synthesis_duration += time.time()

    if r.status_code != 200:
        logging.error("Synthesis failed. HTTP error code %s", r.status_code)
        return
    else:
        logging.info("Synthesis finished in {0:.1f}s.".format(synthesis_duration))

    # preliminary timestamp saving
    save_throttle_down_timestamp(synthesis_duration)

    # with open("/tmp/temp_req.txt", "w") as f:
    #     f.write(r.text)
    # soup = BeautifulSoup.BeautifulSoup(open("/tmp/temp_req.txt"), "html.parser")

    soup = BeautifulSoup.BeautifulSoup(r.text, "html.parser")

    for result_tag in soup.find('audio').parent.parent.findAll('a'):

        if not opts.download_all and 'wav' not in result_tag.contents:
            continue

        raw_href = result_tag['href']
        url = BASE_URL + raw_href[2:]
        local_filename = os.path.splitext(score_filename)[0] + '.' + raw_href.split('/')[-1]

        logging.info("Saving {} to {}".format(url, local_filename))

        with open(local_filename, 'wb') as f:
            f.write(requests.get(url, headers=headers).content)

        logging.info("Saved")

    # final timestamp saving
    save_throttle_down_timestamp(synthesis_duration)


def main(argv=None):
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.5"
    program_build_date = "%s" % __updated__

    program_version_string = 'sinsy-cli %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''Interact with Sinsy'''
    program_license = "GPL v3+ 2016 Olivier Jolly"

    if argv is None:
        argv = sys.argv[1:]

    try:
        parser = argparse.ArgumentParser(epilog=program_longdesc,
                                         description=program_license)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                            default=False,
                            help="debug parsing [default: %(default)s]")
        parser.add_argument("-V", "--version", action="version", version=program_version_string)
        parser.add_argument("-a", "--all", dest="download_all", action="store_true",
                            help="Download all assets [wav + logs, defaults: download only wav]")

        parser.add_argument("-l", "--language", dest="SPKR_LANG", default="japanese",
                            choices=("japanese", "english", "mandarin"),
                            help="Vocal bank language [defaults: %(default)s]")
        parser.add_argument("-b", "--bank", dest="SPKR", default=1, type=int,
                            help="Vocal bank index for the given spoken language [from 0, max depends on language, default: %(default)s]")
        parser.add_argument("-g", "--gender", dest="SYNALPHA", default=0.55, type=float,
                            help="Gender parameter [between -0.8 and 0.8, default: %(default)s]")
        parser.add_argument("-v", "--vibrato", dest="VIBPOWER", default=1, type=float,
                            help="Vibrato intensity [between 0 and 2, default: %(default)s]")
        parser.add_argument("-p", "--pitch", dest="F0SHIFT", default=0, type=int,
                            help="Pitch shift [in half tones, between -24 and 24, default: %(default)s]")

        parser.add_argument("score_filename", help="input file in MusicXML format", nargs="+")

        # process options
        opts = parser.parse_args(argv)

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    if opts.debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    if not (-0.8 <= opts.SYNALPHA <= 0.8):
        logging.error("Invalid gender value (%s must be between -0.8 and 0.8)", opts.SYNALPHA)
        return 1

    if not (0 <= opts.VIBPOWER <= 2):
        logging.error("Invalid vibrato intensity (%s must be between 0 and 2)", opts.VIBPOWER)
        return 2

    if not (-24 <= opts.F0SHIFT <= 24):
        logging.error("Invalid pitch shift (%s must be between -24 and 24)", opts.F0SHIFT)
        return 3

    for score_filename in opts.score_filename:
        send_score(score_filename, opts)

    return 0


if __name__ == "__main__":
    sys.exit(main())
