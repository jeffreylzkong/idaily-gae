#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
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
import webapp2
import urllib2
import re
from bs4 import BeautifulSoup as bs
from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(60)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class NewsContentHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('url')
        text = self.request.get('text').strip()
        try:
            text = text.decode('utf-8')
        except:
            pass
        soup = bs(urllib2.urlopen(url).read())
        dom = soup.find(text=re.compile(text))
        if not dom:
            # search by less words
            text = ' '.join(text.split(' ')[:4])
            dom = soup.find(text=re.compile(text))
        if not dom:
            text = text.split(' ')[1]
            dom = soup.find(text=re.compile(text))
        if not dom:
            domWrapper = soup.body
        else:
            domWrapper = dom
            if dom.parent:
                domWrapper = dom.parent
            if domWrapper.parent:
                domWrapper = domWrapper.parent
        [s.extract() for s in domWrapper(['iframe', 'style', 'script'])]
        for a in domWrapper.findAll('a'):
            a['href'] = ''
        # Allow CORS
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write(str(domWrapper))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newsContent', NewsContentHandler)
], debug=True)
