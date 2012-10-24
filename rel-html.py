#!/usr/bin/env python

# Provided an index URL and a few project hints page this
# will spit out a shiny HTML 5 W3C compliant releases page.

# Copyright (C) 2012 Luis R. Rodriguez <mcgrof@do-not-panic.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from HTMLParser import HTMLParser
import urllib
import ConfigParser
import re, sys

class index_parser(HTMLParser):
	"HTML index parser for software releases class."
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()

	def __init__(self):

		HTMLParser.__init__(self)

		self.config = ConfigParser.SafeConfigParser({'rel_html_proj': 'linux', 'rel_html_url_stable': 'kernel.org'})
		self.config.read('rel-html.cfg')

		self.rel_html_proj = self.config.get("project", "rel_html_proj")
		self.rel_html_stable = self.config.get("project", "rel_html_stable")
		self.rel_html_stable_short = self.rel_html_stable.replace('v', '')
		self.rel_html_next = self.config.get("project", "rel_html_next")
		self.rel_html_url_stable = self.config.get("project", "rel_html_url_stable") + '/' + self.rel_html_stable
		self.rel_html_url_next = self.config.get("project", "rel_html_url_next")

		self.hyperlinks = []
		self.rels = []
		self.signed = False
		self.changelog = ''
		self.signed_changelog = False

	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		if tag != 'a': return
		for name, value in attributes:
			if name != 'href': return
			if (not value.startswith(self.rel_html_proj) and
			    not value.startswith('ChangeLog')):
				continue
			if name == "href":
				self.hyperlinks.append(value)

	def handle_endtag(self, tag):
		return
	def handle_data(self, data):
		return

	def get_hyperlinks(self):
		"Return the list of hyperlinks."

		rel_target = self.rel_html_proj + '-' + self.rel_html_stable_short
		rel_changelog = 'ChangeLog-' + self.rel_html_stable

		latest_rel_num = 0
		rel_num = 0

		for url in self.hyperlinks:
			if (url.startswith(rel_target)):
				m = re.search('(?<=' + rel_target + '-)\d+', url)
				rel_num = m.group(0)
				if (int(rel_num) > latest_rel_num):
					latest_rel_num = int(rel_num)

		rel_target = rel_target + '-' + str(latest_rel_num)
		rel_changelog = rel_changelog + '-' + str(latest_rel_num)

		for url in self.hyperlinks:
			if (url.startswith(rel_target) and
			    url.endswith('tar.bz2')):
				self.rels.append(url)
				continue

			if (url.startswith(rel_target) and
			    url.endswith('tar.sign')):
				self.signed = True
				continue

			if (url.startswith(rel_changelog) and
			    url.endswith('.sign')):
				self.signed_changelog = True
				continue

			if (url.startswith(rel_changelog)):
				self.changelog = url


def main():

	parser = index_parser()

	f = urllib.urlopen(parser.rel_html_url_stable)
	html = f.read()

	parser.parse(html)
	parser.get_hyperlinks()

	if (not parser.signed):
		print "No signed release found!"
		sys.exit(1)

	if (not parser.signed_changelog):
		print "No signed release ChangeLog found!"
		sys.exit(1)

	if (not parser.changelog):
		print "No ChangeLog found!"
		sys.exit(1)

	# Write HTML5 base page
	for rel in parser.rels:
		print rel
	print parser.changelog

if __name__ == "__main__":
        main()
