# YASS ~ Yet Another Stock Screener
## CS410 - Text Information Systems

by Ryan Yusko

*ryusko2@illinois.edu*

This project created for CS410 - Text Information Systems with several 
goals in mind:

- Provide *freely available* and *reliable* access to historical stock data
- Mine buy/sell recommendations and related news headlines for individual 
stocks of interest
- Perform a basic sentiment analysis based on mined data, and rank top 5 and 
bottom 5 stocks from the list provided

YASS was developed on Python 2.7.14.  It utilizes several standard libraries:

- sys, os, datetime, time, io, re
- threading, Queue, urllib

YASS also requires several external libraries, depending on which functionality
you plan on using:

- metapy
- BeautifulSoup 4 (included in repository)
- pyyaml, requests (required for historical data retrieval)

### YASS primary files:

- yass.py ~ main control flow; sets up parameters
- yassMenu.py ~ menu utility class, and nothing else
- yassParam.py ~ parameters are set up and stored here
- yassFinOne.py ~ worker class for a single stock symbol, retrieved from [finviz.com](http://www.finviz.com)
- yassFinviz.py ~ creates threads and manages querying and retrieval from [finviz.com](http://www.finviz.com) (via FinOne)
- yassHistory.py ~ creates threads and manages historical data retrieval from ~~Google~~ [Yahoo! Finance](https://finance.yahoo.com/)
- yassRank.py ~ analyzes and ranks mined data

### Installation

- Clone from git repository
    - git@github.com:ryusko2/cs410-yass.git
    - https://github.com/ryusko2/cs410-yass.git
- Install external dependencies (via pip, for example)
    - metapy
    - pyyaml, requests (if utilizing historical data retrieval)
    
### Usage

`python yass.py {file=symbols.txt}`

- YASS will look for stock symbols in symbols.txt by default, if no arguments 
are passed
    - repository’s symbols.txt is pre-populated with 14 symbols
- Or, specify your own list of symbols
    - one symbol per line
    - no comments or special characters

*Optional historical data retrieval*

Look in yass.py for the following code:

```python
#uncomment the following line to load previous 6-months of historical data
#  into individual csv files in ./hist/
#yh = yassHistory(yp)
```

...and uncomment the appropriate line to retrieve the historical data.

### Acknowledgements

Sentiment analysis provided by Bing Liu

- [https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html](https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html)

Cookie/crumb functionality to retrieve historical data from 
[Yahoo! Finance](https://finance.yahoo.com) adapted from Jev Kuznetsov's 
[Trading with Python Library](http://www.tradingwithpython.com)