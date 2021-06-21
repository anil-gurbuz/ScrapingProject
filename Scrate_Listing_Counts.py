from Car_Scraper import *

brand_listing_count = pd.read_csv("brand_listing_count.csv")[lambda x: x["listing_count"]>1000] # No different then applying adidtional filter step

final_df = pd.DataFrame(columns=["brand","model","listing_count"])
for (brand,model) in zip(brand_listing_count.brand,brand_listing_count.first_model):
    BRAND = brand
    MODEL = model
    scraper = Car_Scrapper(brand=BRAND, model=MODEL)
    scraper.goToCars()
    scraper.filterBrandModel()
    s = scraper.filter_page_soup


    def get_model_tags(tag):
        brand = BRAND  # Must be modified based on brand model
        model = MODEL
        if tag.name == "a" and tag.has_attr("href"):
            if tag["href"].startswith(f"/cars/?q=(C.Make.{brand}._.(Or.Model.{model}._.Model."):
                return True
        return False

    model_tags = s.find_all(get_model_tags)
    counts = [int(count.nextSibling.nextSibling.string.strip("()")) for count in model_tags]
    model_names = [tag.string for tag in model_tags]

    model_df = pd.DataFrame(
        {"brand": [scraper.brand] * len(model_names), "model": model_names, "listing_count": counts})
    model_df = model_df.sort_values("listing_count", axis=0, ascending=False).reset_index(drop=True)
    model_df.to_csv(f"{brand}_model_counts.csv", index=False)
    final_df = final_df.append(model_df)

final_df.to_csv("model_counts.csv", index=False)

