# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from Car_Scraper import *




if __name__ == '__main__':
    models_df = pd.read_csv("model_counts.csv")[lambda x: x["listing_count"] > 30].sort_values(
        "listing_count").reset_index(drop=True)

    last_car_id = 31640
    page_to_start= 5
    cars_finished = 207

    skip_list = models_df.model.values[:cars_finished].tolist()

    for idx, row in models_df.iterrows():
        if row["model"] in skip_list:
            continue
        n_pages = row["listing_count"] // 12 + 1
        n_pages = n_pages if n_pages < 20 else 20

        scraper = Car_Scrapper(brand=row["brand"], model=row["model"], car_id_start=last_car_id + 1)
        scraper.scrapeNPages(n_pages, page_to_start)

        scraper.df.to_csv(f"{row['brand']}_{row['model']}_listings.csv", index=False)
        last_car_id = scraper.car_id
        cars_finished += 1
        page_to_start = 1
        logging.info(f"{row['brand']}_{row['model']} is done! {cars_finished} cars scraped")
