# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#"sec-ch-ua": ["Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"  ],
# "cookie": "csncidcf=234CA92F-FAB2-4A0B-9289-FF0492940C7E; csnclientid=519AFD3C-44DA-48D6-98AA-97C0599E9E0A; cidgenerated=1; cmp.ret.enq.afgtoken=CfDJ8Efs2BAxx71EoBhTrHnI3sO9Y914fS7wjxE5cIX4j_5x2bCJN4AChVblJ3ntIfiIHxQT9gRcQ-1OFI5eHZzWs-7OvSprlT64rP04ndyzw7OSJ8qVICL3MfQxAl4CsB62aKlhPqvmts34Vb28F-YA7OM; DeviceId=0079107e-fc80-44b6-a153-018be732e028; csn.bi=1623498427342; datadome=_1NVuwPgtSeIPaNQZMx8OkWxsIPngniDsSwxckSwa7~Lu2PTLC.o_NCKXddTgsfI-z_WxkzbLAibRg6uo~nQEhPQgOOKR5KS4luxgNIFbD; a360Fb=true",
#  "path": "/cars/details/2015-audi-a3-attraction-auto-my15/OAG-AD-19806093/?Cr=0&gts=OAG-AD-19806093&gtsSaleId=OAG-AD-19806093&gtsViewType=topspot&rankingType=topspot",

from lib import *
from Car_Scraper import Car_Scrapper, INITIAL_HEADERS, INITIAL_URL


HEADERS["path"] = "/cars/"
HEADERS["referer"] = "https://www.carsales.com.au/"
# Check HEADERS["cookie"]

url = "https://www.carsales.com.au/cars/details/2011-audi-a1-ambition-auto-my12/SSE-AD-7268624/?Cr=0"


# Get the page HTML and Parse
r = requests.get(INITIAL_URL, headers=INITIAL_HEADERS)
soup = BeautifulSoup(r.text, "html.parser")

def getCarDetails(soup, brand, model,  car_id,  attributes=ATTRIBUTES , class_start = "col features-item-value features-item-value-"):

    row = [brand, model, car_id]

    # For each attribute search the document and find the relevant element
    for attr in attributes:
        element = soup.find(class_=class_start + attr)

        try:
            row.append(element.string.strip())

        # If element or element string doesn't exists then try looking for span
        except AttributeError:
            try:
                row.append(element.find("span").string.strip())
            except AttributeError:
                row.append(None)

    return tuple(row)


def getImageLinks(soup) -> list:

    # Find javascripts within HTML
    scripts = soup.find_all("script")

    car_image_urls = []

    # How many scripts have "var gallery_data". If bigger than 1, then structure might be different
    counter =0

    # Iterate over scripts and select the one contains image urls
    for script in scripts:
        # Make sure exists only in 1 script
        if re.search("var gallery_data", str(script.string)):
            counter +=1
            j = json.loads(re.search("{.*}", str(script.string)).group())
            for image in j["media"]:
                # Save image urls
                car_image_urls.append(image["contentUrl"])

    assert counter ==1, "There are more than one JavaScript in the HTML having 'var gallery_data' "

    return car_image_urls


def saveImages(urls:list, brand, model, car_id)->None:

    brand_path = os.path.join(SAVE_DIR_PATH, brand)
    model_path = os.path.join(brand, model)

    # Create directory for car brand and model if doesn't exists already
    if not os.path.isdir(brand_path):
        os.mkdir(brand_path)
        os.mkdir(model_path)
    else:
        if not os.path.isdir(model_path):
            os.mkdir(model_path)


    for i, img_url in enumerate(urls):
        # Request image and save
        ##### MIGHT TRY AND HANDLE WHAT HAPPENS IF BANNED #########
        response = requests.get(img_url)
        file_path = os.path.join(model_path, f"{car_id}_{i}.png")
        file = open(file_path, "wb")
        file.write(response.content)
        file.close()
        # Sleep for 3 seconds before making another request
        time.sleep(3)


def scrapeOneListing(listing_page_url, brand, model, car_id) -> None:
    # Request listing page html
    ##### MIGHT TRY AND HANDLE WHAT HAPPENS IF BANNED #########
    listing_page_html = requests.get(listing_page_url, headers=HEADERS)

    # Parse HTML file
    soup = BeautifulSoup(listing_page_html.text, "html.parser")

    # Get car image links from parsed HTML
    car_image_urls = getImageLinks(soup)
    # Request images form the links and save
    saveImages(car_image_urls, brand, model, car_id)

    # Get car details as a tuple to save in a DF
    row = getCarDetails(soup, brand, model, car_id)

    return row





listings_url = "https://www.carsales.com.au/cars/audi/a1/"

HEADERS = {
"authority": "www.carsales.com.au",
"path": "/",
"sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
"method": "GET",
"scheme": "https",
"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9",
"cache-control": "max-age=0",
"sec-ch-ua-mobile": "?0",
"sec-fetch-dest": "document",
"sec-fetch-mode": "navigate",
"sec-fetch-site": "none",
"sec-fetch-user": "?1",
"upgrade-insecure-requests": "1",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
}



# Initiate Session Object and go to home page
s = requests.Session()
s.headers = HEADERS
url= "https://www.carsales.com.au"
r = s.get(url)

# Modify Headers and go to /cars/ page
HEADERS["path"] = "/cars/"
HEADERS["referer"] = "https://www.carsales.com.au/"
url ="https://www.carsales.com.au/cars/"
r = s.get(url)



####
soup = BeautifulSoup(r.text, "html.parser")



##### Modify Headers and filter based on Make and model
HEADERS["path"] = "/cars/audi/a1/"
HEADERS["referer"] = "https://www.carsales.com.au/cars"
url ="https://www.carsales.com.au/cars/audi/a1"
r = s.get(url)


#####
cls = "listing-item card showcase"

def initiateSessionGoToCars(initial_headers):
    # Initiate session and assign headers
    s = requests.Session()
    s.headers = initial_headers

    # Go to Homepage
    r = s.get("https://www.carsales.com.au")

    #



def scrapeOnePageOfListings():
    pass

def scrapeOneModel():
    pass

def scrapeOneBrand():
    pass

def scrapeAll():
    pass


scraper = Car_Scrapper()
scraper.goToCars()
scraper.filterBrandModel()
scraper.scrapeListingLinks()



#if __name__ == '__main__':
