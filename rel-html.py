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
import urllib2
import ConfigParser
import re, sys
import os, getopt
from operator import itemgetter

debug = 0

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

def __compute_rel_weight(rel_specs):
	weight = 0
	extra = 0
	sublevel = 0
	relmod = 0
	relmod_type = 0

	if (debug):
		sys.stdout.write("VERSION       = %s\n" % rel_specs['VERSION'])
		sys.stdout.write("PATCHLEVEL    = %s\n" % rel_specs['PATCHLEVEL'])
		sys.stdout.write("SUBLEVEL      = %s\n" % rel_specs['SUBLEVEL'])
		sys.stdout.write("EXTRAVERSION  = %s\n" % rel_specs['EXTRAVERSION'])
		sys.stdout.write("RELMOD_UPDATE = %s\n" % rel_specs['RELMOD_UPDATE'])
		sys.stdout.write("RELMOD_TYPE   = %s\n" % rel_specs['RELMOD_TYPE'])

	if (rel_specs['EXTRAVERSION'] != ''):
		if ("."  in rel_specs['EXTRAVERSION'] or
		    "rc" in rel_specs['EXTRAVERSION']):
			rc = rel_specs['EXTRAVERSION'].lstrip("-rc")
			if (rc == ""):
				rc = 0
			else:
				rc = int(rc) - 20
			extra = int(rc)
		else:
			extra = int(rel_specs['EXTRAVERSION']) + 10

	if (rel_specs['SUBLEVEL'] != ''):
		sublevel = int(rel_specs['SUBLEVEL'].lstrip(".")) * 20
	else:
		sublevel = 5

	if (rel_specs['RELMOD_UPDATE'] != ''):
		mod = rel_specs['RELMOD_UPDATE']
		if (mod == ""):
			mod = 0
		else:
			mod = int(mod)
		relmod = int(mod)

	if (rel_specs['RELMOD_TYPE'] != ''):
		rtype = rel_specs['RELMOD_TYPE']
		if ("c" in rtype):
			relmod_type = relmod_type + 6
		if ("u" in rtype):
			relmod_type = relmod_type + 7
		if ("p" in rtype):
			relmod_type = relmod_type + 8
		if ("n" in rtype):
			relmod_type = relmod_type + 9
		if ("s" in rtype):
			relmod_type = relmod_type + 10

	weight = (int(rel_specs['VERSION'])    << 32) + \
		 (int(rel_specs['PATCHLEVEL']) << 16) + \
		 (sublevel   		       << 8 ) + \
		 (extra * 60) + (relmod * 2) + relmod_type

	return weight

def get_rel_spec(rel):
	if ("rc" in rel):
		m = re.match(r"v*(?P<VERSION>\d+)\.+" \
			      "(?P<PATCHLEVEL>\d+)[.]*" \
			      "(?P<SUBLEVEL>\d*)" \
			      "(?P<EXTRAVERSION>[-rc]+\w*)\-*" \
			      "(?P<RELMOD_UPDATE>\d*)[-]*" \
			      "(?P<RELMOD_TYPE>[usnpc]*)", \
			      rel)
	else:
		m = re.match(r"v*(?P<VERSION>\d+)\.+" \
			      "(?P<PATCHLEVEL>\d+)[.]*" \
			      "(?P<SUBLEVEL>\d*)[.]*" \
			      "(?P<EXTRAVERSION>\w*)\-*" \
			      "(?P<RELMOD_UPDATE>\d*)[-]*" \
			      "(?P<RELMOD_TYPE>[usnpc]*)", \
			      rel)
	if (not m):
		return m
	rel_specs = m.groupdict()
	return rel_specs

def compute_rel_weight(rel):
	rel_specs = get_rel_spec(rel)
	if (not rel_specs):
		return 0
	return __compute_rel_weight(rel_specs)

