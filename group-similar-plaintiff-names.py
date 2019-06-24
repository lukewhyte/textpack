import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from sparse_dot_topn import awesome_cossim_topn


class ColumnGrouper():
    def __init__(self, csv_path, column_to_group, match_threshold, top_n):
        self._df = pd.read_csv(csv_path)
        self._column = column_to_group
        self._match_threshold = match_threshold
        self._top_n = top_n
        self._matrix = None

    def _ngrams_analyzer(self, string, n=3):
        string = re.sub(r'[,-./]', r'', string)
        ngrams = zip(*[string[i:] for i in range(n)])
        return [''.join(ngram) for ngram in ngrams]

    def _get_tf_idf_matrix(self):
        vectorizer = TfidfVectorizer(analyzer=self._ngrams_analyzer)
        return vectorizer.fit_transform(self._df[self._column])

    def build_matrix(self):
        tf_idf_matrix = self._get_tf_idf_matrix()
        self._matrix = awesome_cossim_topn(tf_idf_matrix, tf_idf_matrix.transpose(), self._top_n, self._match_threshold)

def get_matches_df(sparse_matrix, name_vector, top=5700):
    non_zeros = sparse_matrix.nonzero()
    
    print(sparse_matrix)

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]
    
    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size
    
    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)
    
    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]
    
    return pd.DataFrame({'left_side': left_side,
                          'right_side': right_side,
                           'similairity': similairity})


eviction_grouper = ColumnGrouper(
    csv_path='./data/evictions-test.csv',
    column_to_group='Plaintiff',
    match_threshold=0.7,
    top_n=10,
)

eviction_grouper.build_matrix()

matches_df = get_matches_df(eviction_grouper._matrix, eviction_grouper._df['Plaintiff'])
