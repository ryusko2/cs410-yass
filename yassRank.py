################################################################################
# File:    yassRank.py
# Author:  Ryan Yusko
# 
# Class that provides a basic sentiment analysis to rank the stocks from mined
# news data retrieved from Finviz.
#
# @created 12/16/17
# @updated 12/19/17
################################################################################
import os, yassMenu, metapy
from yassFinviz import Finviz
from yassParam import Param

#unicode error handling
from exceptions import UnicodeWarning 
from warnings import filterwarnings 
filterwarnings(action="error", category=UnicodeWarning)


################################################################################
# class Rank
# Analyzes and ranks each collected [mined] document.
#
# @created 12/16/17
# @updated 12/19/17
class Rank:

################################################################################
# __init__(yf,yp)
# Initializes Rank class with a preloaded yassFinviz object, and Param() object.
# The Finviz object will contain the list of symbols we are interested in.
# The Finviz object will have already placed the mined data into ./data/SYM.txt
# The Param() object is passed primarily for logging back to main program.
#
# @param yf - Finviz() object from yassFinviz.py containing symbols.
# @param yp - Param() object from yassParam.py that handles logging.
#
# @created 12/16/17
# @updated 12/18/17
  def __init__(self, yf, yp):
    #store symbols and reference to prefs (for logging)
    self.symbols = yf.symbols
    self.yp = yp
    
    #prefix for doc data
    self.doc_prefix = "./docs/"
    
    #load the positive sentiments
    self.pos = [line.rstrip('\r\n') for line in open('config/positive-words.txt')]
    self.yp.log('read %i positive sentiments (Rank.__init__)' % len(self.pos))
    
    #load the negative sentiments
    self.neg = [line.rstrip('\r\n') for line in open('config/negative-words.txt')]
    self.yp.log('read %i negative sentiments (Rank.__init__)' % len(self.neg))
    
    #dictionary for final ranking
    self.ranking = dict()
    
    #run the ranking
    self.do_ranking()
##################################################################  __init__(yf)


################################################################################
# do_ranking()
# Ranks each of the gathered data in ./docs/
#
# @created 12/18/17
# @updated 12/19/17
  def do_ranking(self):
    for tick in self.symbols:
      dat = self.doc_prefix + tick + '.txt'
      self.ranking[tick] = self.get_rank(dat)
      
    self.yp.log('ranked %i documents (Rank.do_ranking)' % len(self.ranking))
    
    #data structure for storing sorted key,value pairs
    s_ranking = list()
    
    #sort based on ranking "value"
    for key, value in sorted(self.ranking.iteritems(), key=lambda (k,v): (v,k)):
      s_ranking.append('%s: %i' % (key, value))
    
    if len(s_ranking) >= 5:
      print 'bottom 5:'
      for tick in s_ranking[:5]:
        print tick
      print 'top 5:'
      for tick in s_ranking[-5:]:
        print tick
##################################################################  do_ranking()


################################################################################
# get_rank(doc)
# Assigns a rank to the passed document based on pre-loaded sentiments
#
# @param doc - relative path with data to rank
#
# @created 12/17/17
# @updated 12/19/17
  def get_rank(self, doc):
    #rank starts at 0 :)
    rank = 0
    
    #open the file
    f = open(doc, 'r')
    
    #set up analyzer
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
    tok = metapy.analyzers.ListFilter(tok, "config/lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)
    #the Porter2Filter was not producing acceptable results
    # -> for example, it changed 'splurge' to 'splurg' as well as other changes
    #    inconsistent with natural language
    #tok = metapy.analyzers.Porter2Filter(tok)
    tok = metapy.analyzers.LowercaseFilter(tok)
    
    #set up doc content
    doc = metapy.index.Document()
    doc.content(f.read().decode('utf-8').strip())
    tok.set_content(doc.content())
    f.close()
    
    #analyze away!
    ana = metapy.analyzers.NGramWordAnalyzer(1, tok)
    vec = ana.analyze(doc)
    
    #check it out
    for word in vec:
      try:
        if word in self.pos:
          rank += vec[word]
        elif word in self.neg:
          rank -= vec[word]
      except UnicodeWarning as uw:
        #we don't care about non-interpretable characters, so continue
        continue  
      
    return rank
#################################################################  get_rank(doc)


################################################################################
# get_rank(doc) <static>
# Assigns a rank to the passed document based on pre-loaded sentiments
# This method loads the positive & negative sentiments separately...and should
#  really only be used for testing, since the constructor stores these 
#  sentiments in memory for constant access; class method should be used for
#  regular implementation.
#
# @param doc - relative path with data to rank
#
# @created 12/18/17
# @updated 12/19/17
  @staticmethod
  def get_rank(doc):
    pos = [line.rstrip('\r\n') for line in open('config/positive-words.txt')]
    neg = [line.rstrip('\r\n') for line in open('config/negative-words.txt')]
    
    #rank starts at 0 :)
    rank = 0
    
    #open the file
    f = open(doc, 'r')
    
    #set up analyzer
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
    tok = metapy.analyzers.ListFilter(tok, "config/lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)
    #the Porter2Filter was not producing acceptable results
    # -> for example, it changed 'splurge' to 'splurg' as well as other changes
    #    inconsistent with natural language
    #tok = metapy.analyzers.Porter2Filter(tok)
    tok = metapy.analyzers.LowercaseFilter(tok)
    
    #set up doc content
    doc = metapy.index.Document()
    doc.content(f.read().decode('utf-8').strip())
    tok.set_content(doc.content())
    f.close()
    
    #analyze away!
    ana = metapy.analyzers.NGramWordAnalyzer(1, tok)
    vec = ana.analyze(doc)
    
    #check it out
    for word in vec:
      try:
        if word in pos:
          rank += vec[word]
        elif word in neg:
          rank -= vec[word]
      except UnicodeWarning as uw:
        #we don't care about non-interpretable characters, so continue
        continue  
      
    return rank
########################################################  get_rank(doc) <static>


################################################################################
# __main__
# This stub created for testing purposes.
#
# @created 12/17/17
# @updated 12/18/17
if __name__ == '__main__':
  yp = Param()
  print yassMenu.getHeader(yp.version, yp.versionDate)
  
  print 'AAPL rank: %i' % Rank.get_rank('docs/AAPL.txt')
  print 'GOOG rank: %i' % Rank.get_rank('docs/GOOG.txt')
######################################################################  __main__


#//yassRank.py