def __compute_rel_weight_next(rel_specs):
	weight = 0
	date = 0
	relmod_update = 0
	relmod_type = 0

	if (debug):
		sys.stdout.write("DATE_VERSION  = %s\n" % rel_specs['DATE_VERSION'])
		sys.stdout.write("RELMOD_UPDATE = %s\n" % rel_specs['RELMOD_UPDATE'])
		sys.stdout.write("RELMOD_TYPE   = %s\n" % rel_specs['RELMOD_TYPE'])

	if (rel_specs['DATE_VERSION'] != ''):
		date = rel_specs['DATE_VERSION'].lstrip("rc")
		date = int(date.translate(None, "-"))

	if (rel_specs['RELMOD_UPDATE'] != ''):
		mod = rel_specs['RELMOD_UPDATE']
		if (mod == ""):
			mod = 0
		else:
			mod = int(mod)
		relmod = int(mod)

	if (rel_specs['RELMOD_TYPE'] != ''):
		rtype = rel_specs['RELMOD_TYPE']
		if ("c" in rtype):
			relmod_type = relmod_type + 6
		if ("u" in rtype):
			relmod_type = relmod_type + 7
		if ("p" in rtype):
			relmod_type = relmod_type + 8
		if ("n" in rtype):
			relmod_type = relmod_type + 9
		if ("s" in rtype):
			relmod_type = relmod_type + 10

	weight = (999                << 32) + \
		 (int(date)          << 16) + \
		 (int(relmod_update) << 8 ) + \
		 (int(relmod_type))

	return weight

def compute_rel_weight_next(rel):
	if (len(rel) < 4):
		return 0
	if (rel[4] == "-"):
		m = re.match(r"v*(?P<DATE_VERSION>\w+-*\w*-*\w*)[-]*" \
			      "(?P<RELMOD_UPDATE>\d*)[-]*" \
			      "(?P<RELMOD_TYPE>[usnpc]*)", \
			      rel)
	else:
		m = re.match(r"v*(?P<DATE_VERSION>\w+)[-]*" \
			      "(?P<RELMOD_UPDATE>\d*)[-]*" \
			      "(?P<RELMOD_TYPE>[usnpc]*)", \
			      rel)
	if (not m):
		return 0

	rel_specs = m.groupdict()

	return __compute_rel_weight_next(rel_specs)

def sort_rels_weight(col):
	return sorted(col, key=lambda k: k['weight'], reverse=True)

