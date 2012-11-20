# rel-html

rel-html is designed to parse naked index html pages
with tarballs on a software project and automatically
produce a nice shiny HTML5 release page for you. It takes
as input a configuration file, rel-html.cfg, in which
you can specify attributes for the release.

# TODO

 * Figure out how to automatically determine releases
   from git.

	- If we have many stable releases how should
	  we annotate this via git ?

 * See if we can copy the EOL release into an eol/ directory
   and moving forward instead of parsing the tags use the
   directory name to automatically determine other release
   attributes.

