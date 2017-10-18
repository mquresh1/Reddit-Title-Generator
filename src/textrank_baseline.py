# -*- coding: utf-8 -*-
"""
Original code by https://github.com/davidadamojr/

Modified by Mohammad Qureshi

This code uses TextRank for title generation by summarization, the naive solution
"""

import io
import itertools
import os

import networkx as nx
import nltk

import json

__version__ = '0.1.0'


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


def extractSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get,
                       reverse=True)
					   
	# return only the top ranking sentence
    return sentences[0]


def create_baseline_title(comments):
    """ Function that performs all prerequisites for handling data and organizing it to be used 
        to call extractSentences
    """
    # Removing [deleted] comments from the comment list and cleaning up leading symbols not relevant to the process
    comments = [comment.replace('&gt; ', '') for comment in comments if comment != '[deleted]']

    # join comments into a "document" since the sentence extraction will tokenize 
    text = ' '.join(comments)
    
    return extractSentences(text)


if __name__ == '__main__':
    file_path = sys.path[0] + '/outputs/comments.json'

    with open(file_path, encoding='utf-8') as data:
		# load comment data 
        comment_data = json.load(data)
        
		# writes results to file
        with open('baseline_output.txt', 'w', encoding='utf-8') as f:
            for title, comments in comment_data.items():
                # filter out small posts
                if(len(comments) > 9):
                    gen_title = create_baseline_title(comments)
                    f.write("##############################################################\n")
                    f.write('ORIGINAL TITLE: {}\n'.format(title))
                    f.write('GENERATED TITLE: {}\n\n'.format(gen_title))