class index_tarball_hunter(HTMLParser):
	"Goes through an index page with releases and adds tarball targets to the index parser"
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()
	def handle_decl(self, decl):
		pass
	def tarball_add_stable(self, t_new):
		s_new = t_new.get('specifics')
		for t_old in self.tarballs:
			s_old = t_old.get('specifics')
			idx = self.tarballs.index(t_old)

			if (s_old['VERSION'] != s_new['VERSION']):
				break

			if (s_old['PATCHLEVEL'] != s_new['PATCHLEVEL']):
				break

			if (s_old['EXTRAVERSION'] != '' and
			    s_new['EXTRAVERSION'] != ''):
				if (s_new['EXTRAVERSION'] > s_old['EXTRAVERSION']):
					self.tarballs.remove(t_old)
					self.tarballs.insert(idx, t_new)
					return
				if (s_new['EXTRAVERSION'] < s_old['EXTRAVERSION']):
					return
			if (s_old['RELMOD_UPDATE'] != '' and
			    s_new['RELMOD_UPDATE'] != ''):
				if (s_old['RELMOD_UPDATE'] == s_new['RELMOD_UPDATE']):
					if (s_new['RELMOD_TYPE'] == ''):
						self.tarballs.insert(idx-1, t_new)
						return
					self.tarballs.append(t_new)
					return
				if (s_new['RELMOD_UPDATE'] > s_old['RELMOD_UPDATE']):
					self.tarballs.remove(t_old)
					self.tarballs.insert(idx, t_new)
					return
				else:
					return
		self.tarballs.append(t_new)
	def tarball_add_next(self, t_new):
		index_parser = self.index_parser
		s_new = t_new.get('specifics')
		for t_old in self.tarballs:
			s_old = t_old.get('specifics')
			idx = self.tarballs.index(t_old)
			if (index_parser.next_rel_date in t_old.get('rel')):
				self.tarballs.insert(idx-1, t_new)
				return
		self.tarballs.append(t_new)
	def is_rel_eol(self, rel_specs):
		index_parser = self.index_parser
		for eol in index_parser.eol:
			m = re.match(r"v*(?P<VERSION>\d+)\.+" \
				      "(?P<PATCHLEVEL>\d+)[.]*" \
				      "(?P<SUBLEVEL>\w*)[.-]*" \
				      "(?P<EXTRAVERSION>\w*)", \
				      eol)
			if (not m):
				continue
			eol_specs = m.groupdict()
			if (eol_specs['VERSION'] == rel_specs['VERSION'] and
			    eol_specs['PATCHLEVEL'] == rel_specs['PATCHLEVEL']):
				return True
		return False
	def update_latest_tarball_stable(self, value):
		index_parser = self.index_parser
		if (self.release not in value):
			return
		if ('tar.sign' in value):
			return
		if (index_parser.release_extension not in value):
			return

		m = re.match(r'' + index_parser.rel_html_proj + '-+' \
			      "v*(?P<VERSION>\d+)\.+" \
			      "(?P<PATCHLEVEL>\d+)\.*" \
			      "(?P<SUBLEVEL>\w*)[.-]*" \
			      "(?P<EXTRAVERSION>\w*)[-]*" \
			      "(?P<RELMOD_UPDATE>\d*)[-]*" \
			      "(?P<RELMOD_TYPE>[usnpc]*)", \
			      value)
		if (not m):
			return

		rel_specifics = m.groupdict()

		supported = True
		if (self.is_rel_eol(rel_specifics)):
			supported = False

		p = re.compile(index_parser.release_extension + '$')
		rel_name = p.sub("", value)

		ver = rel_name.lstrip(index_parser.rel_html_proj + '-')

		p = re.compile('-[usnpc]$')
		changelog_ver = p.sub("", ver)
		tmp_changelog = 'ChangeLog-' + changelog_ver
		tmp_changelog_signed = tmp_changelog + ".sign"

		if (index_parser.ignore_changelogs):
			chanlog_req = False
		else:
			if ("rc" in ver):
				chanlog_req = False
			else:
				chanlog_req = True

		w = compute_rel_weight(ver)
		if (not w):
			return

		tar = dict(version = ver,
			   weight = w,
			   rel=rel_name,
			   specifics = rel_specifics,
			   base_url = self.base_url,
			   base_url_validated = False,
			   url = self.base_url + '/' + value,
			   maintained = supported,
			   longterm = False,
			   next_rel = False,
			   tarball = value,
			   tarball_exists = True,
			   ignore_signature = index_parser.ignore_signatures,
			   signed_tarball = rel_name + '.tar.sign',
			   signed_tarball_exists = False,
			   changelog = tmp_changelog,
			   changelog_url = self.base_url + '/' + tmp_changelog,
			   changelog_exists = False,
			   changelog_required = chanlog_req,
			   signed_changelog = tmp_changelog_signed,
			   signed_changelog_exists = False,
			   verified = False)

		self.tarball_add_stable(tar)
	def update_latest_tarball_next(self, value):
		index_parser = self.index_parser
		m = re.match(r'' + index_parser.rel_html_proj + '+' \
			      + '\-(?P<DATE_VERSION>' + index_parser.next_rel_date + '+)' \
			      + '\-*(?P<EXTRAVERSION>\d*)' \
			      + '\-*(?P<RELMOD>\w*)',
			      value)

		if (not m):
			return

		rel_specifics = m.groupdict()

		rel_name_next = index_parser.rel_html_proj + '-' + rel_specifics['DATE_VERSION']
		next_version = rel_specifics['DATE_VERSION']

		if (rel_specifics['EXTRAVERSION'] != ''):
			rel_name_next = rel_name_next + '-' + rel_specifics['EXTRAVERSION']
			next_version = next_version + '-' + rel_specifics['EXTRAVERSION']

		if (rel_specifics['RELMOD'] != ''):
			rel_name_next = rel_name_next + '-' + rel_specifics['RELMOD']
			next_version = next_version + '-' + rel_specifics['RELMOD']

		tar_next = rel_name_next + index_parser.release_extension
		s_tarball_next = rel_name_next + ".tar.sign"

		tmp_changelog = 'ChangeLog-' + next_version
		tmp_changelog_signed = 'ChangeLog-' + next_version + ".sign"

		w = compute_rel_weight_next(next_version)

		tar_next = dict(version=next_version,
				weight = w,
				rel = rel_name_next,
				url = '',
				specifics = rel_specifics,
				base_url = self.base_url,
				base_url_validated = False,
				maintained = True,
				longterm = False,
				next_rel = True,
				tarball = tar_next,
				tarball_exists = True,
				ignore_signature = index_parser.ignore_signatures,
				signed_tarball = s_tarball_next,
				signed_tarball_exists = False,
				changelog = tmp_changelog,
			        changelog_url = self.base_url + '/' + tmp_changelog,
				changelog_exists = False,
				changelog_required = False,
				signed_changelog = tmp_changelog_signed,
				signed_changelog_exists = False,
				verified = False)
		self.tarball_add_next(tar_next)

	def print_tarballs(self):
		for tar in self.tarballs:
			specifics = tar.get('specifics')
			sys.stdout.write("Tarball: %s<br>----extra: %s mod_update: %s mod_type: %s<br>" % \
					 (tar.get('url'),
					  specifics['EXTRAVERSION'],
					  specifics['RELMOD_UPDATE'],
					  specifics['RELMOD_TYPE']))
	def update_rel_candidates(self):
		index_parser = self.index_parser
		for tar in self.tarballs:
			index_parser.rel_html_rels.append(tar)
	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		index_parser = self.index_parser
		if tag != 'a': pass
		for name, value in attributes:
			if name != 'href': pass
			if (self.release not in value):
				pass

			if (index_parser.next_rel_date != '' and
			    index_parser.next_rel_date in value and
			    index_parser.release_extension in value):
				self.update_latest_tarball_next(value)
				pass

			self.update_latest_tarball_stable(value)
	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		pass
	def handle_comment(self, data):
		pass
	def __init__(self, index_parser, release, url):
		HTMLParser.__init__(self)
		self.index_parser = index_parser
		self.base_url = url.rstrip("/")
		self.release = release
		self.tarballs = []

