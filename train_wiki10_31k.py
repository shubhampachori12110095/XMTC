'''
Created on Nov, 2017

@author: FrancesZhou
'''

from __future__ import absolute_import

import os
import argparse
import numpy as np
from biLSTM.preprocessing.preprocessing import generate_label_embedding_from_file, get_train_test_doc_label_data
from biLSTM.preprocessing.dataloader import DataLoader2, DataLoader3
from biLSTM.core.biLSTM import biLSTM
from biLSTM.core.solver import ModelSolver
from biLSTM.utils.io_utils import load_pickle, load_txt

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('-train_doc_wordID_data', '--train_doc_wordID_data_path', type=str,
                       default='datasets/Wiki10/output/final/train_doc_wordID.pkl',
                       help='path to the train wordID data')
    parse.add_argument('-test_doc_wordID_data', '--test_doc_wordID_data_path', type=str,
                       default='datasets/Wiki10/output/final/test_doc_wordID.pkl',
                       help='path to the test wordID data')
    parse.add_argument('-train_label_data', '--train_label_data_path', type=str,
                       default='datasets/Wiki10/output/final/train_label.pkl',
                       help='path to the train labels data')
    parse.add_argument('-test_label_data', '--test_label_data_path', type=str,
                       default='datasets/Wiki10/output/final/test_label.pkl',
                       help='path to the test labels data')
    parse.add_argument('-vocab', '--vocab_path', type=str, default='datasets/vocab', help='path to the vocab')
    # parse.add_argument('-word_embeddings', '--word_embedding_path', type=str,
    #                    default='datasets/glove.840B.300d.txt',
    #                    help='path to the word embeddings')
    parse.add_argument('-word_embeddings', '--word_embedding_path', type=str,
                       default='datasets/word_embeddings.npy',
                       help='path to the word embeddings')
    parse.add_argument('-label_embeddings', '--label_embedding_path', type=str,
                       default='datasets/Wiki10/output/label_pair/label.embeddings',
                       help='path to the label embeddings')
    parse.add_argument('-pretrained_model', '--pretrained_model_path', type=str,
                       default=None, help='path to the pretrained model')
    #parse.add_argument('-o', '--out_dir', type=str, required=True, help='path to the output dir')
    # -- default
    parse.add_argument('-n_epochs', '--n_epochs', type=int, default=10, help='number of epochs')
    parse.add_argument('-batch_size', '--batch_size', type=int, default=16, help='batch size')
    parse.add_argument('-lr', '--learning_rate', type=float, default=0.0002, help='learning rate')
    parse.add_argument('-update_rule', '--update_rule', type=str, default='adam', help='update rule')
    args = parse.parse_args()

    vocab = load_pickle(args.vocab_path)
    print 'load word/label embeddings'
    word_embeddings = np.load(args.word_embedding_path)
    label_embeddings = generate_label_embedding_from_file(args.label_embedding_path)
    print 'load train/test data'
    train_doc = load_pickle(args.train_doc_wordID_data_path)
    test_doc = load_pickle(args.test_doc_wordID_data_path)
    train_label = load_pickle(args.train_label_data_path)
    test_label = load_pickle(args.test_label_data_path)
    # train_data = train_data[:len(train_data)/10]
    # test_data = test_data[:len(test_data)/10]
    # train_label = train_label[:len(train_data)]
    # test_label = test_label[:len(test_data)]
    #all_labels = load_pickle(args.all_labels_path)
    all_labels = label_embeddings.keys()
    print 'create train/test data loader...'
    train_loader = DataLoader2(train_doc, train_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, pos_neg_ratio=1)
    max_seq_len = train_loader.max_seq_len
    test_loader = DataLoader2(test_doc, test_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, pos_neg_ratio=1, max_seq_len=max_seq_len)
    # ----- train -----
    print 'build biLSTM model...'
    # (self, max_seq_len, input_dim, num_label_embedding, num_hidden, num_classify_hidden)
    model = biLSTM(max_seq_len, 300, 64, 64, 32, args.batch_size)

    print 'model solver...'
    # def __init__(self, model, train_data, test_data, **kwargs):
    solver = ModelSolver(model, train_loader, test_loader,
                         n_epochs=args.n_epochs,
                         batch_size=args.batch_size,
                         update_rule=args.update_rule,
                         learning_rate=args.learning_rate,
                         pretrained_model=None,
                         model_path='datasets/Wiki10/output/results/model_save/',
                         test_path='datasets/Wiki10/output/results/model_save/')
    print 'begin training...'
    solver.train()

    # test
    # test_all = DataLoader3(test_doc, test_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, max_seq_len)
    # solver.test(test_all)


if __name__ == "__main__":
    main()
