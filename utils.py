import csv
import shutil
from copy import deepcopy
from datetime import datetime, timezone, timedelta

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
            file_name, file = read_image_content(i)
            sent_content_list.append({
                "type": "image",
                "data": {
                    "message": file_name
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


if __name__ == "__main__":
    # sent_to_line_notify({'message': '\ngo.jpeg'}, {}, "maApn9NeoJx0jjcChEqoMrgUyJsLhBIjhInBzpBq8XB")
    print(get_all_file_path('./Sent'))