class index_rel_inferrer(HTMLParser):
	"Goes through an index page with releases and update the inferred release"
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()
	def handle_decl(self, decl):
		pass
	def revise_inference(self, rel, value):
		index_parser = self.index_parser

		value = value.lstrip(index_parser.rel_html_proj + "-")

		p = re.compile(index_parser.release_extension + '$')
		value = p.sub("", value)

		base_specs = get_rel_spec(rel.get('base'))
		if (not base_specs):
			return

		inferred_specs = get_rel_spec(value)
		if (not inferred_specs):
			return

		if (inferred_specs['VERSION'] != base_specs['VERSION']):
			return
		if (inferred_specs['PATCHLEVEL'] != base_specs['PATCHLEVEL']):
			return
		if (base_specs['SUBLEVEL'] != ''):
			if (inferred_specs['SUBLEVEL'] != base_specs['SUBLEVEL']):
				return

		w = compute_rel_weight(value)
		if (not w):
			return

		inferred_rel = dict(base = rel,
				    url = self.base_url,
				    highest_release = value,
				    weight = w)

		# XXX: better way to do this?
		if (rel.get('highest_release') == ''):
			rel['url'] = self.base_url
			rel['highest_release'] = value
			rel['weight'] = w
		if (rel.get('weight') < inferred_rel.get('weight')):
			rel['url'] = self.base_url
			rel['highest_release'] = value
			rel['weight'] = w

	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		index_parser = self.index_parser
		if tag != 'a': return
		for name, value in attributes:
			if name != 'href': return
			if (index_parser.rel_html_proj not in value):
				return
			if (index_parser.release_extension not in value):
				return
			if (".sign" in value):
				return
			for rel in index_parser.inferred_releases:
				if (rel.get('base') not in value):
					continue
				self.revise_inference(rel, value)
	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		pass
	def handle_comment(self, data):
		pass
	def __init__(self, index_parser, url):
		HTMLParser.__init__(self)
		self.index_parser = index_parser
		self.base_url = url

