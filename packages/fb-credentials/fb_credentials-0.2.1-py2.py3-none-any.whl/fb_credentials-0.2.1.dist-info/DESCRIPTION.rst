fb_credentials
==============

An extension to logging functionality for FogBugz module and for extensions
to it like fborm. 

Function fb_credentials.FogBugz is a layer on top of the constructor fogbugz.Fogbugz
 or similar constructors (for example fborm.FogBugzORM) that provides a convenient
 parsing of a .hgrc file (by default in the $HOME dir), or prompts the user for
 credentials.

Sample usage
============

import fb_credentials
fb = fb_credentials.FogBugz('https://YourRepository.com/')
fb.search(q='53410', cols='ixBug')

E-mail me
=========

portu.github@gmail.com


