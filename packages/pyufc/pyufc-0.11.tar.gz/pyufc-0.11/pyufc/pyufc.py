#!/usr/bin/python
"""
PyUFC - A Python wrapper for API access to the UFC fighter roster
Inspired by https://github.com/valish/ufc-api
"""

import inspect

from bs4 import BeautifulSoup
import requests

__author__ = "Eric Hamiter <ehamiter@gmail.com>"
__version__ = "1.0"


class PyUFCError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Fighter(object):
    def __init__(self):
        self.base_url = "http://www.ufc.com/fighter/"
        self.parsed_html = None
        self.name = None
        self.nickname = None
        self.hometown = None
        self.location = None
        self.age = None
        self.reach = None
        self.leg_reach = None
        self.record = None
        self.college = None
        self.degree = None
        self.summary = None
        self.biography = None
        self.twitter_url = None
        self.website_url = None
        self.youtube_url = None
        self.strikes_attempted = None
        self.strikes_successful = None
        self.takedowns_attempted = None
        self.takedowns_successful = None

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    @staticmethod
    def check_response(response):
        if response.status_code == 200:
            return response
        else:
            raise PyUFCError("Error: {}".format(response.reason))

    def get_fighter(self, fighter):
        """Takes a fighter's first and last name as a string and tries to find their profile on UFC's site.

        :param: fighter
        :type: string
        :returns: instance

        >>> f = Fighter()
        >>> f.get_fighter("randy couture")
        >>> f.name
        u'Randy Couture'
        >>> f.nickname
        u'The Natural'
        """

        fighter = str(fighter).lower().replace(" ", "-")
        url = "{}{}".format(self.base_url, fighter)
        r = requests.get(url)
        self.check_response(r)
        self.parsed_html = BeautifulSoup(r.text, "html.parser")
        self._get_attributes()

    def serialize(self):
        attributes = inspect.getmembers(self, lambda x: not (inspect.isroutine(x)))
        excluded = ("base_url", "parsed_html")
        return dict([a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__') or a[0] in excluded)])

    def _get_attributes(self):
        self.name = self._parse_html("div", "fighter-details", "h1")
        self.nickname = self._parse_html("td", "fighter-nickname")
        self.hometown = self._parse_html("td", "fighter-from")
        self.location = self._parse_html("td", "fighter-lives-in")
        self.age = self._parse_html("td", "fighter-age")
        self.biography = self._parse_html("div", "biography")
        self.reach = self._parse_html("td", "fighter-reach")
        self.leg_reach = self._parse_html("td", "fighter-leg-reach")
        self.record = self._parse_html("td", "fighter-skill-record")
        self.college = self._parse_html("td", "fighter-college")
        self.degree = self._parse_html("td", "fighter-degree")
        self.summary = self._parse_html("td", "fighter-skill-summary")
        self.twitter_url = self._parse_html("li", "fighter-twitter-link", None, True)
        self.website_url = self._parse_html("li", "fighter-website-link", None, True)
        self.youtube_url = self._parse_html("li", "fighter-youtube-link", None, True)
        self.strikes_attempted, self.strikes_successful = self._parse_graphs(0)
        self.takedowns_attempted, self.takedowns_successful = self._parse_graphs(1)
        self._get_height()
        self._get_weight()

    def _parse_html(self, element, element_id, parent=None, link=False):
        parsed = self.parsed_html.find(element, {"id": element_id}) or ""
        if parsed and parent:
            parsed = getattr(parsed, parent)
        if parsed and link:
            parsed = parsed.find("a").get("href")
        if parsed and hasattr(parsed, "text"):
            parsed = parsed.text.replace("\n", "").replace("\t", "")
        return parsed

    def _parse_graphs(self, index):
        attempted = None
        successful = None
        stats = self.parsed_html.findAll("div", {"class": "overall-stats"})[index]
        if stats:
            graph = stats.findAll("div", {"class": "graph"})[0]
            attempted = getattr(graph.find("div", {"class": "max-number"}), "text")
            successful = getattr(graph.find("div", {"id": "total-takedowns-number"}), "text")
        return attempted, successful

    def _get_height(self):
        height = self._parse_html("td", "fighter-height")
        self.height = height.split(" (")[0] if height else None
        self.height_cm = height.split("( ")[1].split(" cm )")[0] if height else None

    def _get_weight(self):
        weight = self._parse_html("td", "fighter-weight")
        self.weight = weight.split(" lb (")[0] if weight else None
        self.weight_kg = weight.split("( ")[1].split(" kg )")[0] if weight else None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
