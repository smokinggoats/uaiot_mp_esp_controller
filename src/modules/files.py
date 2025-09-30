import os
import json


def dir_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) != 0
    except OSError:
        return False


def file_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False


def create_json(file_path: str, data: dict, flag: str = "w"):
    *path_list, _ = file_path.split("/")
    recurssive_mkdir(path_list)
    with open(file_path, flag) as file:
        file.write(json.dumps(data))
    return data


def get_json_file(file_path: str) -> dict:
    with open(file_path) as file:
        return json.load(file)


def open_or_create_json(file_path: str, data: dict) -> bool:
    if file_exists(file_path):
        with open(file_path) as file:
            return json.load(file)
    else:
        return create_json(file_path, data)


def write_json(file_path: str, data: dict) -> bool:
    try:
        with open(file_path, mode="w") as f:
            f.write(json.dumps(data))
        return True
    except Exception as e:
        print(e)
        return False


def mkdir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass
    return True


def rmdir(path):
    try:
        os.rmdir(path)
    except OSError:
        pass
    return True


def recurssive_mkdir(path_list: list[str] | None = None):
    last_path, *sub_path = path_list
    mkdir(last_path)
    if len(sub_path) > 0:
        sub_path[0] = f"{last_path}/{sub_path[0]}"
        return recurssive_mkdir(sub_path)
    return True


def recurssive_deldir(path_list: list[str] | None = None):
    last_path, *sub_path = path_list
    if len(sub_path) > 0:
        sub_path[0] = f"{last_path}/{sub_path[0]}"
        recurssive_deldir(sub_path)
    return rmdir(last_path)
