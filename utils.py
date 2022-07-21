import csv
import shutil
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import os
from PIL import Image

import requests
import glob

import setting

setting = setting.get_settings()


def get_line_notify_token(path) -> list:
    token_dict = []
    with open(path + '/sent_token_list.txt', encoding='utf-8') as f:
        for line in f:
            line = line.split(',')
            token_dict.append({
                "name": line[0].rstrip(),
                "token": line[1].rstrip()
            })
    return token_dict


def sent_to_line_notify(content: dict, token: dict):
    print("發送群組: {}".format(token.get("name")))
    headers = {"Authorization": "Bearer " + token.get("token")}
    content = deepcopy(content)
    if content.get("type") == "image":
        content["files"] = {
            "imageFile": open(content.get("files").get("imageFile"), "rb")
        }
    r = requests.post(setting.line_notify_api, headers=headers, data=content.get("data"), files=content.get("files"))
    if r.ok:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
        white_csv_log([dt2.strftime("%Y-%m-%d %H:%M:%S"), token.get("name"), content.get("filename")])


def get_all_file_path(path) -> list:
    return sorted(glob.glob(path + '/*', recursive=True))


def parser_file(files: list) -> list:
    sent_content_list = []
    for i in files:
        if "txt" in i:
            file_name, file = read_txt_content(i)
            sent_content_list.append({
                "type": "msg",
                "data": {
                    "message": file
                },
                "files": {},
                "filename": file_name
            })
        elif "jpg" in i or "jpeg" in i or "png" in i:
            resize_image(i)
            file_name, file = read_image_content(i)
            sent_content_list.append({
                "type": "image",
                "data": {
                    "message": " ",
                },
                "files": {
                    "imageFile": file
                },
                "filename": file_name
            })
    return sent_content_list


def read_txt_content(path: str):
    content = "\n"
    with open(path, encoding='utf-8') as f:
        for line in f:
            content += line
    move_file(path, path.replace("Sent", "History"))
    return path.split("/")[-1], content


def move_file(path, new_path):
    shutil.move(path, new_path)


def read_image_content(path: str):
    new_path = path.replace("Sent", "History")
    move_file(path, new_path)
    return path.split("/")[-1], new_path


def process_sent_notify(sent_content: dict, snet_target: list):
    for token in snet_target:
        sent_to_line_notify(sent_content, token)


def white_csv_log(log: list):
    path = "./log/發送紀錄.csv"
    with open(path, "a+") as f:
        csv_write = csv.writer(f)
        csv_write.writerow(log)


def resize_image(path):
    orig_size = get_size_format(os.path.getsize(path))
    if float(orig_size[0:-2]) > 3:
        compress_img(path, 3 / float(orig_size[0:-2]))


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def compress_img(image_name, new_size_ratio=0.9, quality=90, width=None, height=None, to_jpg=True):
    # load the image to memory
    img = Image.open(image_name)
    # print the original image shape
    print("[*] Image shape:", img.size)
    # get the original image size in bytes
    image_size = os.path.getsize(image_name)
    # print the size before compression/resizing
    print("[*] Size before compression:", get_size_format(image_size))
    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.ANTIALIAS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    # split the filename and extension
    filename, ext = os.path.splitext(image_name)
    # make new filename appending _compressed to the original file name
    if to_jpg:
        # change the extension to JPEG
        new_filename = f"{filename}{ext}"
    else:
        # retain the same extension of the original image
        new_filename = f"{filename}{ext}"
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    print("[+] New file saved:", new_filename)
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filename)
    # print the new size in a good format
    print("[+] Size after compression:", get_size_format(new_image_size))
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    # print the saving percentage
    print(f"[+] Image size change: {saving_diff / image_size * 100:.2f}% of the original image size.")


if __name__ == "__main__":
    # sent_to_line_notify({'message': '\ngo.jpeg'}, {}, "maApn9NeoJx0jjcChEqoMrgUyJsLhBIjhInBzpBq8XB")
    print(get_all_file_path('./Sent'))
