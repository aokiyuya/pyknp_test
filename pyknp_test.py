#! !(which python)
# coding: utf-8
###########################
# Author: Yuya Aoki
#
###########################
import pyknp as kp
from copy import deepcopy as dc
from collections import deque


# features_in_phrase = {
#         'pronounce': '',
#         'rank_in_a_sequence_of_phrase': 0,
#         'rank_in_a_sequence_of_elements_of_P_A': 0,
#         'POS_tag_in_the_phrase': '',
#         'POS_tag_sequence': '',
#         'Pair_of_POS_tag_and_its_order_in_the_phrase': '',
#         'Which_semantic_role_the_phrase_has': '',
#         'Which_semantic_role_exist_on_the_utterance': '',
#         'Pair_of_semantic_role_and_its_order_in_the_phrase': ['', 0],
#         'P_A_significance_score': 0,
#         'Word_in_the_phrase': '',
#         'Pair_of_words_in_the_phrase': [],
#         'Pair_of_word_and_its_order_in_the_phrase': ['', 0]
#         }

class Features_in_phrase(object):
    def __init__(self):
        self.sentence = ''
        self.pronounce = ''
        self.rank_in_a_sequence_of_phrase = 0
        self.rank_in_a_sequence_of_elements_of_P_A = 0
        self.POS_tag_in_the_phrase = ''
        self.POS_tag_sequence = ''
        self.Pair_of_POS_tag_and_its_order_in_the_phrase = ''
        self.Which_semantic_role_the_phrase_has = ''
        self.Which_semantic_role_exist_on_the_utterance = ''
        self.Pair_of_semantic_role_and_its_order_in_the_phrase = []
        # self.P_A_significance_score = 0
        self.Word_in_the_phrase = ''
        self.Pair_of_words_in_the_phrase = ''
        self.Pair_of_word_and_its_order_in_the_phrase = ''
        self.label = ''

    def _string_features(self):
        return ",".join([
            self.pronounce,
            str(self.rank_in_a_sequence_of_phrase),
            str(self.rank_in_a_sequence_of_elements_of_P_A),
            self.POS_tag_in_the_phrase,
            self.POS_tag_sequence,
            self.Pair_of_POS_tag_and_its_order_in_the_phrase,
            self.Which_semantic_role_the_phrase_has,
            self.Which_semantic_role_exist_on_the_utterance,
            self.Pair_of_semantic_role_and_its_order_in_the_phrase,
            self.Word_in_the_phrase,
            self.Pair_of_words_in_the_phrase,
            self.Pair_of_word_and_its_order_in_the_phrase,
            self.label
        ])

    def _string_features_without_label(self):
        return ",".join([
            self.pronounce,
            str(self.rank_in_a_sequence_of_phrase),
            str(self.rank_in_a_sequence_of_elements_of_P_A),
            self.POS_tag_in_the_phrase,
            self.POS_tag_sequence,
            self.Pair_of_POS_tag_and_its_order_in_the_phrase,
            self.Which_semantic_role_the_phrase_has,
            self.Which_semantic_role_exist_on_the_utterance,
            self.Pair_of_semantic_role_and_its_order_in_the_phrase,
            self.Word_in_the_phrase,
            self.Pair_of_words_in_the_phrase,
            self.Pair_of_word_and_its_order_in_the_phrase
        ]) + '\n'

    def print(self):
        print(self._string_features())

    def get_study_data(self):
        return self._string_features_without_label()

    def write(self):
        with open("_features.csv", 'a') as fp:
            fp.write(self._string_features())


