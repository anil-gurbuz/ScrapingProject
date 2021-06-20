
from lib import *
from Car_Scraper import Car_Scrapper, INITIAL_HEADERS, INITIAL_URL

def get_brands_tags(tag):
    if tag.name == "a" and tag.has_attr("href"):
        if tag["href"].startswith("/cars/?q=(Or.(C.Make.Audi._.Model.A1.)_.Make"):
            return True
    return False


def get_model_tags(tag):
    brand = "Audi" # Must be modified based on brand model
    model = "A1"
    if tag.name == "a" and tag.has_attr("href"):
        if tag["href"].startswith(f"/cars/?q=(C.Make.{brand}._.(Or.Model.{model}._.Model."):
            return True
    return False


def saveBrandCounts():
    scraper = Car_Scrapper()
    scraper.goToCars()
    scraper.filterBrandModel()
    s = scraper.filter_page_soup

    # Create Brand listing counts df
    brand_tags = s.find_all(get_brands_tags)
    counts  = [int(count.nextSibling.nextSibling.string.strip("()")) for count in brand_tags]
    brand_names = [tag.string for tag in brand_tags]

    brand_df = pd.DataFrame({"brand":brand_names,"listing_count":counts })
    #brand_df = brand_df.loc[brand_df.listing_count > 1000,]
    brand_df = brand_df.sort_values("listing_count",axis=0, ascending=False).reset_index(drop=True)
    brand_df.to_csv("brand_listing_count.csv", index=False)

    return brand_df


# Create Model listing counts for CURRENT BRAND
#####  Replicate this steps for each model over there by first going to filter page for each brand #######
def saveModelCountsForBrand(brand, model):
    scraper = Car_Scrapper(brand=brand, model=model)
    scraper.goToCars()
    scraper.filterBrandModel()
    s = scraper.filter_page_soup

    model_tags = s.find_all(get_model_tags)
    counts  = [int(count.nextSibling.nextSibling.string.strip("()")) for count in model_tags]
    model_names = [tag.string for tag in model_tags]

    model_df = pd.DataFrame({"brand":[scraper.brand]*len(model_names),"model":model_names,"listing_count":counts })
    model_df = model_df.sort_values("listing_count",axis=0, ascending=False).reset_index(drop=True)
    model_df.to_csv(f"{brand}_model_counts.csv" , index=False)

    return model_df


