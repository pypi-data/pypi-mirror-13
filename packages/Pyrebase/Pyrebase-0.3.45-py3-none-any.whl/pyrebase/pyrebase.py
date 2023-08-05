import requests
from requests.exceptions import HTTPError
from firebase_token_generator import create_token
from urllib.parse import urlencode, quote
import re
import json
import math
from random import uniform
import time
from collections import OrderedDict


class Firebase():
    """ Firebase Interface """
    def __init__(self, fire_base_url, fire_base_secret):
        if not fire_base_url.endswith('/'):
            url = ''.join([fire_base_url, '/'])
        else:
            url = fire_base_url
        # find db name between http:// and .firebaseio.com
        db_name = re.search('https://(.*).firebaseio.com', fire_base_url)
        if db_name:
            name = db_name.group(1)
        else:
            db_name = re.search('(.*).firebaseio.com', fire_base_url)
            name = db_name.group(1)
        # default to admin
        auth_payload = {"uid": "1"}
        options = {"admin": True}

        self.token = create_token(fire_base_secret, auth_payload, options)
        self.requests = requests.Session()
        self.fire_base_url = url
        self.fire_base_name = name
        self.secret = fire_base_secret
        self.path = ""
        self.buildQuery = {}
        self.last_push_time = 0
        self.last_rand_chars = []

    def auth_with_password(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        return request_object.json()

    def create_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def remove_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/remove?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def change_password(self, email, old_password, new_password):
        request_ref = 'https://auth.firebase.com/auth/firebase/update?' \
                      'firebase={0}&email={1}&oldPassword={2}&newPassword={3}'.\
            format(self.fire_base_name, email, old_password, new_password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def send_password_reset_email(self, email):
        request_ref = 'https://auth.firebase.com/auth/firebase/reset_password?firebase={0}&email={1}'.\
            format(self.fire_base_name, email)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def order_by_child(self, order):
        self.buildQuery["orderBy"] = order
        return self

    def start_at(self, start):
        self.buildQuery["startAt"] = start
        return self

    def end_at(self, end):
        self.buildQuery["endAt"] = end
        return self

    def equal_to(self, equal):
        self.buildQuery["equalTo"] = equal
        return self

    def limit_to_first(self, limit_first):
        self.buildQuery["limitToLast"] = limit_first
        return self

    def limit_to_last(self, limit_last):
        self.buildQuery["limitToLast"] = limit_last
        return self

    def shallow(self):
        self.buildQuery["shallow"] = True
        return self

    def child(self, *args):
        new_path = "/".join(args)
        if self.path:
            self.path += "/{}".format(new_path)
        else:
            if new_path.startswith("/"):
                new_path = new_path[1:]
            self.path = new_path
        return self

    def get(self, token=None):
        parameters = {}
        parameters['auth'] = check_token(token, self.token)
        for param in list(self.buildQuery):
            if type(self.buildQuery[param]) is str:
                parameters[param] = quote('"' + self.buildQuery[param] + '"')
            else:
                parameters[param] = self.buildQuery[param]
        request_ref = '{0}{1}.json?{2}'.format(self.fire_base_url, self.path, urlencode(parameters))
        # reset path and buildQuery for next query
        query_key = self.path.split("/")[-1]
        self.path = ""
        buildQuery = self.buildQuery
        self.buildQuery = {}
        # do request
        request_object = self.requests.get(request_ref)
        # return if error
        try:
            request_object.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e, request_object.text)

        request_dict = request_object.json()
        # if primitive or simple query return
        if not isinstance(request_dict, dict):
            return PyreResponse(request_dict, query_key)
        if not buildQuery:
            return PyreResponse(convert_to_pyre(request_dict.items()), query_key)
        # return keys if shallow is enabled
        if buildQuery.get("shallow"):
            return PyreResponse(request_dict.keys(), query_key)
        # otherwise sort
        sorted_response = None
        if buildQuery.get("orderBy"):
            if buildQuery["orderBy"] == "$key":
                sorted_response = sorted(request_dict.items(), key=lambda item: item[0])
            else:
                sorted_response = sorted(request_dict.items(), key=lambda item: item[1][buildQuery["orderBy"]])
        return PyreResponse(convert_to_pyre(sorted_response), query_key)

    def push(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.post(request_ref, data=json.dumps(data))
        return request_object.json()

    def set(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.put(request_ref, data=json.dumps(data))
        return request_object.json()

    def update(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.patch(request_ref, data=json.dumps(data))
        return request_object.json()

    def remove(self, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.delete(request_ref)
        return request_object.json()

    def generate_key(self):
        push_chars = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        now = int(time.time() * 1000)
        duplicate_time = now == self.last_push_time
        self.last_push_time = now
        time_stamp_chars = [0] * 8
        for i in reversed(range(0, 8)):
            time_stamp_chars[i] = push_chars[now % 64]
            now = math.floor(now / 64)
        new_id = "".join(time_stamp_chars)
        if not duplicate_time:
            for i in range(0, 12):
                self.last_rand_chars.append(math.floor(uniform(0, 1) * 64))
        else:
            for i in range(0, 11):
                if self.last_rand_chars[i] == 63:
                    self.last_rand_chars[i] = 0
                self.last_rand_chars[i] += 1
        for i in range(0, 12):
            new_id += push_chars[self.last_rand_chars[i]]
        return new_id

    def sort(self, origin, by_key):
        # unpack pyre objects
        pyres = origin.each()
        new_list = []
        for pyre in pyres:
            new_list.append(pyre.item)
        # sort
        data = sorted(dict(new_list).items(), key=lambda item: item[1][by_key])
        return PyreResponse(convert_to_pyre(data), origin.key())


def convert_to_pyre(items):
    pyre_list = []
    for item in items:
        pyre_list.append(Pyre(item))
    return pyre_list


class PyreResponse:
    def __init__(self, pyres, query_key):
        self.pyres = pyres
        self.query_key = query_key

    def val(self):
        if isinstance(self.pyres, list):
            pyre_list = []
            for pyre in self.pyres:
                pyre_list.append((pyre.key(), pyre.val()))
            return OrderedDict(pyre_list)
        else:
            return self.pyres

    def key(self):
        return self.query_key

    def each(self):
        if isinstance(self.pyres, list):
            return self.pyres


class Pyre:
    def __init__(self, item):
        self.item = item

    def val(self):
        return self.item[1]

    def key(self):
        return self.item[0]


def check_token(user_token, admin_token):
    if user_token:
        return user_token
    else:
        return admin_token
