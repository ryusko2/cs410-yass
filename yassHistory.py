################################################################################
# File:    yassHistory.py
# Author:  Ryan Yusko
# 
# Threaded history class collector that utilizes Yahoo! Finance
# 
# Additional non-base packages needed for cookie & crumb retrieval
#  (to ensure compatibility with Yahoo! finance):
#   yaml
#   requests
#
# @created 12/1/17
# @updated 12/15/17
################################################################################
import sys, threading, Queue, datetime, os.path
import urllib, yaml, io, requests, re
from yassParam import Param

dateTimeFormat = "%Y%m%d %H:%M:%S"

class yassHistory:
  def_delta = -180     #default "lookback" time is 6 months
  def_connections = 20 #default maximum number of connections/threads

################################################################################
# class HistoryThread
# Establishes a thread for loading stock history data from Yahoo!, and writes 
#  data to an appropriate subdirectory for this screen
#
# @created 12/1/17
# @updated 12/15/17
  class HistoryThread(threading.Thread):
    def __init__(self, queue, pre, hist):
      threading.Thread.__init__(self)
      self.queue = queue
      self.prefix = pre
      self.hist = hist

    def run(self):
      while 1:
        try:
          # fetch a job from the queue
          ticker, fromdate, todate = self.queue.get_nowait()
        except Queue.Empty:
          raise SystemExit
        if ticker[0] == "^": 
          tick = ticker[1:]
        else:
          tick = ticker
        filename = self.prefix + "%s.csv" % tick
        fp = open(filename, "wb")
        quote = dict()
        quote['period1'] = yassHistory.epoch_seconds(fromdate)
        quote['period2'] = yassHistory.epoch_seconds(todate)
        quote['interval'] = '1d'
        quote['events'] = 'history'
        quote['crumb'] = self.hist._token['crumb']

        #encode quote
        params = urllib.urlencode(quote)

        url = "https://query1.finance.yahoo.com/v7/finance/download/%s?%s" % \
                          (tick, params)
        try:
          data = requests.get(url, cookies={'B':self.hist._token['cookie']})
          fp.write(data.text)
        except IOError as ioe:
          self.hist.yp.log('IOError loading %s (HistoryThread.run)' % tick)
          self.hist.reload.insert(len(self.hist.reload), 
                                            (ticker, fromdate, todate))
          self.hist.info('adding %s to reload queue... (HistoryThread.run)' %
                                            tick)

        #close up & cleanup
        fp.close()
        sys.stdout.write(".")
        sys.stdout.flush()
###########################################################  class HistoryThread


################################################################################
# __init__(yp)
# Initializes yassHistory class with parameters.
#
# @param yp - Param() class from roscoParam.py containing parameters for this
#             yassHistory object.
#
# @created 12/1/17
# @updated 12/14/17
  def __init__(self, yp):
    #store a reference to the preferences
    self.yp = yp
    
    #store some basics
    self.today = datetime.datetime.now()
    self.today_str = datetime.datetime.now().strftime("%Y%m%d")
    self.lookback = self.today+datetime.timedelta(yassHistory.def_delta)
    self.lookback_str = self.lookback.strftime("%Y%m%d")
    
    #print self.today, self.today_str
    #print self.lookback, self.lookback_str
    
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
                  
    #store reference to hist directory for this week's stocks
    self.prefix = "./hist/"
                  
    #main queue for retrieving historical quotes
    self.keepers = Queue.Queue()
    
    #copy of stock data for error processing
    self.tickers = []
    
    #and data for reloading
    self.reload = []
    
    #get token from disk or yahoo
    self._token = self.loadToken()
    
    #build the queue
    self.buildQueue()
##################################################################  __init(yp)__
        
    
################################################################################
# buildQueue()
# Builds the queue for retrieving historical data from symbols in symbol list
#
# @created 12/1/17
# @updated 12/10/17
  def buildQueue(self):
    # put symbols into the queue
    for tick in self.symbols:
      self.keepers.put((tick, self.lookback_str, self.today_str))
      self.tickers.insert(len(self.tickers), 
                        (tick, self.lookback_str, self.today_str))
    
    self.yp.log('read %i symbols from %s (yassHistory.buildQueue)' % \
                    (len(self.tickers), self.yp.symbols_list))
##################################################################  buildQueue()


################################################################################
# checkFailed()
# checks the history files compiled in the hist directory to determine if any
#  are 0KB, and adds those stocks to the reload list
#
# @created 12/1/17
# @updated 12/14/17
  def checkFailed(self):
    for tick in self.tickers:
      if os.path.getsize(self.prefix + tick[0] + '.csv') == 0:
        match = False
        for sym in self.reload:
          if tick[0] is sym[0]:
            match = True
        
        #if the reload queue didn't already have the 0-sized stock, add it      
        if match == False:
          self.reload.insert(len(self.reload), tick)
    
    self.info('found %i histories to reload... (yassHistory.checkFailed)' %
                  len(self.reload))
#################################################################  checkFailed()


################################################################################
# epoch_seconds(date_string)
# Returns an integer representation of the number of seconds elapsed from the
# epoch to the passed date string (YYYYMMDD)
#
# @param date_string - date string, in format YYYYMMDD, to calculate seconds
#                      from the epoch
#
# @created 12/15/2017
# @updated 12/15/2017
  @staticmethod
  def epoch_seconds(date_string):
    dt = datetime.datetime(int(date_string[0:4]), 
                           int(date_string[4:6]), 
                           int(date_string[6:8]))
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())
####################################################  epoch_seconds(date_string)


