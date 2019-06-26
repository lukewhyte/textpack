import re
import pandas as pd
from functools import reduce
from fuzzywuzzy import fuzz

import pdb


class ColumnGrouper():
    def __init__(self, csv_path, column_to_group, threshold, match_type, export_path):
        self._df = pd.read_csv(csv_path)
        self._column = column_to_group
        self._threshold = threshold
        self._matcher = self._set_matcher(match_type)
        self._groups = None
        self._export_path = export_path
        self._trained_rows = 0
        self._grouped_rows = 0

    def _set_matcher(self, match_type):
        try:
            return getattr(fuzz, match_type)
        except AttributeError:
            print(f'FuzzyWuzzy does not have the attribute: {match_type}. Read the docs here: https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/')

    def _train_group(self, key, groups):
        highest_prox = 0
        best_key = key
        for name in groups[key]:
            prox = 0
            for sibling in groups[key]:
                if sibling != name:
                    prox += self._matcher(name, sibling)
            if prox > highest_prox:
                highest_prox = prox
                best_key = name
        groups[best_key] = groups.pop(key)

    def _add_name_to_group(self, key, value, groups):
        groups[key].add(value)
        self._train_group(key, groups)

    def _add_new_group(self, groups, value):
        groups[value] = set([value])

    def _get_closest_match(self, matches, value):
        closest = None
        highest_prox = 0
        for key, names in matches.items():
            prox = self._matcher(value, key)
            if prox > highest_prox:
                highest_prox = prox
                closest = key
        return closest

    def _find_matching_groups(self, groups, value):
        return {key: names for key, names in groups.items() if self._matcher(value, key) > self._threshold}

    def _determine_best_group(self, groups, value):
        matches = self._find_matching_groups(groups, value)
        if not matches:
            return None
        else:
            return self._get_closest_match(matches, value)

    def _clean_name(self, value):
        return re.sub(r'[,-./]', r'', value).upper()

    def _build_groups(self, groups, value):
        value = self._clean_name(value)
        key = self._determine_best_group(groups, value)
        if key is None:
            self._add_new_group(groups, value)
        elif value not in groups[key]:
            self._add_name_to_group(key, value, groups)
        self._trained_rows += 1
        print(f'{self._trained_rows} rows trained')
        return groups

    def train_grouper(self):
        self._groups = reduce(self._build_groups, self._df[self._column].unique().tolist(), {})

    def get_group_keys(self):
        try:
            return list(self._groups.keys())
        except AttributeError:
            print('You need to train the grouper before keys will exist')

    def get_group_names(self, min_names_per_group=2):
        try:
            return [names for names in self._groups if len(names) >= min_names_per_group]
        except AttributeError:
            print('You need to train the grouper before keys will exist')

    def _compare_two_groups(self, best, group, value):
        prox = self._matcher(value, group['key'])
        if prox > best[1]:
            best = (group['key'], prox)
        return best

    def _get_best_group_for_row(self, value):
        value = self._clean_name(value)

        if value in self._groups:
            return value

        best = ('', 0)
        for key in self.get_group_keys():
            prox = self._matcher(value, key)
            if prox > best[1]:
                best = (key, prox)

        self._grouped_rows += 1
        print(f'{self._grouped_rows} rows grouped')
        return best[0]

    def add_grouped_column_to_df(self, column_name='Group'):
        self._df[column_name] = self._df.apply(lambda row: self._get_best_group_for_row(row[self._column]), axis=1)

    def export_csv(self):
        self._df.to_csv(self._export_path)


eviction_grouper = ColumnGrouper(
    csv_path='./data/evictions.csv',
    column_to_group='Plaintiff',
    threshold=75,
    match_type='token_sort_ratio',
    export_path='./data/evictions-grouped-two.csv'
)

eviction_grouper.train_grouper()

eviction_grouper.add_grouped_column_to_df()

eviction_grouper.export_csv()