class stable_url_parser(HTMLParser):
	"Goes through an index page and returns a URL for a release"
	def parse(self, html):
		"Parse the given string 's'."
		self.feed(html)
		self.close()
	def update_url(self, rel_target, rel_target_string, r, r_string):

		rel_string = r_string.lstrip("/v")
		rel_string = rel_string.rstrip("/")
		w = compute_rel_weight(rel_string)

		rel = dict(release_base = rel_target_string,
			   release = rel_string,
			   weight = w,
			   version = r['VERSION'],
			   patchlevel = r['PATCHLEVEL'],
			   extraversion = r['EXTRAVERSION'],
			   sublevel = r['SUBLEVEL'],
			   relmod = r['RELMOD_UPDATE'],
			   rel_url = self.base_url.rstrip("/") + '/' + r_string.rstrip("/"))

		if (len(self.stable_urls) == 0):
			self.stable_urls.append(rel)
			return

		for r_tmp in self.stable_urls:
			if (r_tmp.get('release_base') != rel_target_string):
				continue
			if (r_tmp.get('release') == r_string):
				return
			if (r_tmp.get('weight') < w):
				self.stable_urls.remove(r_tmp)
				self.stable_urls.append(rel)
				return

		self.stable_urls.append(rel)

	def update_stable_urls(self, rel, value):
		rel_target = get_rel_spec(rel)
		if (not rel_target):
			return

		r = get_rel_spec(value)
		if (not r):
			return

		if (rel_target['VERSION'] == ''):
			return
		if (rel_target['VERSION'] != r['VERSION']):
			return

		if (rel_target['PATCHLEVEL'] == ''):
			return
		if (rel_target['PATCHLEVEL'] != r['PATCHLEVEL']):
			return

		self.update_url(rel_target, rel, r, value)

	def handle_decl(self, decl):
		pass
	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		if tag != 'a': pass
		for name, value in attributes:
			if name != 'href': pass
			for rel in self.index_parser.supported:
				if (rel in value):
					self.update_stable_urls(rel, value)
	def handle_endtag(self, tag):
		pass
	def handle_data(self, data):
		pass
	def handle_comment(self, data):
		pass
	def __init__(self, index_parser, url):
		HTMLParser.__init__(self)
		self.index_parser = index_parser
		self.base_url = url
		self.stable_urls = []


