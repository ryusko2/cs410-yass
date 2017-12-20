################################################################################
# File:    yassFinviz.py
# Author:  Ryan Yusko
# 
# Class that provides an interface to retrieve data from Finviz.
# Updated to provide threaded loading of individual stocks.
#
# @created 12/5/17
# @updated 12/18/17
################################################################################
import urllib, sys, os.path, time, threading, Queue
from datetime import date
#from bs4 import BeautifulSoup
from yassFinOne import FinOne

class Finviz:

################################################################################
# class FinOneThread
# Establishes a thread for loading a single stock from finviz.com, and sends
#  selected data back to the finviz object for updating once all threads have
#  completed.
#
# @created 12/5/17
# @updated 12/18/17
  class FinOneThread(threading.Thread):
    def __init__(self, queue, pre, finviz):
      threading.Thread.__init__(self)
      self.queue = queue
      self.prefix = pre
      self.fv = finviz
      
    def run(self):
      while 1:
        try:
          sym = self.queue.get_nowait()
        except Queue.Empty:
          raise SystemExit
        
        #correction for bad input  
        if sym[0] == "^":
          sym = sym[1:]
          
        filename = self.prefix + "%s.txt" % sym
        
        #load stock data
        fv1 = FinOne(sym)
        
        try:
          #print 'retrieving FViz for %s' % row[0]
          #retrieving stock data sometimes throws IOErrors
          fv1.retrieve()
          
          self.fv.yp.log('%s: retrieved %s (FinOneThread.run)' % 
                          (sym, fv1.url))
                          
          f = open(filename, 'w')
          
          #write ratings
          for rating in fv1.rate:
            #f.write(rating)
            f.write(("%s, %s, %s\n" % (rating[0], rating[1], rating[2])).encode('utf-8'))
            
          #write news headlines
          for story in fv1.news:
            #f.write(story)
            f.write(("%s, %s\n" % (story[0], story[1])).encode('utf-8'))
            
          #close the file
          f.close()

        except IOError as ioe:
          self.fv.yp.log('IOError loading %s (FinOneThread.run)' % sym)
          #failed to load, so add this row to reload queue
          self.fv.reload.insert(len(self.fv.reload), sym)
          self.fv.info('adding %s to reload queue... (FinOneThread.run)' %
                            sym)
          #print ioe
##########################################################  class FinOneThread()


################################################################################
# __init__(yp)
# Initializes Finviz class with parameters.
#
# @param yp - Param() class from yassParam.py containing parameters for this
#             Finviz screen.
#
# @created 12/5/17
# @updated 12/16/17
  def __init__(self, yp):
    #store a reference to the preferences
    self.yp = yp
    
    #make sure symbol list exists
    try:
      assert os.path.isfile(self.yp.symbols_list), \
             "could not open symbol list %s" % yp.symbols_list
      self.yp.log('assertion os.path.isfile passed %s (yassHistory.__init__)' %
                    self.yp.symbols_list)
    except AssertionError as ae:
      self.yp.log('assertion os.path.isfile failed for %s (yassHistory.__init__)' %
                    self.yp.symbols_list)
      raise
    
    #get symbols
    self.symbols = [line.rstrip('\n') for line in open(yp.symbols_list)]
    
    #print & log number of symbols read
    print 'read %i symbols from %s...' % (len(self.symbols), yp.symbols_list)
    self.yp.log('read %i symbols from %s... (Finviz.__init__)' % (len(self.symbols), yp.symbols_list))
                  
    #store reference to hist directory for this week's stocks
    self.prefix = "./docs/"
                  
    #main queue for symbols to look up and mine
    self.keepers = Queue.Queue()
    
    #copy of stock data for error processing
    self.tickers = []
    
    #populate our data structures
    for tick in self.symbols:
      self.keepers.put(tick)
      self.tickers.insert(len(self.tickers), tick)
    
    #and data for reloading
    self.reload = []
    
    #and start mining!
    self.mineSymbols()
##################################################################  __init__(yp)
  
  
################################################################################
# mineSymbols()
# Iterates through symbols and mines data from individual pages on Finviz
#
# @created 12/5/17
# @updated 12/18/17
  def mineSymbols(self):
    if not os.path.exists(self.prefix):
      os.makedirs(self.prefix)
      
    #load maximum of 20 stocks at a time
    connections = min(20,len(self.keepers.queue))
    
    #fire off the threads
    threads = []
    for dummy in range(connections):
      t = self.FinOneThread(self.keepers, self.prefix, self)
      t.start()
      threads.append(t)

    #set up a counter and let user know we are fetching...
    cnt = 0
    #sys.stdout.write("waiting for finviz threads to finish  >>")
    #sys.stdout.flush()
    self.info("waiting for finviz threads to finish... (Finviz.mineSymbols)")
    
    #wait for all threads to finish
    for thread in threads:
      thread.join()
    
    #reload stocks that had problems
    while len(self.reload) > 0:
      cnx = min(5,len(self.reload))
      self.info('trying to reload %i stocks (Finviz.mineSymbols)' % 
                  len(self.reload))
                  
      q2 = Queue.Queue()
      
      for row in self.reload:
        q2.put(row)
        self.info("added %s to queue (Finviz.mineSymbols)" % row[0])
      
      #reset reload
      self.reload = []
      
      thr = []
      for dummy in range(cnx):
        t = self.FinOneThread(q2, self.prefix, self)
        t.start()
        thr.append(t)
      
      self.info("waiting for reload threads to finish... (Finviz.mineSymbols)")
      
      for thread in thr:
        thread.join()
    #//while len(self.reload) > 0
#################################################################  mineSymbols()
    

################################################################################
# info(msg)
# Simplifies print statement to log whatever we print...and then print it.
#
# @created 12/5/17
# @updated 12/5/17
  def info(self, msg):
    self.yp.log(msg)
    print msg
#####################################################################  info(msg)


#//yassFinviz.py