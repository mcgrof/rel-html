#!/usr/bin/env python

# Provided an index URL and a few project hints page this
# will spit out a shiny HTML 5 W3C compliant releases page.

# Copyright (C) 2012-2013 Luis R. Rodriguez <mcgrof@do-not-panic.com>
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
import os, getopt
from operator import itemgetter

def rel_html_license_verbose():
	print '-----------------------------------------------------------------------'
	print 'Copyright (C) 2012-2013 Luis R. Rodriguez <mcgrof@do-not-panic.com>'
	print ''
	print 'This program is free software: you can redistribute it and/or modify'
	print 'it under the terms of the GNU Affero General Public License as'
	print 'published by the Free Software Foundation, either version 3 of the'
	print 'License, or (at your option) any later version.'
	print ''
	print 'This program is distributed in the hope that it will be useful,'
	print 'but WITHOUT ANY WARRANTY; without even the implied warranty of'
	print 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the'
	print 'GNU Affero General Public License for more details.'
	print ''
	print 'You should have received a copy of the GNU Affero General Public License'
	print 'along with this program.  If not, see <http://www.gnu.org/licenses/>.'
	print '-----------------------------------------------------------------------'

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

	def __init__(self, config_file):

		HTMLParser.__init__(self)

		self.config = ConfigParser.SafeConfigParser()
		self.config.read(config_file)

		self.rel_html_proj = self.config.get("project", "rel_html_proj")
		stable_vers = self.config.get("project", "rel_html_stable_vers").split()

		self.rel_html_release_urls = []

		urls = self.config.get("project", "rel_html_url_releases").split()

		for url in urls:
			self.rel_html_release_urls.append(url.strip())

		self.rel_html_rels = []

		if (self.config.has_option("project", "ignore_signatures")):
			self.ignore_signatures = self.config.get("project", "ignore_signatures")
		else:
			self.ignore_signatures = False
		if (self.config.has_option("project", "ignore_changelogs")):
			self.ignore_changelogs = self.config.get("project", "ignore_changelogs")
		else:
			self.ignore_changelogs = False
		if (self.config.has_option("project", "release_extension")):
			self.release_extension = "." + self.config.get("project", "release_extension")
		else:
			self.release_extension = ".tar.bz2"

		if (self.config.has_option("project", "rel_html_testing_ver")):
			ver_testing = self.config.get("project", "rel_html_testing_ver")
		else:
			ver_testing = ""
		rel_name_testing = self.rel_html_proj + '-' + ver_testing
		tar_testing = rel_name_testing + self.release_extension
		s_tarball_testing = rel_name_testing + ".tar.sign"
		tmp_changelog_testing = 'ChangeLog-' + ver_testing
		tmp_changelog_signed_testing = 'ChangeLog-' + ver_testing + ".sign"

		rel_testing = dict(version=ver_testing,
				   rel=rel_name_testing,
				   url='',
				   maintained = True,
				   longterm = False,
				   next_rel = False,
				   tarball = tar_testing,
				   tarball_exists = False,
				   ignore_signature = self.ignore_signatures,
				   signed_tarball = s_tarball_testing,
				   signed_tarball_exists = False,
				   changelog = tmp_changelog_testing,
				   changelog_url = '',
				   changelog_exists = False,
				   changelog_required = False,
				   signed_changelog = tmp_changelog_signed_testing,
				   signed_changelog_exists = False,
				   verified = False)

		if (ver_testing != ""):
			self.rel_html_rels.append(rel_testing)

		for ver in stable_vers:
			maint = True
			if "EOL" in ver:
				maint = False

			ver = ver.strip(":EOL")
			rel_name = self.rel_html_proj + '-' + ver
			tar = rel_name + self.release_extension
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
				   longterm = False,
				   next_rel = False,
				   tarball = tar,
				   tarball_exists = False,
				   ignore_signature = self.ignore_signatures,
				   signed_tarball = s_tarball,
				   signed_tarball_exists = False,
				   changelog = tmp_changelog,
				   changelog_url = '',
				   changelog_exists = False,
				   changelog_required = not self.ignore_changelogs,
				   signed_changelog = tmp_changelog_signed,
				   signed_changelog_exists = False,
				   verified = False)
			self.rel_html_rels.append(rel)

		self.next_rel_day = 0
		self.next_rel_month = 0
		self.next_rel_url = ''
		self.next_rel_date = ''

		self.rel_license = self.config.get("project", "rel_license")
		self.html_title = self.config.get("html", "title")

		self.html_nav_dict = ({ 'url': self.config.get("html", "nav_01_url"),
					'txt': self.config.get("html", "nav_01_txt") },
				      { 'url': self.config.get("html", "nav_02_url"),
				        'txt': self.config.get("html", "nav_02_txt") },
				      { 'url': self.config.get("html", "nav_03_url"),
				        'txt': self.config.get("html", "nav_03_txt") })

		self.html_release_title = self.config.get("html", "release_title")
		if (self.config.has_option("html", "release_title_next")):
			self.html_release_title_next = self.config.get("html", "release_title_next")
		else:
			self.html_release_title_next = ''
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
			if (self.next_rel_date != '' and
			    self.next_rel_date in value and
			    self.release_extension in value):
				m = re.match(r'' + self.rel_html_proj + '+' \
					      + '\-(?P<DATE_VERSION>' + self.next_rel_date + '+)' \
					      + '\-*(?P<EXTRAVERSION>\d*)' \
					      + '\-*(?P<RELMOD>\w*)',
					      value)

				rel_specifics = m.groupdict()

				rel_name_next = self.rel_html_proj + '-' + rel_specifics['DATE_VERSION']
				next_version = rel_specifics['DATE_VERSION']

				if (rel_specifics['EXTRAVERSION'] != ''):
					rel_name_next = rel_name_next + '-' + rel_specifics['EXTRAVERSION']
					next_version = next_version + '-' + rel_specifics['EXTRAVERSION']

				if (rel_specifics['RELMOD'] != ''):
					rel_name_next = rel_name_next + '-' + rel_specifics['RELMOD']
					next_version = next_version + '-' + rel_specifics['RELMOD']

				tar_next = rel_name_next + self.release_extension
				s_tarball_next = rel_name_next + ".tar.sign"

				rel_next = dict(version=next_version,
						rel=rel_name_next,
						url='',
						maintained = True,
						longterm = False,
						next_rel = True,
						tarball = tar_next,
						tarball_exists = True,
				   		ignore_signature = self.ignore_signatures,
						signed_tarball = s_tarball_next,
						signed_tarball_exists = False,
						changelog = '',
						changelog_url = '',
						changelog_exists = False,
						changelog_required = False,
						signed_changelog = '',
						signed_changelog_exists = False,
						verified = False)
				self.rel_html_rels.append(rel_next)

			# Stable release mods
			for r in self.rel_html_rels:
				if (self.next_rel_date != '' and
				    self.next_rel_date not in value and
				    'tar.sign' not in value and
				    self.release_extension in value and
				    r.get('version') in value):
					m = re.match(r'' + self.rel_html_proj + '-+' \
						      "v*(?P<VERSION>\w+.)" \
						      "(?P<PATCHLEVEL>\w+.*)" \
						      "(?P<SUBLEVEL>\w*)" \
						      "(?P<EXTRAVERSION>[.-]\w*)" \
						      "(?P<RELMOD>[-][usnpc]+)", \
						      value)
					if not m:
						continue
					rel_specifics = m.groupdict()

					rel_mod = rel_specifics['RELMOD']
					if (rel_mod == ''):
						continue
					rel_name = r.get('rel') + rel_mod

					rel_s = dict(version=r.get('version') + rel_mod,
						     rel=rel_name,
						     url='',
						     maintained = True,
						     longterm = False,
						     next_rel = False,
						     tarball = rel_name + self.release_extension,
						     tarball_exists = True,
				   		     ignore_signature = self.ignore_signatures,
						     signed_tarball = rel_name + '.tar.sign',
						     signed_tarball_exists = False,
						     changelog = '',
						     changelog_url = '',
						     changelog_exists = False,
						     changelog_required = False,
						     signed_changelog = '',
						     signed_changelog_exists = False,
						     verified = False)
					idx = map(itemgetter('version'), self.rel_html_rels).index(r.get('version'))
					self.rel_html_rels.insert(idx+1, rel_s)
					break

			for r in self.rel_html_rels:
				# sys.stdout.write('%s<br>\n' % value)
				if r.get('version') in value:
					if r.get('tarball') in value:
						r['tarball_exists'] = True
						r['url'] = value
						if "longerm" in value:
							r['longterm'] = True
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
				sys.stdout.write('No tarball: %s<br>\n' % r['tarball'])
				break
			if (not r['ignore_signature']):
				if (not r['signed_tarball_exists']):
					all_verified = False
					sys.stdout.write('No signed tarball: %s<br>\n' % r['signed_tarball'])
					break
			if (r['changelog_required']):
				if (not (r['changelog_exists'])):
					all_verified = False
					sys.stdout.write('No changelog (%s): %s<br>\n' % (r['changelog'], r['version']))
					break
				if (not (r['signed_changelog_exists'])):
					sys.stdout.write('No signed changelog (%s): %s<br>\n' % (r['signed_changelog'], r['version']))
					all_verified = False
					break
			r['verified'] = True

		return all_verified

