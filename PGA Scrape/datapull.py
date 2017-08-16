#pip3 install lxml
#pip3 install BeautifulSoup4
#pip3 install pandas

import os
import csv
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd


#gets URLS based
#year is a number in 20xx format
#stat_index is a list of statistics desired (ex 101, 102, 103)
def get_links(year, stat_index):
    urls = []
    base_url = "http://www.pgatour.com/stats/stat."

    if year == 2017:
        stryear = ""
    else:
        stryear = str(year)

    for i in range(len(stat_index)):
        url_add = base_url+str(stat_index[i])+stryear+".html"
        urls.append(url_add)
    return urls

#finds data from a given URL
def scrape_pga_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    #now find the headers for the table, save as heads
    heads = soup.find('thead').find_all('th')
    #init pandas df
    data = []
    cols = [heads[i].get_text() for i in range(len(heads))]

    #now find and save the body of the table
    body = soup.find('tbody').find_all('tr')
    for i in range(len(body)):
        row = body[i].find_all('td')
        data.append([row[i].get_text().replace(u'\xa0', u' ').strip() for i in range(len(row))])

    return pd.DataFrame(data, columns=cols)

#CSV location is a string
#gets a list of stat indexes from csv file
def get_stat_index(csv_location):
    data = pd.read_csv(csv_location, names=['statname', 'stat'])
    stat_index = data.stat.dropna()
    stat_index = stat_index[1:].tolist()
    return stat_index



#Year = year to get stats for
def get_stats_csv(csv_location = 'statindex.csv', year=2017, sep_folders=False):
    print("Running Get Stats [CSV]...")
    stat_index = get_stat_index(csv_location)
    print("Stat Indexes Found...")
    print("Getting URLs...")

    urls = get_links(year, stat_index)

    print("{} URLs Found...".format(len(urls)))
    print("Processing URLs...")
    data = pd.DataFrame()
    for i in range(len(urls)):
        data = scrape_pga_data(urls[i])
        #write CSV using stat_index[i] as title
        if(sep_folders):
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, str(year))
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)
            csv_file_path = str(year)+"/"+str(stat_index[i])+"_"+str(year)+".csv"
        csv_file_path = str(stat_index[i])+"_"+str(year)+".csv"
        data.to_csv(csv_file_path)


def get_multiyear_stats_csv(years):
    for i in years:
        print("Finding Stats for {}".format(i))
        get_stats_csv('statindexes.csv', i)

def main():
    get_stats_csv('statindexes.csv',2016)
    #years = [2011,2012,2013,2014,2015]
    #get_multiyear_stats_csv(years)

if __name__ == "__main__":
    main()
