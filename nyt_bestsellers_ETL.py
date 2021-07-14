import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import datetime as DT

weeksToSearch = 10 # how many weeks would you like to get data from

# search backwards from this date (must be +- 7 days from this date exactly)
curDate = DT.date(2021, 7, 18)

def get_data(year, month, day):
    """
    This function takes in a date in (year, month, day) format and scrapes 
    the NYT bestsellers list from that date. Returns a final list in the form:
    [[date, rank, category, title, author, # weeks on list, description]]
    """
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
    "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    # standardize date format with leading zeros if needed for the URL
    if (int(month) < 10):
        month = "0" + month
    if (int(day) < 10):
        day = "0" + day

    # request current dates NYT page for scraping
    r = requests.get("https://www.nytimes.com/books/best-sellers/" + year + "/" +  month + "/" + day, headers=headers)
    content = r.content
    soup = BeautifulSoup(content, features='lxml')

    # standardize date format
    date = str(year) + "-" + str(month) + "-" + str(day)
    rank = 1 # rank/5 for each book in the category
    categoryNum = 0
    
    FinalList = []
    categoryList = []

    # category was in a separate css section from rest of data
    for c in soup.findAll('section', attrs={'class':'e8j42380'}):
        category = c.find('a', attrs={'class':'css-nzgijy'})
        categoryList.append(category.text)

    # grab the rest of the data, clean it, and add each row to FinalList
    for d in soup.findAll('a', attrs={'class':'css-g5yn3w'}):
        title = d.find('h3', attrs={'class':'css-i1z3c1'})
        author = d.find('p', attrs={'class':'css-1nxjbfc'})
        description = d.find('p', attrs={'class':'css-5yxv3r'})
        weeks = d.find('p', attrs={'class':'css-t7cods'})
        
        workingList = []
        workingList.append(date)
        workingList.append(rank)
        rank += 1

        workingList.append(categoryList[categoryNum])

        if rank == 6:
            categoryNum += 1
            rank = 1

        if title is not None:
            workingList.append(title.text.title())
        else:
            workingList.append('Unknown')
        
        if author is not None:
            authors = author.text.split()
            # majority of text begins with "by AUTHOR NAME"
            # but some begin with "Written and Illustrated by AUTHOR NAME"
            if authors[0] == "written":
                workingList.append(authors[len(authors) - 2] + " " + authors[len(authors) - 1])
            else:
                workingList.append(author.text[3:])
        else:
            workingList.append('Unknown')

        if weeks is not None:
            weeksOnList = weeks.text.split()
            if weeksOnList[0] == "New":
                workingList.append(1)
            else:
                workingList.append(weeksOnList[0])
        else:
            workingList.append('Unknown')
        
        if description is not None:
            workingList.append(description.text)
        else:
            workingList.append('Unknown')

        FinalList.append(workingList)
    
    return FinalList




results = []
for i in range(weeksToSearch):
    results.append(get_data(str(curDate.year), str(curDate.month), str(curDate.day)))
    curDate = curDate - DT.timedelta(days = 7)

# transform data to work with pandas dataframe
results2 = [item for sublist in results for item in sublist]

df = pd.DataFrame(results2, columns=['Date', 'Rank', 'Category', 'Title', 'Author', 'Week on List', 'Description'])
df.to_csv('nyt_books.csv', index=False, encoding='utf-8')

df = pd.read_csv('nyt_books.csv')