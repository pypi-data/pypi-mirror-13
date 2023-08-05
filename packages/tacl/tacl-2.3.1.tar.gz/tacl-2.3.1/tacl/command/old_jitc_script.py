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
import csv
import io
import logging
import os

import tacl
from tacl import constants


logger = logging.getLogger('jitc')


class Processor:

    def __init__ (self, store, corpus, catalogue, maybe_label, tokenizer,
                  output_dir):
        self._corpus = corpus
        self._maybe_label = maybe_label
        self._maybe_texts = [text for text, label in catalogue.items()
                             if label == maybe_label]
        self._no_texts = [text for text, label in catalogue.items()
                          if label != maybe_label]
        self._no_label = catalogue[self._no_texts[0]]
        self._output_dir = output_dir
        self._store = store
        self._tokenizer = tokenizer
        self._ratios = {}

    def _drop_no_label_results (self, results, fh, reduce=False):
        # Drop results associated with the 'no' label.
        results.seek(0)
        report = tacl.Report(results, self._tokenizer)
        report.remove_label(self._no_label)
        if reduce:
            report.reduce()
        results = report.csv(fh)

    def process_maybe_text (self, yes_text, maybe_text, work_dir,
                            yn_results_path):
        if maybe_text == yes_text:
            return
        logger.debug('Processing "maybe" text {} against "yes" text {}.'.format(
            maybe_text, yes_text))
        ym_results_path = os.path.join(
            work_dir, 'intersect_with_' + maybe_text + '.csv')
        catalogue = {yes_text: self._no_label,
                     maybe_text: self._maybe_label}
        self._run_query(ym_results_path, self._store.intersection, [catalogue])
        distinct_results_path = os.path.join(
            work_dir, 'distinct_' + maybe_text + '.csv')
        results = [yn_results_path, ym_results_path]
        labels = [self._no_label, self._maybe_label]
        self._run_query(distinct_results_path, self._store.diff_supplied,
                        [results, labels])
        stats_path = os.path.join(work_dir, 'stats_' + maybe_text + '.csv')
        if not os.path.exists(stats_path):
            stats_report = tacl.StatisticsReport(self._corpus, self._tokenizer,
                                                 distinct_results_path)
            stats_report.generate_statistics()
            with open(stats_path, mode='w', encoding='utf-8', newline='') as fh:
                stats_report.csv(fh)
        with open(stats_path, encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            ratio_data = {}
            for row in reader:
                ratio_data[row[constants.SIGLUM_FIELDNAME]] = row[constants.PERCENTAGE_FIELDNAME]
        self._ratios[yes_text].append((maybe_text, ratio_data))

    def process_yes_text (self, yes_text, no_catalogue):
        logger.debug('Processing "maybe" text {} as "yes".'.format(yes_text))
        self._ratios[yes_text] = []
        yes_work_dir = os.path.join(self._output_dir, yes_text)
        os.makedirs(yes_work_dir, exist_ok=True)
        results_path = os.path.join(yes_work_dir, 'intersect_with_no.csv')
        self._run_query(results_path, self._store.intersection, [no_catalogue])
        for maybe_text in self._maybe_texts:
            self.process_maybe_text(yes_text, maybe_text, yes_work_dir,
                                    results_path)

    def process_yes_texts (self):
        no_catalogue = {text: self._no_label for text in self._no_texts}
        for yes_text in self._maybe_texts:
            no_catalogue[yes_text] = self._maybe_label
            self.process_yes_text(yes_text, no_catalogue)
            no_catalogue.pop(yes_text)
        for texts in self._ratios.values():
            logger.debug(texts)
            texts.sort(key=lambda x: max([0] + [float(ratio) for ratio
                                          in x[1].values()]), reverse=True)
        with open(os.path.join(self._output_dir, 'groupings.txt'), mode='w') \
             as fh:
            for main_text, group_data in self._ratios.items():
                fh.write('{}:\n'.format(main_text))
                for related_text, related_text_data in group_data:
                    fh.write('    {} ('.format(related_text))
                    for witness, ratio in related_text_data.items():
                        fh.write('{}: {}; '.format(witness, ratio))
                    fh.write(')\n')
                fh.write('\n\n')

    def _run_query (self, path, query, query_args):
        if os.path.exists(path):
            return
        output_results = io.StringIO(newline='')
        query(*query_args, output_fh=output_results)
        with open(path, mode='w', encoding='utf-8', newline='') as fh:
            self._drop_no_label_results(output_results, fh)


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
    processor = Processor(store, corpus, catalogue, args.label, tokenizer,
                          output_dir)
    processor.process_yes_texts()

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
