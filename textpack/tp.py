import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sparse_dot_topn import awesome_cossim_topn


class TextPack():
    def __init__(self, df, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3):
        self.df = df
        self.group_lookup = {}
        self._column = self._get_column(columns_to_group)
        self._match_threshold = match_threshold
        self._ngram_remove = ngram_remove
        self._ngram_length = ngram_length

    def _get_column(self, columns_to_group):
        if ''.join(columns_to_group) in self.df.columns:
            return ''.join(columns_to_group)
        else:
            self.df['textpackGrouper'] = self.df[columns_to_group.pop(0)].astype(str).str.cat(self.df[columns_to_group].astype(str))
            return 'textpackGrouper'

    def _ngrams_analyzer(self, string):
        string = re.sub(self._ngram_remove, r'', string)
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

    def set_ngram_remove(self, ngram_remove):
        self._ngram_remove = ngram_remove

    def set_ngram_length(self, ngram_length):
        self._ngram_length = ngram_length

    def set_match_threshold(self, match_threshold):
        self._match_threshold = match_threshold

    def build_group_lookup(self):
        vals = self.df[self._column].unique().astype('U')

        print('Building the TF-IDF, Cosine & Coord matrices...')
        coord_matrix = self._get_cosine_matrix(vals).tocoo()

        print('Building the group lookup...')
        for row, col in zip(coord_matrix.row, coord_matrix.col):
            if row != col:
                self._add_pair_to_lookup(vals[row], vals[col])

    def add_grouped_column_to_data(self, column_name='Group'):
        print('Adding grouped columns to data frame...')
        self.df[column_name] = self.df[self._column].map(self.group_lookup).fillna(self.df[self._column])

    def run(self, column_name='Group'):
        self.build_group_lookup()
        self.add_grouped_column_to_data(column_name)
        print('Ready for export')

    def _filter_df_for_export(self):
        return self.df.drop(columns=['textpackGrouper']) if 'textpackGrouper' in self.df.columns else self.df

    def export_json(self, export_path=None):
        return self._filter_df_for_export().to_json(export_path)

    def export_csv(self, export_path=None):
        return self._filter_df_for_export().to_csv(export_path)


def read_json(json_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3):
    return TextPack(pd.read_json(json_path), columns_to_group, match_threshold, ngram_remove, ngram_length)


def read_excel(excel_path, columns_to_group, sheet_name=None, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3):
    return TextPack(pd.read_excel(excel_path), sheet_name, columns_to_group, match_threshold, ngram_remove, ngram_length)


def read_csv(csv_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3):
    return TextPack(pd.read_csv(csv_path), columns_to_group, match_threshold, ngram_remove, ngram_length)
