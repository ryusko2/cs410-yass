################################################################################
# File:    yassParam.py
# Author:  Ryan Yusko
# 
# Class that encompasses some common parameters.
#
# @created 12/1/17
# @updated 12/14/17
################################################################################
from datetime import date, timedelta, datetime, time
import os.path

class Param:
#   def_delta = 18 # default window (days) for analysis...ends up being the Friday
#                  # following 3 full trading weeks
                
################################################################################
# __init__(db)
# Initializes a bunch of parameters to default based on current date & time
# Also compiles basic statistics on the database for the default object's
#   trading period.
#
# @param symbols  - list to open containing symbols
#
# @created 12/1/17
# @updated 12/4/17
  def __init__(self, symbols=False):
    self.verbose_logging = False
    self.version = 0.015
    self.versionDate = date(2017, 12, 19)
    if symbols == False:
      self.symbols_list = 'symbols.txt'
    else:
      self.symbols_list = symbols
    
    #store stats in a dict  
    self.stats = dict()
    
    #tally stocks in db if the db exists
    #if os.path.isfile(self.symbols_list):
    #  self.countStocks()
    
    self.log_name = "%s.log" % date.strftime(datetime.now(), "%Y%m%d_%H%M%S")
    self.log_file = open("logs/"+self.log_name, 'w')
    self.log('opened log file %s (Param.__init__)' % self.log_name)
#############################################################  __init__(ver, db)
    
    
################################################################################
# __del__()
# Destructor.
# Closes log file upon object destruction.
#
# @created 12/1/17
  def __del__(self):
    if not self.log_file.closed:
      self.log('closing log file %s (Param.__del__)' % self.log_name)
      self.log_file.close()
#####################################################################  __del__()
    
    
################################################################################
# closeLog()
# Closes the log file and returns the relative reference to said file.
# Used in "auto" mode to provide log for emailing.
#
# @created 12/1/17
  def closeLog(self):
    if not self.log_file.closed:
      self.log('closing log file %s (Param.closeLog())' % self.log_name)
      self.log_file.close()
    return "logs/" + self.log_name
####################################################################  closeLog()


################################################################################
# getNewDate(ref)
# Attempts to get a new date from the user, prompting for month, day, & year
# Default values are provided based on the passed date object (ref)
#
# @param ref - date object from which to derive default values
#
# @created 12/1/17
  def getNewDate(self, ref):
    M = ref.month
    D = ref.day
    Y = ref.year
    try:
      m = raw_input('enter new month [%i]: ' % M)    #get month
      if m != '': M = int(m)# if input is not blank, try to interpret the response
      d = raw_input('enter new day [%i]: ' % D)      #get day
      if d != '': D = int(d)# if input is not blank, try to interpret the response
      y = raw_input('enter new year [%i]: ' % Y)     #get year
      if y != '': Y = int(y)# if input is not blank, try to interpret the response
    
      # if we made it this far successfully, return a new date object
      return date(Y,M,D)
    except ValueError:
      print 'error crunching numbers...please select again...'
###############################################################  getNewDate(ref)


################################################################################
# log(note)
# Logs the passed string to the log for this instance of preferences
#
# @param note - string to put into the log
#
# @created 12/1/17
  def log(self, note):
    self.log_file.write('%s: %s\n' % (datetime.now().isoformat(), note))
#####################################################################  log(note)


################################################################################
# log_string()
# Closes the log and returns a string representation of its contents.
#
# @created 12/1/17
  def log_string(self):
    body = ''
    log_path = self.closeLog()
    #log_file = open(log_path, 'r')
    with open(log_path, 'r') as log_file:
      body = log_file.read()
    return body
##################################################################  log_string()


#//yassParam.py