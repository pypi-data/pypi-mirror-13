# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import defusedxml.lxml
import magic
import os
import requests
import unittest

from lxml.html import HTMLParser

from bakery_lint.base import BakeryTestCase as TestCase, TestCaseOperator


class TestDescriptionHtmlEnUs(TestCase):

    targets = ['description']
    tool = 'FontBakery'
    name = __name__

    def test_broken_links(self):
        """ Check if DESCRIPTION do not have broken links """
        try:
            contents = open(self.operator.path).read()
        except:
            self.fail('File {} does not exist'.format(self.operator.path))
        doc = defusedxml.lxml.fromstring(contents, parser=HTMLParser())
        for link in doc.xpath('//a/@href'):
            try:
                response = requests.head(link)
                self.assertEqual(response.status_code, requests.codes.ok,
                                 msg='%s is broken' % link)
            except requests.exceptions.RequestException as ex:
                self.fail('%s raises exception [%r]' % (link, ex))

    def test_description_is_valid_html(self):
        """ DESCRIPTION.en_us.html is not real html file """
        msg = 'DESCRIPTION.en_us.html is not real html file'
        if not os.path.exists(self.operator.path):
            self.fail('File {} does not exist'.format(self.operator.path))
        self.assertEqual(magic.from_file(self.operator.path, mime=True), 'text/html', msg)

    def test_description_is_more_than_500b(self):
        """ DESCRIPTION.en_us.html is more than 500 bytes """
        msg = 'DESCRIPTION.en_us.html is not real html file'
        try:
            statinfo = os.stat(self.operator.path)
        except:
            self.fail('File {} does not exist'.format(self.operator.path))
        msg = 'DESCRIPTION.en_us.html must have size larger than 500 bytes'
        self.assertGreater(statinfo.st_size, 500, msg)


def get_suite(path):
    suite = unittest.TestSuite()
    TestDescriptionHtmlEnUs.operator = TestCaseOperator(path)
    for test in unittest.defaultTestLoader.loadTestsFromTestCase(TestDescriptionHtmlEnUs):
        suite.addTest(test)
    return suite