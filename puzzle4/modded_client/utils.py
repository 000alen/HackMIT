from typing import Any, Union, Dict
import jsonpickle
from requests.models import Response
import requests
import uuid

import constants as constants


def jsonpickle_decode(text):
    return jsonpickle.decode(text.replace("hackbase.client.", ""))


def post_route(route, data=None) -> Union[Dict[Any, Any], None]:
    endpoint = "%s/u/%s/tracker/%s" % (
        constants.NODE_SERVER,
        constants.USERNAME,
        route
    )

    try:
        data = data=jsonpickle.encode(data)
        # print(f"{data=}")
        r = requests.post(endpoint, data=data)
        print(r)
        return jsonpickle_decode(r.text)  # type: ignore
    except Exception as e:
        print(f"failed request: {route}, error: {e}")
        return None


def get_route(route, params=None) -> Union[Dict[Any, Any], None]:
    endpoint = "%s/u/%s/tracker/%s" % (
        constants.NODE_SERVER,
        constants.USERNAME,
        route
    )
    try:
        if params:
            endpoint += "?" + \
                "&".join([f"{key}={value}" for key, value in params.items()])
        r = requests.get(endpoint)
        # if not r.json()["success"]:
        #         print(f"failed request: {route}, msg: {r.json()['message']}")
        return jsonpickle_decode(r.text)  # type: ignore
    except Exception as e:
        print(f"failed request: {route}, error: {e}")
        return None


def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')


def trim_string(s, max_len=constants.PRINT_STR_LEN):
    if(len(s) <= max_len):
        return s
    return f"{s[:max_len]}..."
