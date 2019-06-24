import pandas as pd
from functools import reduce
from fuzzywuzzy import fuzz

import pdb


class ColumnGrouper():
    def __init__(self, csv_path, column_to_group, threshold, match_type):
        self._df = pd.read_csv(csv_path)
        self._column = column_to_group
        self._threshold = threshold
        self._matcher = self._set_matcher(match_type)
        self._groups = None

    def _set_matcher(self, match_type):
        try:
            return getattr(fuzz, match_type)
        except AttributeError:
            print(f'FuzzyWuzzy does not have the attribute: {match_type}. Read the docs here: https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/')

    def _train_group(self, group):
        highest_prox = 0
        for name in group['names']:
            prox = 0
            for sibling in group['names']:
                if sibling != name:
                    prox += self._matcher(name, sibling)
            if prox > highest_prox:
                highest_prox = prox
                group['key'] = name

    def _add_name_to_group(self, group, value):
        group['names'].add(value)
        self._train_group(group)

    def _add_new_group(self, groups, value):
        groups.append({
            'key': value,
            'names': set([value]),
        })

    def _get_closest_match(self, matches, value):
        closest = None
        highest_prox = 0
        for group in matches:
            prox = self._matcher(value, group['key'])
            if prox > highest_prox:
                highest_prox = prox
                closest = group
        return closest

    def _find_matching_groups(self, groups, value):
        return list(
            filter(
                lambda group: self._matcher(value, group['key']) > self._threshold,
                groups
            )
        )

    def _determine_best_group(self, groups, value):
        matches = self._find_matching_groups(groups, value)
        if not matches:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            return self._get_closest_match(matches, value)

    def _build_groups(self, groups, value):
        group = self._determine_best_group(groups, value)
        if group is None:
            self._add_new_group(groups, value)
        elif value not in group['names']:
            self._add_name_to_group(group, value)
        return groups

    def train_grouper(self):
        self._groups = reduce(self._build_groups, self._df[self._column].to_list(), [])

    def get_group_keys(self):
        try:
            return [group['key'] for group in self._groups]
        except AttributeError:
            print('You need to train the grouper before keys will exist')

    def get_group_names(self, min_names_per_group=2):
        try:
            return [group['names'] for group in self._groups if len(group['names']) >= min_names_per_group]
        except AttributeError:
            print('You need to train the grouper before keys will exist')

    def _compare_two_groups(self, best, group, value):
        prox = self._matcher(value, group['key'])
        if prox > best[1]:
            best = (group['key'], prox)
        return best

    def _get_best_group_for_row(self, value):
        best = ('', 0)
        for group in self._groups:
            prox = self._matcher(value, group['key'])
            if prox > best[1]:
                best = (group['key'], prox)
        return best[0]

    def add_grouped_column_to_df(self, column_name='Group'):
        self._df[column_name] = self._df.apply(lambda row: self._get_best_group_for_row(row[self._column]), axis=1)


eviction_grouper = ColumnGrouper(
    csv_path='./data/evictions-test.csv',
    column_to_group='Plaintiff',
    threshold=70,
    match_type='token_sort_ratio'
)

eviction_grouper.train_grouper()

eviction_grouper.add_grouped_column_to_df()

print(eviction_grouper._df['Group'])
