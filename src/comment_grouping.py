# -*- coding: utf-8 -*-
"""
Written by Mohammad Qureshi

Used the truncated dataset and the titles extracted for this set to create a dictionary
of titles->list of comments for use in Phase 1 and Phase 2 title generation
"""

import json

# truncated.json is a spliced version of the one month Reddit comment history
json_file = "truncated.json"

# create a dictionary to hold title->comments
comments_dict = {}
with open('titles.json', encoding='utf-8') as data:
	# load title data
    titles = json.load(data)
    with open(json_file, encoding='utf-8') as file:
		# go through each line(json block) in truncated
        for line in file:
			# used try except to error handle in case strange characters were picked up in comments
            try:
                comment = json.loads(line)
				# title data is grouped by subreddit before using link_id as link_id
				# is only unique to a subreddit
                title = titles[comment['subreddit']][comment['link_id'][3:]]
                if title not in comments_dict:
                    comments_dict[title] = []
                comments_dict[title].append(comment['body'])
            except:
                pass

# write title->comment data to a json for easy loading in title generation
with open('comments.json', 'w') as fp:
    json.dump(comments_dict, fp, sort_keys=True, indent=4)