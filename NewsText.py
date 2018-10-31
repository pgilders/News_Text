#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 14:11:43 2018

Convert rtf files to txt files

Strip auxilliary information from story data

Output as separated txt files with 100,000 word limit (don't cut off articles)

Important: Change the path variable to the path to the rtf files on your computer

@author: Patrick Gildersleve
"""

import glob
import os
import subprocess

# function for splitting document into individual articles
def isplit(iterable,splitters):
    import itertools
    return [list(g) for k,g in itertools.groupby(iterable,lambda x:x in splitters) if not k]
    

path = '' ######## This will need to be changed to the path on your computer
headers = ['The Guardian\n',
           'Guardian.com.\n',
           'The Guardian - Final Edition\n',
           'The Guardian (London)',
           'The Guardian (London)\n',
           'Daily Mirror\n',
           'The Mirror\n',
           'The Times (London)\n',
           'The Sunday Times (London)\n',
           'The Times\n']

doclist = glob.glob(path+'*.rtf') #convert rtf files to txt
print('Converting %d rtf files to txt' %len(doclist))
subprocess.call("textutil -convert txt *.rtf", shell=True)
# =============================================================================
# for i in doclist:
#     #subprocess.check_output("textutil -convert txt %s/%s" %(path, i))
#     subprocess.call("textutil -convert txt %s/%s" %(path, i), shell=True)
# =============================================================================
doclist = glob.glob(path+'*.txt') # get txt files
print('%d files converted\n' %len(doclist))


ntot = 0 
print('Processing txt files')
for doc in doclist:
    print(doc)

    # Import file
    f = open(doc,"r")
    lines = f.readlines()
    f.close()

    
    # Current data being removed:
    # Document number
    # Section
    # Length
    # Load-date
    # Language
    # Publication type
    # Journal Code
    # Graphic
    # Copyright details
    # Newspaper title at the start of each article (see split later)
    
    # We are keeping:
    # Date of publication
    # Byline content
    # Article content
    # Edition information for the times & mirror
    # Location info for times & mirror
    # Calls for comment & contact details in mirror
    
    print('Stripping content')
    
    to_remove = [' DOCUMENTS\n', 'SECTION: ', 'LENGTH: ', 'LOAD-DATE: ', 'LANGUAGE: ', 'PUBLICATION-TYPE: ', 'JOURNAL-CODE: ', 'GRAPHIC: ', 'a division of Transcontinental Media Group Inc.\n', ' MGN Ltd.\n', ' Times Newspapers Limited\n']
    
    for i, item in enumerate(lines): ######## Remove unnecessary article metadata
        if item[0:8] == 'BYLINE: ': # Keep byline content, remove 'BYLINE:'
            lines[i-2] = lines[i-2][:-1]+'.\n' # Add full stop to article title       
            lines[i] = item[8:-1]+'.\n' # add full stop to byline
            
        for j in to_remove:
            if j in item:
                lines.remove(item)
    
    lines2 = [x for x in lines if x != 'All Rights Reserved\n'] # For some reason this one needed to go separately...
    
    lines3 = []
    for i, x in enumerate(lines2): ######## Remove double newline characters
        if x == '\n' and lines2[i-1] =='\n':
            pass
        else:
            lines3.append(x)
    
    print('Splitting content into different txt files')
    
    ################ Add new headers here if required
    stories = isplit(lines3, headers) ######## Split up into individual stories
    ################
        
    # Join stories, up to a limit of 100,000 words
    splittext = {0:[]}
    it = 0
    n=0
    for i in stories:
        text = ' '.join(i)
        words = text.split()
        n += len(words)
        if n < 100000:
            splittext[it].extend(i)
        elif len(words) >= 100000:
            print(len(words))
            print("###########\n"*3+"WARNING: Unexpected header, file not split correctly, may give empty output.\n"+"###########\n"*3)
        else:
            splittext[it+1]= []
            splittext[it+1].extend(i)
            it+=1
            n=len(words)         
    
    print('Writing new files to new folder\n')
    if not os.path.exists(path+'Processed'): # Make directory if required
        os.makedirs(path+'Processed')
        
    # Write to files 
    for k, v in splittext.items():
        name = path+"Processed/%s_Processed_%s" %(k, doc.split('/')[-1])
        f = open(name, "w")
        f.writelines(v)
        f.close()
    ntot += len(splittext)

print('%d files processed, %d files output' %(len(doclist), ntot))