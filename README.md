# rel-html

rel-html is designed to parse naked index html pages
with tarballs on a software project and automatically
produce a nice shiny HTML5 release page for you. It takes
as input a configuration file, rel-html.cfg, in which
you can specify attributes for the release. Exact stable
releases are inferred based on some hints, but we still
require at least the base releases that are supported to
be annoated.

# Example release page

  * http://drvbp1.linux-foundation.org/~mcgrof/rel-html/linux/
  * http://drvbp1.linux-foundation.org/~mcgrof/rel-html/compat-drivers/
  * http://drvbp1.linux-foundation.org/~mcgrof/rel-html/iw/
  * http://drvbp1.linux-foundation.org/~mcgrof/rel-html/crda/
  * http://drvbp1.linux-foundation.org/~mcgrof/rel-html/hostapd/

# TODO

 * Figure out how to automatically determine releases
   from git.

	- If we have many stable releases how should
	  we annotate this via git ?

   It seems that the way to go is to require a config file
   for the project with the oldest stable release supported
   and then annotate eols. We do this right now, so rel-html
   would just need to be modified to infer newer releases.

 * The Linux kernel now (as of 2013-03-10) has json file for
   releases:

	https://www.kernel.org/releases.json

  We need to do a few things then:

	- Get other projects to use json for releases
	- Add json intepreter support to rel-html

  If projects don't use json releases files as the Linux
  kernel does then the current usage of HTMLParser would
  allow us to parse / infer releases for us.

 * See if we can copy the EOL release into an eol/ directory
   and moving forward instead of parsing the tags use the
   directory name to automatically determine other release
   attributes. This is only relevant for the Linux kernel
   right now.

