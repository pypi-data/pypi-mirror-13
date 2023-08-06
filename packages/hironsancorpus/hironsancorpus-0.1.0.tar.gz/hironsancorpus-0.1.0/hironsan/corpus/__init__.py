# -*- coding: utf-8 -*-
import os


class CorpusReader(object):

    def __init__(self, path):
        with open(path) as f:
            sent = []
            sents = []
            for line in f:
                if line	== '\n':
                    sents.append(sent)
                    sent = []
                morph_info = line.strip().split('\t')
                try:
                    morph_info = [word.decode('utf-8') for word in morph_info]
                except AttributeError:
                    pass
                sent.append(morph_info)
        train_num = int(len(sents) * 0.9)
        self.__train_sents = sents[:train_num]
        self.__test_sents = sents[train_num:]

    def iob_sents(self, name):
        if name == 'train':
            return self.__train_sents
        elif name == 'test':
            return self.__test_sents
        else:
            return None


hiron2016 = CorpusReader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iob_sents.txt'))