"""Command-line script to list texts from one corpus (referred to
below as "Maybe" and defined in a catalogue file) in order of
similarity to each text in that corpus. Takes into account a second
corpus of texts (referred to below as "No" and defined in a catalogue
file) that are similar to those in the first, but not in the way(s)
that are the subject of the investigation.

Given the two corpora, Maybe and No, the script performs the following
actions:

1. For each text Y in Maybe:
  1. Run an intersection between Y and No.
  2. For each text M in Maybe (excluding Y):
    1. Run an intersect between Y and M.
    2. Drop Y results.
    3. Run a supplied diff between results from [1.2.2] and results from [1.1].
    4. Drop results with fewer than 5 matches.
    5. Get number of tokens in M.
  3. Rank and list texts in Maybe in descending order of the ratio, from
[1.2.4], of matching tokens (n-gram size x count) to total tokens
[1.2.5].
  4. Concatenate all results from [1.2.4] files.

"""

import argparse
import logging
import os

import tacl
from tacl import constants


logger = logging.getLogger('tacl')


def main ():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        configure_logging(args.verbose)
    store = get_data_store(args)
    corpus = get_corpus(args)
    catalogue = get_catalogue(args)
    tokenizer = get_tokenizer(args)
    check_catalogue(catalogue, args.label)
    store.validate(corpus, catalogue)
    output_dir = os.path.abspath(args.output)
    if os.path.exists(output_dir):
        logger.warning('Output directory already exists; any results therein '
                       'will be reused rather than regenerated.')
    os.makedirs(output_dir, exist_ok=True)
    processor = tacl.JITCProcessor(store, corpus, catalogue, args.label,
                                   tokenizer, output_dir)
    processor.process()

def check_catalogue (catalogue, label):
    """Raise an exception if `catalogue` contains more than two labels, or
    if `label` is not used in the `catalogue`."""
    labels = set(catalogue.values())
    if label not in labels:
        raise Exception(
            'The specified label "{}" must be present in the catalogue.')
    elif len(labels) != 2:
        raise Exception('The catalogue must specify only two labels.')

def configure_logging (verbose):
    """Configures the logging used."""
    if not verbose:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def generate_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--label', required=True)
    parser.add_argument('-m', '--memory', action='store_true',
                        help=constants.DB_MEMORY_HELP)
    parser.add_argument('-r', '--ram', default=3, help=constants.DB_RAM_HELP,
                        type=int)
    parser.add_argument('-t', '--tokenizer', choices=constants.TOKENIZER_CHOICES,
                        default=constants.TOKENIZER_CHOICE_CBETA,
                        help=constants.DB_TOKENIZER_HELP)
    parser.add_argument('-v', '--verbose', action='count',
                        help=constants.VERBOSE_HELP)
    parser.add_argument('db', help=constants.DB_DATABASE_HELP,
                        metavar='DATABASE')
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')
    parser.add_argument('catalogue', help=constants.CATALOGUE_CATALOGUE_HELP,
                        metavar='CATALOGUE')
    parser.add_argument('output', help='Directory to output results into')
    return parser

def get_corpus (args):
    """Returns a `tacl.Corpus`."""
    tokenizer = get_tokenizer(args)
    return tacl.Corpus(args.corpus, tokenizer)

def get_catalogue (args):
    """Returns a `tacl.Catalogue`."""
    catalogue = tacl.Catalogue()
    catalogue.load(args.catalogue)
    return catalogue

def get_data_store (args):
    """Returns a `tacl.DataStore`."""
    return tacl.DataStore(args.db, args.memory, args.ram)

def get_tokenizer (args):
    return tacl.Tokenizer(*constants.TOKENIZERS[args.tokenizer])
