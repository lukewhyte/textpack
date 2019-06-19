import pandas as pd
from fuzzywuzzy import fuzz

df = pd.read_csv('./data/evictions-test.csv')

p_hash_list = []


def add_new_hash(series, plaintiff):
    p_hash_list.append({
        'key': plaintiff,
        'names': [plaintiff],
        'series': series,
    })


def update_key(p_hash):
    high_score = 0
    score = 0
    for name in p_hash['names']:
        for sibling in p_hash['names']:
            score += fuzz.token_sort_ratio(name, sibling)
        if score < high_score:
            high_score = score
            p_hash['key'] = name


def add_to_existing_hash(series, p_hash, plaintiff):
    p_hash['names'].append(plaintiff)
    update_key(p_hash)
    p_hash['series'].append(series)


def add_to_hash_list(series, plaintiff):
    for p_hash in p_hash_list:
        if fuzz.token_sort_ratio(plaintiff, p_hash['key']) > 90:
            return add_to_existing_hash(series, p_hash, plaintiff)
    add_new_hash(series, plaintiff)


for idx, row in df.iterrows():
    add_to_hash_list(row, row['Plaintiff'])

for p_hash in p_hash_list:
    if len(p_hash['names']) > 1:
        print(p_hash['names'])
