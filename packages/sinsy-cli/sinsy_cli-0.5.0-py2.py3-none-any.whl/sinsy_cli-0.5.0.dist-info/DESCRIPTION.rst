sinsy-cli
=========

**sinsy-cli** is a command line interface to the Synsi web service ( http://sinsy.jp ).
**Sinsy** is an open source vocal synthetizer with a similar goal to vocaloid, cevio, alter/ego, acantorix, ...

**sinsy-cli** will send a lyric annotated score in *MusicXML* format and retrieve the vocal synthesis result in wav format
(and accessorily other synthesis log assets).

All online parameters found on the web service can be accessed via command line arguments ::

     usage: sinsy-cli [-h] [-d] [-V] [-a] [-l {japanese,english,mandarin}]
                     [-b SPKR] [-g SYNALPHA] [-v VIBPOWER] [-p F0SHIFT]
                     score_filename [score_filename ...]

    GPL v3+ 2016 Olivier Jolly

    positional arguments:
      score_filename        input file in MusicXML format

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           debug parsing [default: False]
      -V, --version         show program's version number and exit
      -a, --all             Download all assets [wav + logs, defaults: download
                            only wav]
      -l {japanese,english,mandarin}, --language {japanese,english,mandarin}
                            Vocal bank language [defaults: japanese]
      -b SPKR, --bank SPKR  Vocal bank index for the given spoken language [from
                            0, max depends on language, default: 1]
      -g SYNALPHA, --gender SYNALPHA
                            Gender parameter [between -0.8 and 0.8, default: 0.55]
      -v VIBPOWER, --vibrato VIBPOWER
                            Vibrato intensity [between 0 and 2, default: 1]
      -p F0SHIFT, --pitch F0SHIFT
                            Pitch shift [in half tones, between -24 and 24,
                            default: 0]

    Interact with Sinsy

Installation
------------

**sinsy-cli** will be installable from PyPI with a single pip command::

    pip install sinsy-cli

Alternatively, **sinsy-cli** can be run directly from sources after a git pull (recommended if you want to tweak
or read the source)::

    git clone https://gitlab.com/zeograd/sinsy-cli.git
    cd sinsy-cli && python setup.py install

or directly from a git repository generated tarball::

    pip install git+https://gitlab.com/zeograd/sinsy-cli.git



