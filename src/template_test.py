"""
Written by Mohammad Qureshi

Goes through all titles in the database and POS tags them to
find a common structure to be used as a template
"""

import nltk
import json
from collections import defaultdict


with open("comments.json", encoding='utf-8') as data:
    # create a dictionary to hold POS structure and number of times they occur
    pos_dict = defaultdict(int)
    comment_data = json.load(data)
    for title, comments in comment_data.items():
        # filter out small posts
        if(len(comments) > 9):
            # Tokenize title
            wordTokens = nltk.word_tokenize(title)
            # POS tag tokens
            tagged = nltk.pos_tag(wordTokens)

            ''' join the POS by / and use that as a key and increment the occur of this structure '''
            # posStructure = '/'.join([x[1] for x in tagged])
            # pos_dict[posStructure] += 1

            ''' count each occurence of a POS tag '''
            for words in tagged:
                pos_dict[words[1]] += 1

    for k,v in sorted(pos_dict.items(), key=lambda p:p[1], reverse=True):
        print(k, v)
    
    """ 
        Although these results show that every sentence structure is nearly unique in the Reddit database
        by combining these results with the idea that a common structure in English is Subject+Verb+Noun
        we can attempt to form a sentence using POS's in these categories
    
        Subject = [NNP, NN]
        Verb = [VB, VBZ]
        Adjective = [JJ]
    
        If a POS category has not keywords in it, use the next POS 
        Possible template NNP + VB + JJ + NN
    """