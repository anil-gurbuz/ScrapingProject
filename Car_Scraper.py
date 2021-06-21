from lib import *
from Utils import downSizeImage, uploadFileToS3

SAVE_DIR_PATH = "."
INITIAL_URL = "https://www.carsales.com.au"
CAR_FEATURES_CSS_CLASS = "col features-item-value features-item-value-"
CAR_FEATURES = ["network-id", "vehicle", "price", "kilometers", "colour", "interior-colour", "transmission", "body", "engine", "model-year", "fuel-consumption-combined"]
INITIAL_HEADERS = {
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

class Car_Scrapper(requests.Session):
    def __init__(self,init_url=INITIAL_URL, car_features=CAR_FEATURES, features_class=CAR_FEATURES_CSS_CLASS, init_headers=INITIAL_HEADERS, dir_path=SAVE_DIR_PATH, brand="Audi", model="a1"):
        super().__init__() # Inherite methods and attributes of requests.Session class

        self.car_features = car_features
        self.features_class = features_class
        self.df = pd.DataFrame(columns=["brand", "model", "car_id"]+car_features)
        self.dir_path = dir_path


        self.headers = init_headers
        self.filter_page_url = init_url
        self.path = "/"

        self.listing_page_response = None     # HTML request response object
        self.listing_page_soup = None         # Parsed HTML file
        self.filter_page_response = None
        self.filter_page_soup = None

        self.listing_links = []

        self.brand = brand
        self.model = model
        self.car_id = 1


    def goToCars(self):
        self.headers["path"] = "/cars/"
        self.headers["referer"] = self.filter_page_url
        self.filter_page_url += "/cars"

    def filterBrandModel(self):
        self.headers["path"] = "/cars/" + self.brand + "/" + self.model + "/"
        self.headers["referer"] = self.filter_page_url
        self.filter_page_url += "/" + self.brand + "/" + self.model


        self.filter_page_response = self.get(self.filter_page_url)
        self.filter_page_soup = BeautifulSoup(self.filter_page_response.text, "html.parser")


    def filterBrandOnly(self):
        self.headers["path"] = "/cars/" + self.brand + "/"
        self.headers["referer"] = self.filter_page_url
        self.filter_page_url += "/" + self.brand


        self.filter_page_response = self.get(self.filter_page_url)
        self.filter_page_soup = BeautifulSoup(self.filter_page_response.text, "html.parser")

    def scrapeListingLinks(self):
        listing_carousel_tags =  self.filter_page_soup.find_all("a", class_="carousel slide lazy js-encode-search")

        self.listing_links = []
        for listing in listing_carousel_tags:
            self.listing_links.append("https://www.carsales.com.au/" + listing["href"])

    def requestListingPage(self, url):

        path = re.search("/cars/details/.*", url)
        if path:
            self.headers["path"] = path.group()

        self.headers["referer"] = self.filter_page_url

        self.listing_page_response = self.get(url)
        # MIGHT ASSERT response 200 HERE
        assert self.listing_page_response.status_code == 200, f"Listing page request returned {self.listing_page_response.status_code}"

        self.listing_page_soup = BeautifulSoup(self.listing_page_response.text, "html.parser")

    def getCarDetails(self, class_start="col features-item-value features-item-value-"):

        row = [self.brand, self.model, self.car_id]

        # For each attribute search the document and find the relevant element
        for attr in self.car_features:
            element = self.listing_page_soup.find(class_=class_start + attr)

            try:
                row.append(element.string.strip())

            # If element or element string doesn't exists then try looking for span
            except AttributeError:
                try:
                    row.append(element.find("span").string.strip())
                except AttributeError:
                    row.append(None)

        self.df.append(dict(zip(["brand", "model", "car_id"] + self.car_features, row)), ignore_index=True)

    def _getImageLinksFromListing(self):

        # Find javascripts within HTML
        scripts = self.listing_page_soup.find_all("script")

        image_urls = []

        # How many scripts have "var gallery_data". If bigger than 1, then structure might be different
        counter = 0

        # Iterate over scripts and select the one contains image urls
        for script in scripts:
            # Make sure exists only in 1 script
            if re.search("var gallery_data", str(script.string)):
                counter += 1
                j = json.loads(re.search("{.*}", str(script.string)).group())
                for image in j["media"]:
                    # Save image urls
                    image_urls.append(image["contentUrl"])

        assert counter == 1, "There are more than one JavaScript in the HTML having 'var gallery_data' "

        return image_urls

    def saveImages(self, image_urls, to_cloud=True):

        brand_path = self.dir_path + "/" + self.brand
        model_path = self.brand + "/" + self.model

        # Create directory for car brand and model if doesn't exists already
        if not to_cloud:
            brand_path = os.path.join(self.dir_path, self.brand)
            model_path = os.path.join(self.brand, self.model)
            if not os.path.isdir(brand_path):
                os.mkdir(brand_path)
                os.mkdir(model_path)
            else:
                if not os.path.isdir(model_path):
                    os.mkdir(model_path)



        for i, img_url in enumerate(image_urls):
            # Request image and save
            response = requests.get(img_url)

            cropped_images = downSizeImage(response.content, new_size=512)
            for j, im in enumerate(cropped_images):

                if to_cloud:
                    file_path = model_path + "/" + f"{self.car_id}_{i}_crop_{j}.jpeg"
                    in_mem_file = io.BytesIO()
                    im.save(in_mem_file, format="JPEG")
                    in_mem_file.seek(0)
                    uploadFileToS3(in_mem_file, file_path)

                else:
                    file_path = os.path.join(model_path, f"{self.car_id}_{i}_crop_{j}.jpeg")
                    im.save(file_path, format="JPEG")

            # Sleep for 3 seconds before making another request
            time.sleep(3)

    def scrapeOneListing(self, link) -> None:
        self.requestListingPage(link)
        image_urls = self._getImageLinksFromListing()
        self.saveImages(image_urls)
        self.getCarDetails()

        self.car_id +=1


    def scrapePageOfListings(self):
        self.scrapeListingLinks()

        for listing_url in self.listing_links:
            self.scrapeOneListing(listing_url)

    def scrapeNPages(self, N):

        self.goToCars()
        self.filterBrandModel()
        self.scrapePageOfListings() # Scrape first page of listings


        i=1
        while i < N:

            if self.filter_page_url.find("?offset") == -1:
                self.filter_page_url += "/?offset=12"
                self.scrapePageOfListings()

            else:
                offset_val = re.search("(?<=\?offset=)[0-9]*$",self.filter_page_url).group() # Extract Offset value from the url
                new_val = str(int(offset_val) + 12) # Add 12 to represent next page of listings
                self.filter_page_url = re.sub("(?<=\?offset=)[0-9]*$", new_val, self.filter_page_url) # Replace new offset to existing one

                self.scrapePageOfListings()

            logging.info(f"Scraped {i} pages.")
            i+=1



