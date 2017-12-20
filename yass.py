################################################################################
# File:    yass.py
# Author:  Ryan Yusko
# 
# yet another stock screener
#
# @created 12/1/17
# @updated 12/15/17
import yassMenu, sys
from yassParam import Param
from yassHistory import yassHistory
from yassFinviz import Finviz
from yassRank import Rank

#default input file is symbols.txt
input = 'symbols.txt'

#if more than 2 arguments are in sys.argv, something is not right
if len(sys.argv) > 2:
  print 'usage: place list of relevant symbols in symbols.txt,\n' + \
      'one symbol per line.\n' + \
      'usage: python yass.py {file.txt}'
  exit(1)
#else if user passed an input file, use that one instead of symbols.txt
elif len(sys.argv) == 2:
  input = sys.argv[1]

#get a parameter object
yp = Param(input)

#print header
print yassMenu.getHeader(yp.version, yp.versionDate)

try:
  #uncomment the following line to load previous 6-months of historical data
  #  into individual csv files in ./hist/
  #yh = yassHistory(yp)
  
  #get a Finviz object based on the parameters
  yf = Finviz(yp)
  
  #analyze & rank
  yr = Rank(yf, yp)
except AssertionError as ae:
  print 'usage: place list of relevant symbols in symbols.txt,\n' + \
        'one symbol per line.\n' + \
        'usage: python yass.py {file.txt}'
  exit(1)
        
#yh.getHistory()