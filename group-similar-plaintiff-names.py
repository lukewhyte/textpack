import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix


class ColumnValueGrouper():
    def __init__(self, csv_path, column_to_group, export_path, match_threshold=0.8, ngram_length=3):
        self._df = pd.read_csv(csv_path)
        self._column = column_to_group
        self._match_threshold = match_threshold
        self._ngram_length = ngram_length
        self._export_path = export_path
        self._group_lookup = {}

    def _ngrams_analyzer(self, string):
        string = re.sub(r'[,-./]', r'', string)
        ngrams = zip(*[string[i:] for i in range(self._ngram_length)])
        return [''.join(ngram) for ngram in ngrams]

    def _get_tf_idf_matrix(self):
        vectorizer = TfidfVectorizer(analyzer=self._ngrams_analyzer)
        return vectorizer.fit_transform(self._df[self._column].unique())

    def _get_cosine_matrix(self):
        tf_idf_matrix = self._get_tf_idf_matrix()
        return cosine_similarity(tf_idf_matrix, dense_output=False)

    def _vals_are_siblings(self, y, x, prox):
        return (x != y) and (prox > self._match_threshold)

    def _find_group(self, y, x):
        if y in self._group_lookup:
            return self._group_lookup[y]
        elif x in self._group_lookup:
            return self._group_lookup[x]
        else:
            return None

    def _add_vals_to_lookup(self, group, y, x):
        self._group_lookup[y] = group
        self._group_lookup[x] = group

    def _add_pair_to_lookup(self, row, col, data):
        if self._vals_are_siblings(row, col, data):
            group = self._find_group(row, col)
            if group is not None:
                self._add_vals_to_lookup(group, row, col)
            else:
                self._add_vals_to_lookup(row, row, col)

    def build_group_lookup(self):
        print('Building the TF-IDF, Cosine & Coord matrices...')
        coord_matrix = self._get_cosine_matrix().tocoo()

        print('Building the group lookup. This could take a little while...')
        vals = self._df[self._column].unique()
        for row, col, data in zip(coord_matrix.row, coord_matrix.col, coord_matrix.data):
            self._add_pair_to_lookup(vals[row], vals[col], data)

    def add_grouped_column_to_data(self, column_name='Group'):
        print('Adding grouped columns to data frame...')
        self._df[column_name] = self._df[self._column].map(self._group_lookup).fillna(self._df[self._column])

    def export_csv(self):
        self._df.to_csv(self._export_path)


eviction_grouper = ColumnValueGrouper(
    csv_path='./data/evictions.csv',
    column_to_group='Plaintiff',
    export_path='./data/evictions-grouped.csv'
)

eviction_grouper.build_group_lookup()
eviction_grouper.add_grouped_column_to_data()
eviction_grouper.export_csv()