class KNP_Parser(object):
    def __init__(self):
        pass

    def parse_knp(self, knp, string, label=None):
        self.result = knp.parse(string)
        self.phrase_list = self.result.bnst_list()
        # phrase_dic = dict((x.bnst_id, x) for x in phrase_list)
        self.rank_in_a_sequence_of_phrase = 0
        self.p_a_rank = 1
        self.POS_tag_sequence = []
        self.features_list = []
        self.semantic_role_list = []
        for phrase in self.phrase_list:
            self.get_feature_in_phrase(phrase)
        # print(self.POS_tag_sequence)
        # print(self.semantic_role_list)
        for x in self.features_list:
            x.POS_tag_sequence = ";".join(set(self.POS_tag_sequence))
            x.Which_semantic_role_exist_on_the_utterance = ";".join(self.semantic_role_list)
            x.sentence = ''.join([i.pronounce for i in self.features_list])
            # print(x.sentence)
            if label is not None:
                x.label = label.popleft()
            else:
                self.set_label(x, x.pronounce)
            x.write()

    def get_label_from_file(self, feature, fp):
        feature.label = fp.readline()

    def get_feature_in_tag(self, phrase, features):
        sr_count = 1
        for tag in phrase.tag_list():
            feature = kp.Features(tag.spec())
            if '解析格' in feature.keys():
                features.Which_semantic_role_the_phrase_has += feature['解析格']
                features.Pair_of_semantic_role_and_its_order_in_the_phrase.append(str(sr_count) + ':' + feature['解析格'])
                sr_count += 1
            elif '状態述語' in feature.keys():
                features.Which_semantic_role_the_phrase_has += '状態述語'
                features.Pair_of_semantic_role_and_its_order_in_the_phrase.append(str(sr_count) + ':状態述語')
                sr_count += 1
            elif '動態述語' in feature.keys():
                features.Which_semantic_role_the_phrase_has += '動態述語'
                features.Pair_of_semantic_role_and_its_order_in_the_phrase.append(str(sr_count) + ':動態述語')
                sr_count += 1
            if features.Which_semantic_role_the_phrase_has != '':
                self.semantic_role_list.append(
                        features.Which_semantic_role_the_phrase_has)
            if '項構造' in feature.keys():
                features.rank_in_a_sequence_of_elements_of_P_A = self.p_a_rank
                self.p_a_rank = self.p_a_rank + 1
                break
            else:
                features.rank_in_a_sequence_of_elements_of_P_A = 'nil'
                break

    def get_feature_in_phrase(self, phrase):
        features = Features_in_phrase()
        self.rank_in_a_sequence_of_phrase = self.rank_in_a_sequence_of_phrase + 1
        pronounce = []
        POS_list_in_phrase = []
        pos_and_order = []
        word_and_order = []
        for i, mrph in enumerate(phrase.mrph_list()):
            pronounce.append(mrph.midasi)
            word_and_order.append(":".join([str(i + 1), mrph.midasi]))
            POS_list_in_phrase.append(mrph.hinsi)
            pos_and_order.append(":".join([str(i + 1), mrph.hinsi]))
        features.Word_in_the_phrase = ";".join(pronounce)
        features.Pair_of_word_and_its_order_in_the_phrase = ";".join(word_and_order)
        if len(pronounce) < 2:
            pass
        else:
            bi_gram = [pronounce[i] + ":" + pronounce[i + 1] for i in range(0, len(pronounce) - 1)]
            string = ";".join(bi_gram)
            features.Pair_of_words_in_the_phrase = string
        features.pronounce = ''.join(pronounce)
        features.Word_in_the_phrase = ';'.join(pronounce)
        features.rank_in_a_sequence_of_phrase = self.rank_in_a_sequence_of_phrase
        self.get_feature_in_tag(phrase, features)
        features.Pair_of_POS_tag_and_its_order_in_the_phrase = ";".join(pos_and_order)
        features.POS_tag_in_the_phrase = ";".join(POS_list_in_phrase)
        self.POS_tag_sequence.extend(POS_list_in_phrase)
        tmp = dc(features.Pair_of_semantic_role_and_its_order_in_the_phrase)
        features.Pair_of_semantic_role_and_its_order_in_the_phrase = ";".join(tmp)
        self.features_list.append(features)

    def set_label(self, feature, pronounce):
        print(''.join(pronounce))
        while True:
            label = input('label=>')
            if 'x' not in label and 'o' not in label:
                print("type x or o only")
            else:
                feature.label = label
                break


def main():
    print("label:x or o")
    string = '1990年生まれはみんなごはんとラーメンを一緒に食べることが普通だ'
    with open('./label_file') as fp:
        label = deque(fp.readlines())
    label = None
    with open('./all_text.csv') as f:
        for line in f.readlines():
            flag, string = line.split(',')
            if flag == 'x':
                print(string)
                knp = kp.KNP(option='-tab -anaphora')
                knp_parser = KNP_Parser()
                knp_parser.parse_knp(knp, string, label=label)


if __name__ == '__main__':
    # code
    main()
