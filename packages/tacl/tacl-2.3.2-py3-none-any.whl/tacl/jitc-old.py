import csv
import io
import logging
import os

from bokeh.embed import components
from bokeh.charts import Bar
import pandas as pd

from . import constants
from .report import Report
from .statistics_report import StatisticsReport


class JITCProcessor:

    """Generate statistics to list texts from one corpus (referred to
    below as "Maybe" and defined in a catalogue file) in order of
    similarity to each text in that corpus. Takes into account a
    second corpus of texts (referred to below as "No" and defined in a
    catalogue file) that are similar to those in the first, but not in
    the way(s) that are the subject of the investigation.

    Given the two corpora, Maybe and No, the script performs the
    following actions:

    1. For each text Y in Maybe:
      1. Run an intersection between Y and No.
      2. For each text M in Maybe (excluding Y):
        1. Run an intersect between Y and M.
        2. Drop Y results.
        3. Run a supplied diff between results from [1.2.2] and
           results from [1.1].
        4. Get number of tokens in M.
      3. Rank and list texts in Maybe in descending order of the
         ratio, from [1.2.3], of matching tokens (n-gram size x count)
         to total tokens [1.2.5].
    4. Concatenate all results from [1.2.3] files.

    """

    def __init__ (self, store, corpus, catalogue, maybe_label, tokenizer,
                  output_dir):
        self._logger = logging.getLogger(__name__)
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
        report = Report(results, self._tokenizer)
        report.remove_label(self._no_label)
        if reduce:
            report.reduce()
        results = report.csv(fh)

    def process_maybe_text (self, yes_text, maybe_text, work_dir,
                            yn_results_path):
        if maybe_text == yes_text:
            return
        self._logger.debug(
            'Processing "maybe" text {} against "yes" text {}.'.format(
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
            stats_report = StatisticsReport(self._corpus, self._tokenizer,
                                            distinct_results_path)
            stats_report.generate_statistics()
            with open(stats_path, mode='w', encoding='utf-8', newline='') as fh:
                stats_report.csv(fh)
        with open(stats_path, encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                siglum = row[constants.SIGLUM_FIELDNAME]
                ratio = float(row[constants.PERCENTAGE_FIELDNAME])
                self._ratios[yes_text][(maybe_text, siglum)] = ratio

    def process_yes_text (self, yes_text, no_catalogue):
        self._logger.debug('Processing "maybe" text {} as "yes".'.format(
            yes_text))
        self._ratios[yes_text] = {}
        yes_work_dir = os.path.join(self._output_dir, yes_text)
        os.makedirs(yes_work_dir, exist_ok=True)
        results_path = os.path.join(yes_work_dir, 'intersect_with_no.csv')
        self._run_query(results_path, self._store.intersection, [no_catalogue])
        for maybe_text in self._maybe_texts:
            self.process_maybe_text(yes_text, maybe_text, yes_work_dir,
                                    results_path)

    def process_yes_texts (self):
        no_catalogue = {text: self._no_label for text in self._no_texts}
        data = {}
        graphs = {}
        for yes_text in self._maybe_texts:
            no_catalogue[yes_text] = self._maybe_label
            self.process_yes_text(yes_text, no_catalogue)
            no_catalogue.pop(yes_text)
            values = [ratio for ratio in self._ratios[yes_text].values()]
            index = pd.MultiIndex.from_tuples(list(self._ratios[yes_text].keys()),
                                              names=['text', 'siglum'])
            series = pd.Series(values, index=index)
            data[yes_text] = series
        df = pd.DataFrame(data)
        # Create a chart that has two bars per text on x-axis: one for
        # the percentage of that text that overlaps with the base
        # text, and one for the percentage of the base text that
        # overlaps with that text. A tooltip showing the values per
        # witness would be good.
        #
        # Create a stacked bar chart that shows the percentage the
        # content consisting of shared markers that aren't in the no
        # corpus, shared markers that are in the no corpus, and
        # unshared markers.
            #texts = list(set(index.get_level_values('text')))
            #ratios = []
            #for text in texts:
            #    ratio = series[text].max()
            #    ratios.append(ratio)
            #title = 'Shared markers with {}'.format(yes_text)
            #bar = Bar(ratios, texts, stacked=False, title=title,
            #          xlabel='Text', ylabel='% of text sharing markers')
            #graphs[yes_text + '-related'] = bar
        script, divs = components(graphs)

    def _run_query (self, path, query, query_args):
        if os.path.exists(path):
            return
        output_results = io.StringIO(newline='')
        query(*query_args, output_fh=output_results)
        with open(path, mode='w', encoding='utf-8', newline='') as fh:
            self._drop_no_label_results(output_results, fh)
