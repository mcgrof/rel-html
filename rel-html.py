#!/usr/bin/env python

# Provided an index URL and a few project hints page this
# will spit out a shiny HTML 5 W3C compliant releases page.

# Copyright (C) 2012 Luis R. Rodriguez <mcgrof@do-not-panic.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from HTMLParser import HTMLParser
import urllib
import ConfigParser
import re, sys

def rel_html_license():
	return "AGPL"

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

		self.config = ConfigParser.SafeConfigParser()
		self.config.read('rel-html.cfg')

		self.rel_html_proj = self.config.get("project", "rel_html_proj")
		stable_vers = self.config.get("project", "rel_html_stable_vers").split()

		self.rel_html_release_urls = []

		urls = self.config.get("project", "rel_html_url_releases").split()

		for url in urls:
			self.rel_html_release_urls.append(url.strip())

		self.rel_html_rels = []

		ver_testing = self.config.get("project", "rel_html_testing_ver")
		rel_name_testing = self.rel_html_proj + '-' + ver_testing
		tar_testing = rel_name_testing + ".tar.bz2"
		s_tarball_testing = rel_name_testing + ".tar.sign"
		tmp_changelog_testing = 'ChangeLog-' + ver_testing
		tmp_changelog_signed_testing = 'ChangeLog-' + ver_testing + ".sign"

		rel_testing = dict(version=self.config.get("project", "rel_html_testing_ver"),
				   rel=rel_name_testing,
				   url='',
				   maintained = True,
				   tarball = tar_testing,
				   tarball_exists = False,
				   signed_tarball = s_tarball_testing,
				   signed_tarball_exists = False,
				   changelog = tmp_changelog_testing,
				   changelog_url = '',
				   changelog_exists = False,
				   changelog_required = False,
				   signed_changelog = tmp_changelog_signed_testing,
				   signed_changelog_exists = False,
				   verified = False)

		self.rel_html_rels.append(rel_testing)

		for ver in stable_vers:
			maint = True
			if "EOL" in ver:
				maint = False
			ver = ver.strip(":EOL")
			rel_name = self.rel_html_proj + '-' + ver
			tar = rel_name + ".tar.bz2"
			s_tarball = rel_name + ".tar.sign"
			tmp_changelog = 'ChangeLog-' + ver
			tmp_changelog_signed = 'ChangeLog-' + ver + ".sign"

			# A release is only verified if the file exist,
			# its signed, has a respective ChangeLog and
			# the ChangeLog is signed
			rel = dict(version=ver,
				   rel=rel_name,
				   url='',
				   maintained = maint,
				   tarball = tar,
				   tarball_exists = False,
				   signed_tarball = s_tarball,
				   signed_tarball_exists = False,
				   changelog = tmp_changelog,
				   changelog_url = '',
				   changelog_exists = False,
				   changelog_required = True,
				   signed_changelog = tmp_changelog_signed,
				   signed_changelog_exists = False,
				   verified = False)
			self.rel_html_rels.append(rel)

		self.rel_license = self.config.get("project", "rel_license")
		self.html_title = self.config.get("html", "title")

		self.html_nav_dict = ({ self.config.get("html", "nav_01_url"),
				        self.config.get("html", "nav_01_txt") },
				      { self.config.get("html", "nav_02_url"),
				        self.config.get("html", "nav_02_txt") },
				      { self.config.get("html", "nav_03_url"),
				        self.config.get("html", "nav_03_txt") })

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
		if tag != 'a': pass
		for name, value in attributes:
			if name != 'href': pass
			for r in self.rel_html_rels:
				if r.get('version') in value:
					if r.get('tarball') in value:
						r['tarball_exists'] = True
						r['url'] = value
					elif r.get('signed_tarball') in value:
						r['signed_tarball_exists'] = True
					elif (r.get('changelog') == value):
						r['changelog_url'] = value
						r['changelog_exists'] = True
					elif (r.get('signed_changelog') == value):
						r['signed_changelog_exists'] = True

	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		pass

	def releases_verified(self):
		"Verify releases"

		all_verified = True

		for r in self.rel_html_rels:
			if (not r['tarball_exists']):
				all_verified = False
				sys.stdout.write('%s\n' % r['version'])
				break
			if (not r['signed_tarball_exists']):
				all_verified = False
				break
			if (r['changelog_required']):
				if (not (r['changelog_exists'])):
					all_verified = False
					break
				if (not (r['signed_changelog_exists'])):
					all_verified = False
					break
			r['verified'] = True

		return all_verified


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
	def __init__(self, parser):
		HTMLParser.__init__(self)
		self.parser = parser
		self.skip_endtag = False
		self.latest_stable = {}
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

		count = 0
		for r in self.parser.rel_html_rels:
			count+=1
			if (not r.get('verified')):
				continue

			if (count == 2):
				latest_stable = r

			sys.stdout.write('\t\t\t\t<tr>')
			sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (r.get('url'), r.get('rel')))
			sys.stdout.write('\t\t\t\t<td><a href="%s">signed</a></td>\n' % (r.get('signed_tarball')))
			if (r.get('maintained')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="FF0000">EOL</font></td>\n')
			if (r.get('changelog_required')):
				sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (r['changelog'], "ChangeLog"))
			else:
				sys.stdout.write('\t\t\t\t<td></td>\n')
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

def main():

	parser = index_parser()

	html = ""

	for url in parser.rel_html_release_urls:
		f = urllib.urlopen(url)
		html = html + f.read()

	parser.parse(html)
	
	if (not parser.releases_verified()):
		sys.stdout.write("Releases not verified\n")
		sys.exit(1)

	gen = rel_html_gen(parser)
	f = open('html/template.html', 'r')
	html = f.read()

	gen.parse(html)

if __name__ == "__main__":
        main()