################################################################################
# file_len(fname)
# returns the number of lines in a file
#
# @param fname = filename to check number of lines in
#
# @created 12/1/2017
# @updated 12/1/2017
  def file_len(self, fname):
    with open(fname) as f:
      for i, l in enumerate(f):
        pass
    return i + 1
###############################################################  file_len(fname)


################################################################################
# getHistory()
# gets the historical quotes based on the loaded queue (self.keepers)
#
# @created 12/2/17
# @updated 12/14/17
  def getHistory(self):
    #add directory if not already created
    if not os.path.exists(self.prefix):
      os.makedirs(self.prefix)

    num = len(self.keepers.queue)
    connections = min(yassHistory.def_connections, num)
    assert 1 <= connections <= 255, "too much concurrent connections asked"

    # start a bunch of threads, passing them the queue of jobs to do
    threads = []
    for dummy in range(connections):
      	t = self.HistoryThread(self.keepers, self.prefix, self)
      	t.start()
      	threads.append(t)
      
    self.info("waiting for history threads to finish... (yassHistory.getHistory)")
    
    # wait for all threads to finish
    for thread in threads:
      thread.join()
      
    #a little cleanup
    sys.stdout.write("\n")
    sys.stdout.flush()

    self.info('finished trying %i histories... (yassHistory.getHistory)' %
                                  num)

    #for some reason, IOErrors are not being fired off for some histories that
    # remain empty...these files show up as 0KB files in the 'hist' directory,
    # so we'll have to examine the filesystem to see which ones failed.
    self.checkFailed()
    
    while len(self.reload) > 0:
      #clear the queue
      with self.keepers.mutex:
        self.keepers.queue.clear()
      
      cnx = min(5, len(self.reload))
      self.info('trying to retrieve %i histories (yassHistory.getHistory)' %
                          len(self.reload))
      
      for stock in self.reload:
        self.keepers.put(stock)
        self.info('added %s to reload queue (yassHistory.getHistory)' % stock[0])
      
      #reset reload
      self.reload = []
      
      thr = []
      for dummy in range(cnx):
        t = self.HistoryThread(self.keepers, self.prefix, self)
        t.start()
        thr.append(t)
      
      self.info('waiting for reload threads to finish... (yassHistory.getHistory)')
      
      for thread in thr:
        thread.join()
      
      #once threads have finished, check for histories that are still failed
      self.checkFailed()
    #//while len(self.reload) > 0
##################################################################  getHistory()


################################################################################
# loadToken()
# Loads a browser token for retrieving historical data from Yahoo!...
# It prefers loading from the local stored cookie & crumb; however, it will 
# refresh the same via getToken() if refreshDays has passed.
# 
# This method adapted from Jev Kuznetsov's "Trading With Python" library:
#   www.tradingwithpython.com
# Original source:
#   https://github.com/sjev/trading-with-python/blob/3.1.1/lib/yahooFinance.py
#
# This method may be subject to distribution under a BSD License.
#
# @created 12/14/17
# @updated 12/15/17
  def loadToken(self):
    """ 
    get cookie and crumb from APPL page or disk. 
    force = overwrite disk data
    """
    refreshDays = 30 # refreh cookie every x days
    
    # set destinatioin file
    dataDir = './cookieData'
    dataFile = dataFile = os.path.join(dataDir,'yahoo_cookie.yml')
    
    try : # load file from disk
      data = yaml.load(open(dataFile,'r'))
      age = (datetime.datetime.now()- datetime.datetime.strptime(  data['timestamp'], dateTimeFormat) ).days
      assert age < refreshDays, 'cookie too old'
    except (AssertionError,IOError):     # file not found
      if not os.path.exists(dataDir):
        os.mkdir(dataDir)
      data = self.getToken(dataFile)
        
    return data
###################################################################  loadToken()


################################################################################
# getToken()
# Retrieves a token (cookie & crumb) from Yahoo! finance for storage in the
# local filesystem.
# 
# This method adapted from Jev Kuznetsov's "Trading With Python" library:
#   www.tradingwithpython.com
# Original source:
#   https://github.com/sjev/trading-with-python/blob/3.1.1/lib/yahooFinance.py
#
# This method may be subject to distribution under a BSD License.
#
# @created 12/14/17
# @updated 12/15/17
  def getToken(self, fName = None):
    """ get cookie and crumb from yahoo """
    
    url = 'https://finance.yahoo.com/quote/AAPL/history' # url for a ticker symbol, with a download link
    r = requests.get(url)  # download page
    
    txt = r.text # extract html
    
    cookie = r.cookies['B'] # the cooke we're looking for is named 'B'
    
    pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')
    
    for line in txt.splitlines():
      m = pattern.match(line)
      if m is not None:
        crumb = m.groupdict()['crumb']   
    
    assert r.status_code == 200 # check for succesful download
            
    # save to disk
    data = {'crumb': crumb, 'cookie':cookie, 'timestamp':datetime.datetime.now().strftime(dateTimeFormat)}

    if fName is not None: # save to file
      with open(fName,'w') as fid:
        yaml.dump(data,fid)
    
    return data
####################################################################  getToken()
      

################################################################################
# info()
# Simplifies print statement to log whatever we print...and then print it.
#
# @created 6/2/17
# @updated 6/2/17
  def info(self, msg):
    self.yp.log(msg)
    print msg
#####################################################################  info(msg)


if __name__ == '__main__':
#  sample = ("AAPL", "GOOG", "K", "KO")
#  
#  for row in sample:
#    self.keepers.put((row, self.lookback_str, self.today_str))
#    self.tickers.insert(len(self.tickers), 
#                           (row, self.lookback_str, self.today_str))
#
#  print 'hello'
#  yp = Param()
#  h = History(yp)
#  h.averageVolumes()
  print 'hello'
  
#//yassHistory.py