from lib import *

BUCKET_NAME = "anil.cars.bucket"


def downSizeImageWithCrop(image_obj, new_size=512):
    try:
        im = Image.open(io.BytesIO(image_obj))
    except TypeError:
        im = image_obj

    # size: (Width X Height)
    w = im.size[0]
    h = im.size[1]

    if w < new_size or h < new_size:
        logging.info(f"Original image size is smaller than {new_size}")

    cropped_images_list = []
    # Will move the box horizontally
    if w >= h:
        ratio = h / new_size
        im = im.resize((round(w / ratio), new_size))

        for i in range((im.size[0] // new_size) + 1):
            upper = 0
            lower = new_size
            left = i * new_size
            right = left + new_size

            cropped_images_list.append(im.crop((left, upper, right, lower)))

    else:
        ratio = w / new_size
        im = im.resize((new_size, round(h / ratio)))

        for i in range((im.size[1] // new_size) + 1):
            left = 0
            right = new_size
            upper = i * new_size
            lower = upper + new_size

            cropped_images_list.append(im.crop((left, upper, right, lower)))

    return cropped_images_list


def uploadFileToS3(file_obj, file_path, bucket_name=BUCKET_NAME):
    s3 = boto3.client("s3")
    try:
        s3.upload_fileobj(file_obj, bucket_name, file_path)

    except ClientError as e:
        logging.error(e)
        return False

    return True


def createFolderInS3(folder_path, bucket_name=BUCKET_NAME):
    s3 = boto3.client("s3")
    r = s3.put_object(Bucket=bucket_name, Key=folder_path)


def expand2square(pil_img, background_color=(0, 0, 0)):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


def downSizeImageWithPadding(image_obj, new_size=512):
    try:
        im = Image.open(io.BytesIO(image_obj))
    except TypeError:
        im = image_obj

    im.thumbnail((new_size, new_size))
    im = expand2square(im)
    return im
