import csv
from os import system
from tkinter.messagebox import NO
import requests
import bs4
import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
import datetime

def sold_in_last_month(dte_obj_skimmed):
    #calculate how many were sold in last month
    sold_in_last_month = 0
    for i,element in enumerate(dte_obj_skimmed):
        sold_in_last_month += 1
        if i==0:
            dte_last_sold = element
            dte_last_sold = dte_last_sold.replace(month= dte_last_sold.month-1)
        else:
            if(dte_last_sold > element):
                break
            
    return sold_in_last_month
"""
Program poisce zadnjih 200 dražb in naredi statistiko
"""
# parser = argparse.ArgumentParser(description='Process a list of search terms.')
# parser.add_argument('terms', metavar='N', type=str, nargs='+',
#                    help='comma separated list of terms to search for')

# args = parser.parse_args()
# print args.accumulate(args.terms)

# enter multiple phrases separated by '',
phrases =['ryzen+3600']
filter_price = [40, 110]
hist_range = [70, 140 ]
take_last_n = 50

for phrase in phrases:
    site = 'http://www.ebay.de/sch/i.html?_from=R40&_nkw='+phrase+'&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&LH_Auction=1&_samilow=&_samihi=&_sadis=15&_stpos=90278-4805&_sargn=-1%26saslc%3D1&_salic=1&_sop=13&_dmd=1&_ipg=200&LH_Complete=1'
    site = site +"&LH_ItemCondition=1000%7C1500%7C2500%7C3000"
    print(site)
    #raise SystemExit()
    # item condition 7000 = defekt
    res = requests.get(site)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "lxml")

  
    # grab the date/time stamp of each auction listing
    #dte = ["2020. " + e.span.contents[0] for e in soup.find_all(class_="POSITIVE")] #.split(' ')[0]
    dte = [e.find(class_="POSITIVE").contents[0].strip("Verkauft ") for e in soup.find_all("div", {"class":"s-item__title--tagblock"})]
    #dte_obj = [datetime.datetime.strptime(element, "%Y. %d. %b. %H:%M") for element in dte]
    dte_obj = [datetime.datetime.strptime(element, "%d. %b %Y") for element in dte]
    
    # grab all the links and store its href destinations in a list
    #titles = [e.contents[0] for e in soup.find_all(class_="vip")]
    titles = [e.find("span").contents[0] for e in soup.find_all(class_="s-item__title s-item__title--has-tags")]
    
    

    # grab all the links and store its href destinations in a list
    #links = [e['href'] for e in soup.find_all(class_="vip")]
    links = [e.find("a")["href"] for e in soup.find_all("div", {"class":"s-item__wrapper clearfix"})]
    links = links[len(links)-len(titles):]


    # grab all the bid spans and split its contents in order to get the number only
    #bids = [int(e.span.contents[0].split(' ')[0]) for e in soup.find_all("li", "lvformat")]
    bids = [int(e.contents[0].rstrip(" Gebote")) for e in soup.find_all("span", {"class": "s-item__bids s-item__bidCount"})]

    # grab all the prices and store those in a list
    #prices = [float(e.contents[1].replace(".","").replace(",", ".")) for e in soup.find_all("span", "bold bidsold")]
    span_container = soup.find_all("span", "s-item__price")
    prices = []
    for e in span_container:
        price = e.find("span", "POSITIVE")
        if(price is not None):
            prices.append(float(price.contents[0].strip("EUR ").replace(",", ".")))
        
    # zip each entry out of the lists we generated before in order to combine the entries
    # belonging to each other and write the zipped elements to a list
    l = [e for e in zip(dte, titles, links, prices, bids)]

items_below = 0
prices_skimmed = []
bids_skimmed = []
dte_skimmed = []
dte_obj_skimmed = []

for i, item in enumerate(l):
    if filter_price[0] < prices[i] < filter_price[1]:
        items_below += 1
        print("%d. price=%.2f, bids=%d,\nurl=%s" %(i, prices[i], bids[i], links[i]))
    if bids[i] > 0:
        prices_skimmed.append(prices[i])
        bids_skimmed.append(bids[i])
        dte_skimmed.append(dte[i])
        dte_obj_skimmed.append(dte_obj[i])
        
sold_last_month = sold_in_last_month(dte_obj_skimmed)
    
plt.figure(1)
plt.title("Price distribution, N = %d" %len(prices_skimmed[:take_last_n]))
plt.hist(prices_skimmed[:take_last_n], bins=np.arange(hist_range[0], hist_range[1], 2))

correlation = pearsonr(bids_skimmed, prices_skimmed)

plt.figure(2)
plt.scatter(bids_skimmed, prices_skimmed)
plt.ylim(hist_range[0], hist_range[1])
plt.title("bids vs price, p = %.2f" %correlation[0])


plt.figure(3)
plt.title("Price vs item")
plt.ylim(hist_range[0], hist_range[1])
plt.scatter(np.arange(0, len(prices_skimmed)), prices_skimmed)

print("\nFound %d items." %len(l))
print("Correlation between bid and price = %0.2f" %correlation[0])
print("Since %s, %d were sold" %(dte_skimmed[take_last_n], take_last_n))
print("Last month were sold %d items:" %sold_last_month)
print("Mean price: %0.2f, std: %0.2f, low price: %0.2f" %(np.mean(prices_skimmed), np.std(prices_skimmed), np.mean(prices_skimmed)-np.std(prices_skimmed)))
plt.show()