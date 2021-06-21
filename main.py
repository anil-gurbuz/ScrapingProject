# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from Utils import *


scraper = Car_Scrapper()
scraper.scrapeNPages(18)
print("Largest Car_Id to cont from:",scraper.car_id)

#if __name__ == '__main__':


## Get brands and number of listings for each model
li_class = "multiselect-facets-item border-bottom"


