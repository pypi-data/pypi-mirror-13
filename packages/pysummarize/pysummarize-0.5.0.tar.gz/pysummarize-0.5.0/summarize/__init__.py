# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import combinations
from operator import itemgetter

from distance import jaccard
from networkx import Graph, pagerank

from .language import split_sentences, split_words, get_stopwords


__all__ = ['summarize']


def summarize(text, sentence_count=5, language='english'):
    stopwords = get_stopwords(language)
    sentence_list = split_sentences(text, language)
    wordsets = [split_words(sentence, stopwords) for sentence in sentence_list]

    graph = Graph()
    pairs = combinations(enumerate(wordsets), 2)
    for (index_a, words_a), (index_b, words_b) in pairs:
        if words_a and words_b:
            similarity = 1 - jaccard(words_a, words_b)
            if similarity > 0:
                graph.add_edge(index_a, index_b, weight=similarity)

    ranked_sentence_indexes = list(pagerank(graph).items())
    if ranked_sentence_indexes:
        sentences_by_rank = sorted(
            ranked_sentence_indexes, key=itemgetter(1), reverse=True)
        best_sentences = map(itemgetter(0), sentences_by_rank[:sentence_count])
        best_sentences_in_order = sorted(best_sentences)
    else:
        best_sentences_in_order = range(min(sentence_count, len(sentence_list)))

    return ' '.join(sentence_list[index] for index in best_sentences_in_order)
