from lib import *

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

