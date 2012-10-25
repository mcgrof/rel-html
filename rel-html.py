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

def rel_html_license():
	return "ISC"

def rel_html_href():
	return '<a href="https://github.com/mcgrof/rel-html">rel-html</a>'

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
		self.rel_license = self.config.get("project", "rel_license")

		self.html_title = self.config.get("html", "title")

		self.html_nav_dict = ({ self.config.get("html", "nav_01_url"),
				        self.config.get("html", "nav_01_txt") },
				      { self.config.get("html", "nav_02_url"),
				        self.config.get("html", "nav_02_txt") },
				      { self.config.get("html", "nav_03_url"),
				        self.config.get("html", "nav_03_txt") })

		self.html_nav_01_url = self.config.get("html", "nav_01_url")
		self.html_nav_01_txt = self.config.get("html", "nav_01_txt")

		self.html_nav_02_url = self.config.get("html", "nav_02_url")
		self.html_nav_02_txt = self.config.get("html", "nav_02_txt")

		self.html_nav_03_url = self.config.get("html", "nav_02_url")
		self.html_nav_03_txt = self.config.get("html", "nav_03_txt")

		self.html_release_title = self.config.get("html", "release_title")
		self.html_about_title = self.config.get("html", "about_title")
		self.html_about = self.config.get("html", "about")

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
		pass
	def handle_data(self, data):
		pass

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


# Example full html output parser, this can be used to
# simply read and output a full HTML file, you can modify
# this class to help you modify the contents. We do that
# later.
class html_base(HTMLParser):
	"HTML 5 generator from parsed index parser content."
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()
	def handle_decl(self, decl):
		sys.stdout.write('<!%s>' % decl)
	def handle_starttag(self, tag, attributes):
		sys.stdout.write('<%s' % tag)
		for name, value in attributes:
			sys.stdout.write(' %s="%s"' % (name, value))
		sys.stdout.write('>')
	def handle_endtag(self, tag):
		sys.stdout.write('</%s>' % tag)
	def handle_data(self, data):
		sys.stdout.write('%s' % data)
	def handle_comment(self, data):
		sys.stdout.write('<!--%s-->' % data)
	def __init__(self):
		HTMLParser.__init__(self)

def license_url(license):
	if (license == 'GPLv2'):
		return "http://www.gnu.org/licenses/gpl-2.0.html"
	elif (license == 'ISC'):
		return "http://opensource.org/licenses/ISC"
	elif (license == 'AGPL'):
		return "http://www.gnu.org/licenses/agpl-3.0.html"
	else:
		return "http://opensource.org/licenses/alphabetical"

class rel_html_gen(HTMLParser):
	"HTML 5 generator from parsed index parser content."
	def handle_title(self, tag, attributes):
		sys.stdout.write('<%s>%s' % (tag, self.parser.html_title))
	def handle_def_start(self, tag, attributes):
		sys.stdout.write('<%s' % tag)
		for name, value in attributes:
			sys.stdout.write(' %s="%s"' % (name, value))
		sys.stdout.write('>')
	def handle_h1_top(self, tag, attributes):
		self.skip_endtag = True
		sys.stdout.write('%s</h1>\n' % (self.parser.html_title))
		sys.stdout.write('\t\t<nav>\n')
		sys.stdout.write('\t\t\t<ul>\n')
		for txt, url in self.parser.html_nav_dict:
			sys.stdout.write('\t\t\t\t<li><a href="%s">%s</a></li>\n' % (url, txt))
		sys.stdout.write('\t\t\t</ul>\n')
		sys.stdout.write('\t\t</nav>\n')
	def handle_h1_release(self, tag, attributes):
		self.skip_endtag = True
		sys.stdout.write('%s</h1>\n' % (self.parser.html_release_title))
		sys.stdout.write('\t\t\t<table border="1">\n')
		sys.stdout.write('\t\t\t<tr>\n')
		sys.stdout.write('\t\t\t<td>Release</td>\n')
		sys.stdout.write('\t\t\t<td>ChangeLog</td>\n')
		sys.stdout.write('\t\t\t</tr>\n')

		for rel in self.parser.rels:

			url_rel = self.parser.rel_html_url_stable + '/' + rel
			url_changelog = self.parser.rel_html_url_stable + '/' + self.parser.changelog

			sys.stdout.write('\t\t\t\t<tr>')
			sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (url_rel, rel))
			sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (url_changelog, self.parser.changelog))
			sys.stdout.write('\t\t\t\t</tr>')

		sys.stdout.write('\t\t\t</table>\n')
	def handle_h1_about(self, tag, attributes):
		self.skip_endtag = True
		sys.stdout.write('%s</h1>\n' % (self.parser.html_about_title))
		sys.stdout.write('<p>%s</p>\n' % (self.parser.html_about))
	def handle_h_license(self, tag, attributes):
		self.skip_endtag = True
		sys.stdout.write('License</h1>\n')
		sys.stdout.write('\t\t<p>%s is licensed under the <a href="%s">%s</a>. \n' %
				 (self.parser.rel_html_proj,
				  license_url(self.parser.rel_license),
				  self.parser.rel_license))
		sys.stdout.write('This page was generated by %s licensed under the <a href="%s">%s</a></p>\n' %
				 (rel_html_href(),
				 license_url(rel_html_license()),
				 rel_html_license()))
	def handle_h1_pass(self, tag, attributes):
		pass
	def handle_h(self, tag, attributes):
		def_run = self.handle_h1_pass

		for name, value in attributes:
			if (name == 'id'):
				if (value == 'top_content'):
					def_run = self.handle_h1_top
				elif (value == 'release_title'):
					def_run = self.handle_h1_release
				elif (value == 'about'):
					def_run = self.handle_h1_about
				elif (value == 'license'):
					def_run = self.handle_h_license

		sys.stdout.write('<%s' % tag)
		for name, value in attributes:
			sys.stdout.write(' %s="%s"' % (name, value))
		sys.stdout.write('>')

		def_run(tag, attributes)

	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()

	def handle_decl(self, decl):
		sys.stdout.write('<!%s>' % decl)
	def handle_starttag(self, tag, attributes):
		self.skip_endtag = False
		if (tag == 'title'):
			self.handle_title(tag, attributes)
		elif (tag in {'h1', 'h2', 'h3'}):
			self.handle_h(tag, attributes)
		else:
			self.handle_def_start(tag, attributes)
	def handle_endtag(self, tag):
		if (self.skip_endtag):
			pass
		sys.stdout.write('</%s>' % tag)
	def handle_data(self, data):
		sys.stdout.write('%s' % data)
	def handle_comment(self, data):
		sys.stdout.write('<!--%s-->' % data)
	def __init__(self, parser):
		HTMLParser.__init__(self)
		self.parser = parser
		self.skip_endtag = False

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
	#for rel in parser.rels:
	#	print rel
	#print parser.changelog

	gen =  rel_html_gen(parser)
	f = open('html/template.html', 'r')
	html = f.read()

	gen.parse(html)

if __name__ == "__main__":
        main()
