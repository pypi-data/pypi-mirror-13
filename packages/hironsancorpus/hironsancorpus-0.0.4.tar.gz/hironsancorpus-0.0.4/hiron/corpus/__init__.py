# -*- coding: utf-8 -*-
import os


class CorpusReader(object):

    def __init__(self, path):
        import pickle
        with open(path) as f:
            iob_sents = pickle.load(f)
        train_num = int(len(iob_sents) * 0.9)
        self.__train_sents = iob_sents[:train_num]
        self.__test_sents = iob_sents[train_num:]

    def iob_sents(self, name):
        if name == 'train':
            return self.__train_sents
        elif name == 'test':
            return self.__test_sents
        else:
            return None


hiron2016 = CorpusReader(os.path.join(os.path.abspath('hiron/corpus'), 'hiron_corpus.pickle'))