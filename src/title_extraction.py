# -*- coding: utf-8 -*-
"""
Written by Mohammad Qureshi

Used the Reddit Python API Wrapper to make HTML requests to Reddit and pull
titles for each Reddit post in the truncated dataset and write that information
to a json file
"""

import json
import praw

# dataset loaded in
json_file = "truncated.json"
# initialization used for PRAW
reddit = praw.Reddit(user_agent='Title Extractor',
                     client_id='', client_secret='')

title_dict = {}
with open(json_file, encoding='utf-8') as json_data:
	# reddit data opened and read line by line (one comment at a time)
    for line in json_data:
        try:
            data = json.loads(line)
			# subreddit data and link_id pulled from the comment
			# Note: subreddit is pulled here as link_id are only unique per subreddit 
            subreddit = data['subreddit']
            link_id = data['link_id'][3:]
			# Data is stored as a nested dictionary of structure d['subreddit']['link_id'] = title
            if subreddit not in title_dict:
                title_dict[subreddit] = {}
            if link_id not in title_dict[subreddit]:
				# Reddit API used to pull title 
                submission = reddit.submission(url='https://www.reddit.com/r/'+subreddit+'/comments/'+link_id)
				# Title stored in dictionary 
                title_dict[subreddit][link_id] = submission.title
        except:
            pass

# Title dictionary is then stored as a json file to prevent making HTML requests each time
with open('titles.json', 'w') as fp:
    json.dump(title_dict, fp, sort_keys=True, indent=4)   
