import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sparse_dot_topn import awesome_cossim_topn


class ColumnCleaner():
    def __init__(self, df, column_to_group, match_threshold=0.75, ngram_length=3):
        self.df = df
        self.group_lookup = {}
        self._column = column_to_group
        self._match_threshold = match_threshold
        self._ngram_length = ngram_length

    def _ngrams_analyzer(self, string):
        string = re.sub(r'[,-./]', r'', string)
        ngrams = zip(*[string[i:] for i in range(self._ngram_length)])
        return [''.join(ngram) for ngram in ngrams]

    def _get_tf_idf_matrix(self, vals):
        vectorizer = TfidfVectorizer(analyzer=self._ngrams_analyzer)
        return vectorizer.fit_transform(vals)

    def _get_cosine_matrix(self, vals):
        tf_idf_matrix = self._get_tf_idf_matrix(vals)
        return awesome_cossim_topn(tf_idf_matrix, tf_idf_matrix.transpose(), vals.size, self._match_threshold)

    def _find_group(self, y, x):
        if y in self.group_lookup:
            return self.group_lookup[y]
        elif x in self.group_lookup:
            return self.group_lookup[x]
        else:
            return None

    def _add_vals_to_lookup(self, group, y, x):
        self.group_lookup[y] = group
        self.group_lookup[x] = group

    def _add_pair_to_lookup(self, row, col):
        group = self._find_group(row, col)
        if group is not None:
            self._add_vals_to_lookup(group, row, col)
        else:
            self._add_vals_to_lookup(row, row, col)

    def build_group_lookup(self):
        try:
            vals = self.df[self._column].unique()
        except ValueError:
            print('Is the stated column in your dataset?')

        print('Building the TF-IDF, Cosine & Coord matrices...')
        coord_matrix = self._get_cosine_matrix(vals).tocoo()

        print('Building the group lookup...')
        for row, col in zip(coord_matrix.row, coord_matrix.col):
            if row != col:
                self._add_pair_to_lookup(vals[row], vals[col])

    def add_grouped_column_to_data(self, column_name='Group'):
        print('Adding grouped columns to data frame...')
        self.df[column_name] = self.df[self._column].map(self.group_lookup).fillna(self.df[self._column])

    def export_json(self, export_path=None):
        self.df.to_json(export_path)

    def export_csv(self, export_path=None):
        self.df.to_csv(export_path)


def read_df(df, column_to_group, match_threshold=0.75, ngram_length=3):
    return ColumnCleaner(df, column_to_group, match_threshold, ngram_length)


def read_csv(csv_path, column_to_group, match_threshold=0.75, ngram_length=3):
    return ColumnCleaner(pd.read_csv(csv_path), column_to_group, match_threshold, ngram_length)


def read_json(csv_path, column_to_group, match_threshold=0.75, ngram_length=3):
    return ColumnCleaner(pd.read_json(csv_path), column_to_group, match_threshold, ngram_length)
