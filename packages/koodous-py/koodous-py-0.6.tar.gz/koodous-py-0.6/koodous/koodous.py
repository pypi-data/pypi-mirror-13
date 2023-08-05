#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015. The Koodous Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
   
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import hashlib
import logging
import time
import urllib

import certifi
import requests

import utils

__author__ = "Antonio Sanchez <asanchez@koodous.com>"

BASE_URL = 'https://koodous.com/api/'

REQUESTS_CA_BUNDLE = certifi.where()

logger = logging.getLogger('koodous-api')


class Koodous(object):
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': 'Token %s' % token}

    def my_user(self):
        url = '%s/analysts/current' % BASE_URL
        response = requests.get(url=url, headers=self.headers,
                                verify=REQUESTS_CA_BUNDLE)
        if response.status_code == 200:
            return response.json()

        return None

    def upload(self, filepath):
        """
            Function to upload a file
        """

        sha256_file = utils.sha256(filepath)
        url = '%s/apks/%s/get_upload_url' % (BASE_URL, sha256_file)
        response = requests.get(url=url, headers=self.headers,
                                verify=REQUESTS_CA_BUNDLE)
        if response.status_code == 200:
            json_data = response.json()
            # print json_data.get('upload_url', None)
            files = {'file': open(filepath, 'rb')}

            response = requests.post(url=json_data.get("upload_url"),
                                     files=files,
                                     verify=REQUESTS_CA_BUNDLE)
            while response.status_code == 404:  # Workaround server problem sometimes
                time.sleep(1)
                response = requests.post(url=json_data.get("upload_url"),
                                         files=files,
                                         verify=REQUESTS_CA_BUNDLE)
            return sha256_file
        elif response.status_code == 409:
            raise Exception("APK already exists")
        else:
            raise Exception("Unknown error: %s" % response.text)

    def download_to_file(self, sha256, dst):
        """
            Function to download a file to a destination
            Params:
                - sha256 (str): sha256 hash required.
                - dst (str): Path where the sample will be saved.
            Return:
                - sha256 hash if all was done.
            Exception:
                - Exception() with text "Something was wrong during download"
        """
        down_url = self.get_download_url(sha256)
        if down_url:
            res = requests.get(url=down_url, verify=REQUESTS_CA_BUNDLE)
            sha256_downloaded = hashlib.sha256(res.content).hexdigest()

            if sha256 != sha256_downloaded:
                raise Exception("Something was wrong during download")

            with open(dst, "wb") as fd:
                fd.write(res.content)

        else:
            raise Exception("Something was wrong during download")
        return sha256

    def get_download_url(self, sha256):
        """
            Return download URL for hash "sha256"
            Params:
                - sha256 (str): sha256 hash required.
            Return:
                - str: Download URL (valid during 5 minutes).
        """
        url = '%s/apks/%s/download' % (BASE_URL, sha256)

        response = requests.get(url=url, headers=self.headers,
                                verify=REQUESTS_CA_BUNDLE)
        if response.status_code == 200 and response.json().get('download_url',
                                                               None):
            return response.json().get('download_url', None)
        else:
            return None

    def search(self, search_term, limit=None):
        """
            Return apks objects (in json) list according a search string
            Params:
                - search_term (str): Search string according Koodous documentation
                - limit (int): Number to return only the first "limit" apks
            Return:
                - list: apks information found by the search.
        """
        to_ret = list()

        if not limit:
            limit = float('Inf')

        next_page = '%s/apks?page_size=100&search=%s' % (BASE_URL,
                                                         urllib.quote(
                                                             search_term))

        while next_page and len(to_ret) < limit:
            response = requests.get(url=next_page,
                                    headers=self.headers,
                                    verify=REQUESTS_CA_BUNDLE)
            next_page = response.json().get('next', None)
            for sample in response.json().get('results', []):
                to_ret.append(sample)
                if len(to_ret) == limit:
                    break
        return to_ret

    def get_analysis(self, sha256):
        url = '%s/apks/%s/analysis' % (BASE_URL, sha256)

        response = requests.get(url=url, headers=self.headers,
                                verify=REQUESTS_CA_BUNDLE)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 405: #Analysis doesn't exist
            raise Exception(
                  "This sample has not analysis available, you can request it.")
        # Otherwise
        return None

    def get_public_ruleset(self, ruleset_id):
        """
        Retrieve a public ruleset by id.

        :param ruleset_id: identifier of the public ruleset.
        :return: `dict`
        """
        url = '{endpoint}/public_rulesets/{id}'.format(**dict(
            endpoint=BASE_URL,
            id=ruleset_id))
        response = requests.get(url=url, headers=self.headers,
                                verify=REQUESTS_CA_BUNDLE)
        if response.status_code == 200:
            return response.json()
        return None

    def iter_matches_public_ruleset(self, ruleset_id):
        """
        Generator over the the matches of a public ruleset by id.

        :param ruleset_id: identifier of the public ruleset.
        :return: generator
        """
        next_page = '{endpoint}/ruleset_matches/{id}/apks'.format(**dict(
            endpoint=BASE_URL,
            id=ruleset_id))

        while next_page:
            response = requests.get(url=next_page, headers=self.headers,
                                    verify=REQUESTS_CA_BUNDLE)
            if response.status_code != 200:
                break

            r = response.json().get("results", None)

            if r:
                yield r

            next_page = response.json().get('next', None)

    def get_matches_public_ruleset(self, ruleset_id):
        """
        Retrieve the matches of a public ruleset by id. Avoid using this
        method on rulesets with many matches. Use the iterator version
        instead.

        :param ruleset_id: identifier of the public ruleset.
        :return: `list`
        """
        results = []

        for r in self.iter_matches_public_ruleset(ruleset_id):
            results.extend(r)

        return results

    def analyze(self, sha256):
        url = '%s/apks/%s/analyze' % (BASE_URL, sha256)
        res = requests.get(url=url, headers=self.headers,
                           verify=REQUESTS_CA_BUNDLE)
        if res.status_code == 200:
            return True
        return False

    def post_comment(self, sha256, comment):
        url = '%s/apks/%s/comments' % (BASE_URL, sha256)
        payload = {'text': comment}

        response = requests.post(url=url, headers=self.headers,
                                 data=payload, verify=REQUESTS_CA_BUNDLE)

        if response.status_code == 201:
            return response.json().get('text', None)

        return None

    def get_comments(self, sha256):
        to_ret = list()
        next_page = '%s/apks/%s/comments' % (BASE_URL, sha256)

        while next_page:
            response = requests.get(url=next_page,
                                    headers=self.headers,
                                    verify=REQUESTS_CA_BUNDLE)
            next_page = response.json().get('next', None)
            for sample in response.json().get('results', []):
                to_ret.append(sample)

        return to_ret

    def delete_comment(self, comment_id):
        url = '%s/comments/%s' % (BASE_URL, comment_id)
        response = requests.delete(url=url, headers=self.headers,
                                   verify=REQUESTS_CA_BUNDLE)

        if response.status_code == 204:
            return True

        return False

    def vote_apk_positive(self, sha256, kind):
        """
            To send a positive vote to an APK (goodware)
        """
        url = '%s/apks/%s/votes' % (BASE_URL, sha256)
        return requests.post(url, data={'kind': 'positive'},
                             headers=self.headers, verify=REQUESTS_CA_BUNDLE)

    def vote_apk_negative(self, sha256, kind):
        """
            To send a negative vote to an APK (malware)
        """

        url = '%s/apks/%s/votes' % (BASE_URL, sha256)
        return requests.post(url, data={'kind': 'negative'},
                             headers=self.headers, verify=REQUESTS_CA_BUNDLE)

    def vote_apk(self, sha256, kind):
        """
            Function to send a positive or negative vote to an APK.
            Params:
                sha256 (str): sha256 of the file
                kind (str): 'positive' to send a positive vote or
                            'negative' to send a negative vote
            Return:
                TODO
        """
        kind = str(kind)
        if kind != 'positive' or kind != negative:
            raise Exception("Kind vote must be positive or negative")

        url = '%s/apks/%s/votes' % (BASE_URL, sha256)

        return requests.post(url, data={'kind': kind},
                             headers=self.headers, verify=REQUESTS_CA_BUNDLE)