class index_parser(HTMLParser):
	"HTML index parser for software releases class."
	def parse(self, html, url):
		"Parse the given string 's'."
		self.feed(html)
		self.close()

	def __init__(self, config_file):

		HTMLParser.__init__(self)

		self.config = ConfigParser.SafeConfigParser()
		self.config.read(config_file)

		self.rel_html_proj = self.config.get("project", "rel_html_proj")

		self.inferred_releases = []

		if (self.config.has_option("project", "supported")):
			self.supported = self.config.get("project", "supported").split()
			for rel in self.supported:
				inferred_rel = dict(base = rel,
						    url = '',
						    highest_release = '',
						    weight = 0)
				self.inferred_releases.append(inferred_rel)
		else:
			self.supported = list()
		if (self.config.has_option("project", "eol")):
			self.eol = self.config.get("project", "eol").split()
			for rel in self.eol:
				inferred_rel = dict(base = rel, url = '',
						    highest_release = '',
						    weight = 0)
				self.inferred_releases.append(inferred_rel)
		else:
			self.eol = list()

		self.stable_urls = []
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

		self.rels = []
		self.signed = False
		self.changelog = ''
		self.signed_changelog = False

	def get_stable_ext_urls(self, url):
		url_parser = stable_url_parser(self, url)
		try:
			rel = urllib2.urlopen(url)
			html = rel.read()
			url_parser.parse(html)
			self.stable_urls = url_parser.stable_urls
		except urllib2.HTTPError, error:
			return
	def search_stable_tarballs(self, ver, url):
		try:
			tarball_hunter = index_tarball_hunter(self, ver, url)

			f = urllib2.urlopen(url)
			html = f.read()
			tarball_hunter.parse(html)
			tarball_hunter.update_rel_candidates()
		except urllib2.HTTPError, error:
			return
		except urllib2.URLError, e:
			return
	def evaluate_stable_ext_urls(self):
		for r in self.stable_urls:
			self.search_stable_tarballs(r.get('release'), r.get('rel_url'))

	def update_inferred_releases(self, url):
		try:
			rel_inferrer = index_rel_inferrer(self, url)
			f = urllib2.urlopen(url)
			html = f.read()
			rel_inferrer.parse(html)
		except urllib2.HTTPError, error:
			return
		except urllib2.URLError, e:
			return
	def evaluate_inferred_releases(self):
		for r in self.inferred_releases:
			if (r.get('url') == ''):
				continue
			self.search_stable_tarballs(r.get('highest_release'), r.get('url'))
	def __get_next_rel_page(self, url):
		r = urllib2.urlopen(url)
		html = r.read()
		num_parser = largest_num_href_parser()
		return num_parser.parse(html)
	def get_next_url(self, url):
		self.next_rel_month = self.__get_next_rel_page(url)
		self.next_rel_day   = self.__get_next_rel_page(url + self.next_rel_month)
		self.next_rel_url   = url + self.next_rel_month + '/' + self.next_rel_day
		# XXX: automatically look for the largest year
		self.next_rel_date  = '2013' + '-' + self.next_rel_month + '-' + self.next_rel_day
	def evaluate_next_url(self):
		try:
			tarball_hunter = index_tarball_hunter(self,
							      self.next_rel_date,
							      self.next_rel_url)

			f = urllib2.urlopen(self.next_rel_url)
			html = f.read()
			tarball_hunter.parse(html)
			tarball_hunter.update_rel_candidates()
		except urllib2.HTTPError, error:
			return

	def scrape_for_releases(self):
		for url in self.rel_html_release_urls:
			if url.endswith('stable/'):
				self.get_stable_ext_urls(url)
				self.evaluate_stable_ext_urls()
			elif url.endswith('2013/'):
				self.get_next_url(url)
				self.evaluate_next_url()
			else:
				self.update_inferred_releases(url)
		self.evaluate_inferred_releases()
	def review_base_url(self, ver, url):
		try:
			f_rel = urllib2.urlopen(url)
			html = f_rel.read()
			self.parse(html, url)
		except urllib2.HTTPError, error:
			return

	def validate_releases(self):
		for r in self.rel_html_rels:
			if (r.get('base_url_reviewed')):
				continue
			if (r.get('base_url') == ''):
				continue
			self.review_base_url(self, r.get('base_url'))
		self.rel_html_rels = sort_rels_weight(self.rel_html_rels)

	def handle_starttag(self, tag, attributes):
		"Process a tags and its 'attributes'."
		if tag != 'a': pass
		for name, value in attributes:
			if name != 'href': pass
			for r in self.rel_html_rels:
				# sys.stdout.write('%s<br>\n' % value)
				if r.get('version') not in value:
					continue
				if r.get('signed_tarball') in value:
					r['signed_tarball_exists'] = True
				elif r.get('tarball') in value:
					if "longerm" in value:
						r['longterm'] = True
				elif (r.get('changelog') == value):
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
			else:
				if (r['changelog_exists'] and
				    (not (r['signed_changelog_exists']))):
					sys.stdout.write("Although a ChangeLog is not "
							 "required for this release (%s), one does "
							 "but it is not digitally signed. The "
							 "file %s does not exist<br>" %
							(r['version'], r['signed_changelog']))
					all_verified = False
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
				sys.stdout.write('\t\t\t\t<td><a href="%s">signed</a></td>\n' % \
						 (r.get('base_url') + '/' + r.get('signed_tarball')))
			else:
				sys.stdout.write('\t\t\t\t<td></td>\n')
			if (r.get('maintained') == True):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="FF0000">EOL</font></td>\n')
			if (not r.get('longterm')):
				sys.stdout.write('\t\t\t\t<td></td>\n')
			else:
				sys.stdout.write('\t\t\t\t<td><font color="00FF00">Longterm</font></td>\n')

			if (r.get('changelog_required')):
				sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % \
						 (r.get('changelog_url'), "ChangeLog"))
			else:
				if (r.get('changelog_exists')):
					if (r['signed_changelog_exists']):
						sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % \
								 (r.get('changelog_url'), "ChangeLog"))
					else:
						sys.stdout.write('\t\t\t\t<td></td>\n')
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
				sys.stdout.write('\t\t\t\t<td><a href="%s">signed</a></td>\n' % \
						 (r.get('base_url') + r.get('signed_tarball')))
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
				sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % \
						 (r.get('changelog_url'), "ChangeLog"))
			else:
				if (r.get('changelog_exists')):
					if (r['signed_changelog_exists']):
						sys.stdout.write('\t\t\t\t<td><a href="%s">%s</a></td>\n' % \
								 (r.get('changelog_url'), "ChangeLog"))
					else:
						sys.stdout.write('\t\t\t\t<td></td>\n')
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

