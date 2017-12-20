################################################################################
# File:    yassFinOne.py
# Author:  Ryan Yusko
# 
# Class that provides an interface to retrieve single quote data from Finviz.
#
# @created 12/16/17
# @updated 12/18/17 - Added base url retrieval method for building html
################################################################################
import urllib
from bs4 import BeautifulSoup

class FinOne:
  base_url = "https://finviz.com/quote.ashx?t=ZZZZ&ty=c&ta=1&p=d&b=1"
  
################################################################################
# __init__(symbol)
# Initializes FinOne class with passed stock.  Defaults to AAPL.
#
# @param symbol - Symbol to look up
#
# @created 12/16/17
# @updated 12/16/17
  def __init__(self, symbol='AAPL'):
    #replace AAPL with the symbol we are looking for
    self.url = FinOne.stockUrl(symbol)
##############################################################  __init__(symbol)


################################################################################
# retrieve()
# Retrieves rankings and news stories for this FinOne object.
# This functionality was moved into a separate method so that FinOne objects 
#  could be created simply to retrieve the finviz url for individual stocks.
# After this method is called, the data members 'rate' and 'news' should be 
#  available to access the respective statistics.
#
# @created 12/16/18
# @updated 12/18/17
  def retrieve(self):
    #retrieve the web page
    html = urllib.urlopen(self.url).read()
    
    #soup it up
    soup = BeautifulSoup(html, "html.parser")
    
    #store titles & values
    ratings = soup.findAll("td", "fullview-ratings-inner")
    
    #set up list of rankings
    self.rate = list()
    
    #load up ratings for retrieval
    for item in ratings:
      for row in item.table.find_all('tr'):
        col = item.table.find_all('td')
      self.rate.append([col[0].text, col[1].text, col[3].text])
      
    #get news table
    news_table = soup.findAll("table", {"id":"news-table"})
    
    #set up list of news
    self.news = list()
    
    #placeholder date
    date = 'Jan-00-00'
    
    #build out news list
    for table in news_table:
      for story in table.find_all('tr'):
        if story.td.text[0].isalpha():
          date = story.td.text.split(' ')[0]
        self.news.append([date, story.a.text])
####################################################################  retrieve()
    
    
################################################################################
# stockUrl(symbol)
# Returns the finviz url to the query page for the passed symbol
#
# @param symbol - stock you would like to see the url for
#
# @created 12/16/17
# @updated 12/16/17
  @staticmethod
  def stockUrl(symbol):
    return (FinOne.base_url.replace('ZZZZ', symbol))
##############################################################  stockUrl(symbol)
    
#//yassFinOne.py