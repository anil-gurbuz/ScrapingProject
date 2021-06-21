#from lib import *
from Car_Scraper import *

BUCKET_NAME = "anil.cars.bucket"

def downSizeImage(image_obj, new_size = 512):

    try:
        im = Image.open(io.BytesIO(image_obj))
    except TypeError:
        im = image_obj

    # size: (Width X Height)
    w = im.size[0]
    h = im.size[1]

    assert w >= new_size and h >= new_size, f"Original image is smaller than {new_size}"

    cropped_images_list = []
    # Will move the box horizontally
    if w>=h:
        ratio = h/new_size
        im = im.resize((round(w/ratio), new_size))


        for i in range((im.size[0]//new_size)+1):
            upper = 0
            lower = new_size
            left = i*new_size
            right = left + new_size

            cropped_images_list.append(im.crop((left,upper,right,lower)))

    else:
        ratio = w / new_size
        im = im.resize((new_size, round(h / ratio)))

        for i in range((im.size[1] // new_size) + 1):
            left = 0
            right = new_size
            upper = i* new_size
            lower = upper + new_size

            cropped_images_list.append(im.crop((left, upper, right, lower)))


    return cropped_images_list


def uploadFileToS3(file_obj, file_path,  bucket_name=BUCKET_NAME ):
    s3 = boto3.client("s3")
    try:
        s3.upload_fileobj(file_obj, bucket_name, file_path)

    except ClientError as e:
        logging.error(e)
        return False

    return True

def createFolderInS3(folder_path, bucket_name=BUCKET_NAME):
    s3 = boto3.client("s3")
    r = s3.put_object(Bucket=bucket_name, Key= folder_path)



def get_brands_tags(tag):
    if tag.name == "a" and tag.has_attr("href"):
        if tag["href"].startswith("/cars/?q=(Or.(C.Make.Audi._.Model.A1.)_.Make"):
            return True
    return False


def get_model_tags(tag):
    brand = BRAND # Must be modified based on brand model
    model = MODEL
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
def saveModelCountsForBrand(brand):
    scraper = Car_Scrapper(brand=brand)
    scraper.goToCars()
    scraper.filterBrandOnly()
    s = scraper.filter_page_soup

    model_tags = s.find_all(get_model_tags)
    counts  = [int(count.nextSibling.nextSibling.string.strip("()")) for count in model_tags]
    model_names = [tag.string for tag in model_tags]

    model_df = pd.DataFrame({"brand":[scraper.brand]*len(model_names),"model":model_names,"listing_count":counts })
    model_df = model_df.sort_values("listing_count",axis=0, ascending=False).reset_index(drop=True)
    model_df.to_csv(f"{brand}_model_counts.csv" , index=False)

    return model_df