def try_rel_next(rel):
	sys.stdout.write("----------------------------------------\n")
	sys.stdout.write("Rel: %s\n" % rel)
	w = compute_rel_weight_next(rel)
	sys.stdout.write("Weight: %s\n" % w)

def try_rel(rel_dict):
	sys.stdout.write("----------------------------------------\n")
	sys.stdout.write("Rel: %s\n" % rel_dict.get('version'))
	rel_dict["weight"] = compute_rel_weight(rel_dict.get('version'))
	sys.stdout.write("Weight: %s\n" % rel_dict.get("weight"))

def print_rels_weight(rels):
	for r in rels:
		sys.stdout.write("Rel: %20s\t%20s\n" %
				 (r.get('version'), r.get('weight')))

def try_rels(rels):
	col = []
	rsorted = []
	max_weight = 0
	for rel in rels:
		rel_d = dict(version = rel, weight = 0)
		col.append(rel_d)

	for r in col:
		try_rel(r)

	col = sort_rels_weight(col)

	print_rels_weight(col)

def debug_rel_tests():
	try_rel_next("2013-01-10-2-u")
	try_rel_next("20130110-2-u")
	try_rel_next("2013-03-07-u")
	try_rel_next("2013-03-07")

	rels = ["2.6.32.3",
		"3.8",
		"2.6.32.1",
		"2.6.32.40",
		"2.6.32",
		"3.8.2",
		"3.5.1",
		"3.2.1",
		"3.7.1",
		"3.8.2-1-usnpc",
		"3.8-rc1",
		"3.8-rc1-1-usnpc",
		"3.8-rc2-2-usnpc",
		"3.8-rc2-2-c",
		"3.8-rc2-2-s",
		"3.8-rc2-2",
		"3.8-rc3-1-u"]

	try_rels(rels)

def main():

	if (debug):
		debug_rel_tests()
		sys.exit(1)

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

	# We go through two passes on the provided URLs:
	#
	# 1. Scraping for releases
	# 2. Validation
	#
	# The first pass is based on finding the
	# highest release extraversion tarball. We
	# require a second pass as validation entails
	# searching for a ChangeLog and signature file
	# for all known existing releases.

	parser.scrape_for_releases()
	parser.validate_releases()

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