class largest_num_href_parser(HTMLParser):
	"Will take an index page and return the highest numbered link"
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()
		return self.number
	def handle_decl(self, decl):
		pass
	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		if tag != 'a': pass
		for name, value in attributes:
			if name != 'href': pass
			if (re.match(r'\d+', value)):
				number = re.sub(r'\D', "", value)
				if (number > self.number):
					self.number = number

	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		pass
	def handle_comment(self, data):
		pass
	def __init__(self):
		HTMLParser.__init__(self)
		self.number = 0

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
		self.next_rels = []
		self.next_rel_count = 0
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
		for nav in self.parser.html_nav_dict:
			sys.stdout.write('\t\t\t\t<li><a href="%s">%s</a></li>\n' % (nav['url'], nav['txt']))
		sys.stdout.write('\t\t\t</ul>\n')
		sys.stdout.write('\t\t</nav>\n')
	def handle_h1_release(self, tag, attributes):
		self.skip_endtag = True
		sys.stdout.write('%s</h1>\n' % (self.parser.html_release_title))
		sys.stdout.write('\t\t\t<table border="0">\n')

		count = 0

		for r in self.parser.rel_html_rels:
			count+=1
			if (not r.get('verified')):
				continue

			if (count == 2):
				latest_stable = r

			if (r.get('next_rel')):
				self.next_rels.append(r)
				self.next_rel_count = self.next_rel_count + 1
				continue

			sys.stdout.write('\t\t\t\t<tr>')
			sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (r.get('url'), r.get('rel')))
			if (not r.get('ignore_signature')):
				sys.stdout.write('\t\t\t\t<td><a href="%s">signed</a></td>\n' % (r.get('signed_tarball')))
			else:
				sys.stdout.write('\t\t\t\t<td></td>\n')
			if (r.get('maintained')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="FF0000">EOL</font></td>\n')

			if (not r.get('longterm')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="00FF00">Longterm</font></td>\n')

			if (r.get('changelog_required')):
				sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (r['changelog'], "ChangeLog"))
			else:
				sys.stdout.write('\t\t\t\t<td></td>\n')
			sys.stdout.write('\t\t\t\t</tr>')

		sys.stdout.write('\t\t\t</table>\n')

	def handle_h1_release_next(self, tag, attributes):
		if (self.next_rel_count <= 0):
			return
		if (not len(self.next_rels)):
			return
		sys.stdout.write('%s</h1>\n' % (self.parser.html_release_title_next))
		sys.stdout.write('\t\t\t<table border="0">\n')

		for r in self.next_rels:
			if (not r.get('verified')):
				continue

			sys.stdout.write('\t\t\t\t<tr>')
			sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % (r.get('url'), r.get('rel')))
			if (not r.get('ignore_signature')):
				sys.stdout.write('\t\t\t\t<td><a href="%s">signed</a></td>\n' % (r.get('signed_tarball')))
			else:
				sys.stdout.write('\t\t\t\t<td></td>\n')
			if (r.get('maintained')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="FF0000">EOL</font></td>\n')

			if (not r.get('longterm')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="00FF00">Longterm</font></td>\n')

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
				elif (value == 'release_title_next'):
					def_run = self.handle_h1_release_next
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

def check_file(file_input):
	if not os.path.isfile(file_input):
		print 'File not found: %(file)s' % { "file": file_input }
		usage()

def __get_next_rel_page(url):
	r = urllib.urlopen(url)
	html = r.read()
	num_parser = largest_num_href_parser()
	return num_parser.parse(html)

def get_next_rel_url(parser, url):
	parser.next_rel_month = __get_next_rel_page(url)
	parser.next_rel_day   = __get_next_rel_page(url + parser.next_rel_month)
	parser.next_rel_url   = url + parser.next_rel_month + '/' + parser.next_rel_day
	parser.next_rel_date  = '2013' + '-' + parser.next_rel_month + '-' + parser.next_rel_day
	return parser.next_rel_url

def get_next_rel_html(parser, url):
	url = get_next_rel_url(parser, url)
	r = urllib.urlopen(url)
	return r.read()

def read_rel_html(ver, url):
	m = re.match(r"v*(?P<VERSION>\w+.)" \
		      "(?P<PATCHLEVEL>\w+.*)" \
		      "(?P<SUBLEVEL>\w*)" \
		      "(?P<EXTRAVERSION>[.-]\w*)" \
		      "(?P<RELMOD>[-]\w*)", \
		      ver)
	rel_specifics = m.groupdict()
	version =	rel_specifics['VERSION'] + \
			rel_specifics['PATCHLEVEL'] + \
			rel_specifics['SUBLEVEL'] + \
			rel_specifics['EXTRAVERSION']

	url_rel = url + 'v' + version

	f_rel = urllib.urlopen(url_rel)
	return f_rel.read()

def main():
	config_file = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hf:")
	except getopt.GetoptError, err:
		print str(err)
		usage()

	for o, a in opts:
		if o in ("-f"):
			check_file(a)
			config_file = a
		elif o in ("-h", "--help"):
			usage()

	if len(config_file) == 0:
		config_file = 'rel-html.cfg'

	parser = index_parser(config_file)

	html = ""

	for url in parser.rel_html_release_urls:
		if url.endswith('stable/'):
			for r in parser.rel_html_rels:
				html = html + read_rel_html(r.get('version'), url)

		elif url.endswith('2013/'):
			html = html + get_next_rel_html(parser, url)
		else:
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

def usage():
	print ''
	print '%(cmd)s' % { "cmd": sys.argv[0] }
	print ''
	print 'Provided an index URL and a few project hints page this'
	print 'will spit out a shiny HTML 5 W3C compliant releases page.'
	print ''
	rel_html_license_verbose()
	print ''
	print 'This program can be run without arguments or with a project file passed'
	print 'as an argument. If no arguments are given it will assume you have the'
	print 'file rel-html.cfg present on your current directory.'
	print ''
	print 'Usage: %(cmd)s [ -f rel-html.cfg ]' % { "cmd": sys.argv[0] }
	sys.exit(2)

if __name__ == "__main__":
        main()
