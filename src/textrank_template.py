# -*- coding: utf-8 -*-
"""
Original code by https://github.com/davidadamojr/

Modified by Mohammad Qureshi

Uses TextRank for keyword extraction and applies a template to POS-tagged keywords
"""

import io
import itertools
import os

import networkx as nx
import nltk

import json
from collections import defaultdict


__version__ = '0.1.0'

# Used to keep ordering of keywords after extraction
keyword_dict = dict()

# apply syntactic filters based on POS tags
def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]


def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in [x for x in iterable if x not in seen]:
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def lDistance(firstString, secondString):
    """Function to find the Levenshtein distance between two words/sentences -
    gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python
    """
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]


def buildGraph(nodes):
    """nodes - list of hashables that represents the nodes of the graph"""
    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr


def extractKeyphrases(text):
    # tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    # assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]

    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

    # this will be used to determine adjacent words in order to construct
    # keyphrases with two words

    graph = buildGraph(word_set_list)

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    global keyword_dict
    calculated_page_rank = nx.pagerank(graph, weight='weight')
    keyword_dict = calculated_page_rank

    # most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get,
                        reverse=True)

    # the number of keyphrases returned will be relative to the size of the
    # text (a third of the number of vertices)
    aThird = len(word_set_list) // 3
    keyphrases = keyphrases[0:aThird + 1]

    # take keyphrases with multiple words into consideration as done in the
    # paper - if two words are adjacent in the text and are selected as
    # keywords, join them together
    modifiedKeyphrases = set([])
    # keeps track of individual keywords that have been joined to form a
    # keyphrase
    dealtWith = set([])
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            # if this is the last word in the text, and it is a keyword, it
            # definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and secondWord in keyphrases and \
                    secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)

        i = i + 1
        j = j + 1

    return modifiedKeyphrases


def generateTitle(pos_dict):
    """ Based on the common English sentence structure Subject+Verb+Object
        creat a templated sentence using POS tags for the title belong to those
        categories
    """
    Noun = ['NNP', 'NN']
    Verb = ['VB', 'VBZ', 'VBD']
    Adjective = ['JJ']
    title = ""
    
    # Subject
    if(len(pos_dict[Noun[0]]) > 0):
        title += pos_dict[Noun[0]].pop(0) + ' '
    elif(len(pos_dict[Noun[1]]) > 0):
        title += pos_dict[Noun[1]].pop(0) + ' '

    # Verb
    if(len(pos_dict[Verb[0]]) > 0):
        title += pos_dict[Verb[0]].pop(0) + ' '
    elif(len(pos_dict[Verb[1]]) > 0):
        title += pos_dict[Verb[1]].pop(0) + ' '
    elif(len(pos_dict[Verb[2]]) > 0):
        title += pos_dict[Verb[2]].pop(0) + ' '

    # Adjective (for description)
    if(len(pos_dict[Adjective[0]]) > 0):
        title += pos_dict[Adjective[0]].pop(0) + ' '
    
    # Object (favor Nouns here)
    if(len(pos_dict[Noun[1]]) > 0):
        title += pos_dict[Noun[1]].pop(0)
    elif(len(pos_dict[Noun[0]]) > 0):
        title += pos_dict[Noun[0]].pop(0)

    return title


def create_template_title(comments):
    """ Function that performs all prerequisites for handling data and organizing it to be used 
        to call generateTitle 
    """
    # Removing [deleted] comments from the comment list and cleaning up leading symbols not relevant to the process
    comments = [comment.replace('&gt; ', '') for comment in comments if comment != '[deleted]']

    # join comments since the keyword extraction will tokenize 
    text = ' '.join(comments)

    # run keyword extraction on comments
    keyphrases = extractKeyphrases(text)

    # Apply pagerank values to word or first word in a phrase
    keyphrase_dict = {keyphrase : keyword_dict[keyphrase.split(' ')[0]] for keyphrase in keyphrases}

    # Order in descending order of importance 
    ranked_keyphrases = sorted(keyphrase_dict, key=keyphrase_dict.get, reverse=True)

    # Tag and store in dictionary
    tagged = nltk.pos_tag(ranked_keyphrases)
    pos_dict = defaultdict(list)

    for word in tagged:
        pos_dict[word[1]].append(word[0])
    
    return generateTitle(pos_dict)


if __name__ == '__main__':
    file_path = sys.path[0] + '/outputs/comments.json'

    with open(file_path, encoding='utf-8') as data:
        # load comment data 
        comment_data = json.load(data)

        with open('template_output.txt', 'w', encoding='utf-8') as f:
            for title, comments in comment_data.items():
                # filter out small posts
                if(len(comments) > 9):
                    
                    # Write original title and generated title for the post
                    gen_title = create_template_title(comments)
                    f.write("##############################################################\n")
                    f.write('ORIGINAL TITLE: {}\n'.format(title))
                    f.write('GENERATED TITLE: {}\n\n'.format(gen_title))