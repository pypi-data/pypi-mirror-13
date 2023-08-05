Change History
**************

0.3.8 (2016-01-18)
==================

* fixed esgsearch and esgf_logon process.

0.3.7 (2016-01-05)
==================

* use pywps.process.WPSProcess instead of malleefowl.process.WPSProcess.
* cleaned up malleefowl.config.
* updated dockerfile and recipe.

0.3.6 (2015-07-30)
==================

* download: checks if url has "file" schema. Those files can be returned directly.

0.3.5 (2015-07-28)
==================

* added solr search workflow.
* fixed esgf logon: port = "7512"

0.3.4 (2015-07-23)
==================

* disabled "File_Thredds" search type ... using "File" search instead.

0.3.3 (2015-06-18)
==================

* using python myproxyclient.

0.3.2 (2015-06-17)
==================

* added download with openid.
* renamed myproxy_logon().
* updated tomcat/thredds recipe.

0.3.1 (2015-06-14)
==================

* added thredds workflow
* download with `wget -x` to create directories in cache. 
* fixed workflow process output parameter.

0.3.0 (2015-05-22)
==================

* cleaned up processes ... download, esgsearch ...
* refactored workflow with dispel4py ... improved logging.

0.2.1 (2015-05-18)
==================

* fixed adagucserver installation
* using buildout recipes: birdhousebuilder.recipe.adagucserver, birdhousebuilder.recipe.postgres
* swift cloud access processes added.
* log to stderr/supervisor.

0.2.0 (2015-03-24)
==================

* update sphinx docs.
* using birdhouse environment.
* fixed mako_cache path.

0.1.8 (2015-01-17)
==================

* adagucserver with postgres added.
* fixed buildout bootstrap.
* esgf search checks local replica
* esgf archive_path changed

0.1.7 (2014-12-19)
==================

* wget download with thredding.
* added log-level to settings.
* Disabled map processes.
* wget process using local file archive.
* esgsearch process added.
* Disabled restflow.
* Using dispel4py workflow engine.

0.1.6 (2014-11-28)
==================

* Added wpsfetch script to retrieve test data for unit tests.

0.1.5 (2014-11-26)
==================

* changed config for cache_path and cache_url.
* Cleaned up unit tests.
* download method added.

0.1.4 (2014-11-24)
==================

* Using buildout 2.x.

0.1.3 (2014-11-11)
==================

* Fixed LD_LIBRARY_PATH for myproxy-logon. Should not use openssl library from anaconda.
* Replaced install.sh by Makefile.
* Dockerfile added.

0.1.2 (2014-10-21)
==================

* Fixed pyOpenSSL dependency.
* Updated docs.
* Updated dependencies.
* Dockfile for automated builds added.

0.1.1 (2014-08-21)
==================

* Changed default cache path.

0.1.0 (2014-08-18)
==================

* Initial Release.
