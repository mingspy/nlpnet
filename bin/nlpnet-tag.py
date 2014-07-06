#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script will run a POS or SRL tagger on the input data and print the results
to stdout.
"""

import argparse
import logging
from itertools import izip

import nlpnet
import nlpnet.utils as utils

def interactive_running(task, use_tokenizer=True):
    """
    This function provides an interactive environment for running the system.
    It receives text from the standard input, tokenizes it, and calls the function
    given as a parameter to produce an answer.
    
    :param task: either 'pos' or 'srl'
    :param use_tokenizer: whether to use built-in tokenizer
    """
    task_lower = task.lower()
    if task_lower == 'pos':
        tagger = nlpnet.taggers.POSTagger()
    elif task_lower == 'srl':
        tagger = nlpnet.taggers.SRLTagger()
    elif task_lower == 'dependency':
        tagger = nlpnet.taggers.DependencyParser()
    else:
        raise ValueError('Unknown task: %s' % task)
    
    while True:
        try:
            text = raw_input()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        
        if type(text) is not unicode:
            text = unicode(text, 'utf-8')
        
        if use_tokenizer:
            result = tagger.tag(text)
        else:
            tokens = text.split()
            result = [tagger.tag_tokens(tokens, True)]
        
        _print_tagged(result, task)

def _print_tagged(tagged_sents, task):
    """
    Prints the tagged text to stdout.
    
    :param tagged_sents: sentences tagged according to any of nlpnet taggers.
    :param task: the tagging task (either 'pos', 'srl' or 'dependency')
    """
    if task == 'pos':
        _print_tagged_pos(tagged_sents)
    elif task == 'srl':
        _print_tagged_srl(tagged_sents)
    elif task == 'dependency':
        _print_parsed_dependency(tagged_sents)
    else:
        raise ValueError('Unknown task: %s' % task)

def _print_parsed_dependency(parsed_sents):
    """Prints one token per line and its head"""
    for sent in parsed_sents:
        for i, (token, head) in enumerate(sent):
            line = u'%2d %s\t\t%s' % (i, token, head)
            print line.encode('utf-8') 
        
        print

def _print_tagged_pos(tagged_sents):
    """Prints one sentence per line as token_tag"""
    for sent in tagged_sents:
        s = ' '.join('_'.join(item) for item in sent)
        print s.encode('utf-8')

def _print_tagged_srl(tagged_sents):
    for sent in tagged_sents:
        print ' '.join(sent.tokens).encode('utf-8')
        for predicate, arg_structure in sent.arg_structures:
            print predicate.encode('utf-8')
            for label in arg_structure:
                argument = ' '.join(arg_structure[label])
                line = '\t%s: %s' % (label, argument)
                print line.encode('utf-8')
        print


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('task', help='Task for which the network should be used.', 
                        type=str, choices=['srl', 'pos', 'dependency'])
    parser.add_argument('data', help='Directory containing trained models.', type=str)
    parser.add_argument('-v', help='Verbose mode', action='store_true', dest='verbose')
    parser.add_argument('-t', action='store_true', dest='disable_tokenizer',
                        help='Disable built-in tokenizer. Tokens are assumed to be separated by whitespace.')
    parser.add_argument('--no-repeat', dest='no_repeat', action='store_true',
                        help='Forces the classification step to avoid repeated argument labels (SRL only).')
    args = parser.parse_args()
    
    logging_level = logging.DEBUG if args.verbose else logging.WARNING
    utils.set_logger(logging_level)
    logger = logging.getLogger("Logger")
    nlpnet.set_data_dir(args.data)
    
    use_tokenizer = not args.disable_tokenizer
    interactive_running(args.task, use_tokenizer)
    