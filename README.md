# Reddit Title Generator
Takes posts found in a pubicly available Reddit dataset and attempts to generate titles for the posts using the comments.

## How It Works
### Title Extraction
The dataset used for the project was considered incomplete as it did not contain titles for each comment to be included once comments were
grouped. To fix this, *title_extraction* is a script that uses the PRAW (Python Reddit API Wrapper) to make HTML requests to retrieve the
title for each post, these titles are held in a dictionary in the form link_id -> title and stored as a json file to be used later.

### Comment Grouping
After the titles have been extracted, the data file is loaded in along with the dictionary for titles. The data is read line by line and 
the comment is added to a dictionary with its associated title. Once this is completed a dictionary of title -> list of comments is 
written to a json file. This will be the main dataset used for the title generation.

### Template Test
This file is a script that was used for brainstorming and experimentation. The structure of the script is crude and some lines are
commented out but included regardless to show the thought process. Reddit titles were POS tagged after tokenization and their complete 
structure and the total occurrence of POS tags were counted to find common occurrences for insight in the creation of a good template.

### TextRank Baseline
*textrank_baseline* is the first method for title generation. A naive implementation acting more as an opportunity to gain experience with
the data and alogrithms used in the project. The dataset created in *comment_grouping* is loaded and is used with TextRank, the main 
algorithm used in title generation for this project. The implementation of TextRank was provided by David Adamo 
(link provided at the top of the file). The provided code was modified and outfitted to use the dataset provided. TextRank was run
for sentence summarization and only the top sentence was returned and used as the title. The original title and generated title are both 
written to a file for each post in the dataset in the following structure:

ORIGINAL TITLE: ...  
GENERATED TITLE: ...

### TextRank Template
*textrank_template* is the second method of title generation. This method attempts to improve on the original by straying from 
summarization and attempting to "create" sentences. TextRank is used here again except now for extracting keywords rather than 
summarizing sentences. The keywords are extracted and returned in descending order (based on PageRank). The keywords are POS tagged and 
put into a list based on their POS category (maintaining relative ranking). The top word for each POS category is chosen to be placed 
in a position based on a sentence template, the structure of which was decided by results found in *template_test*. If the top word 
for a POS was used and the same POS appears again in the template, the next highest keyword is used. The original title and generated 
title are then both written to a file again in the same structure as *textrank_baseline*.

## Additional Details
A comprehensive description of the steps taken in doing this project along with all cited sources can be found in the *report* PDF 
document.

## Author
* Mohammad Qureshi
