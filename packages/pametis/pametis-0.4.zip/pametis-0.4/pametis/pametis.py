#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pametis version 0.4 - Sitemap Analyzer/Parser/Iterator
#    Copyright (c) 2015 Avner Herskovits
#
#    MIT License
#
#    Permission  is  hereby granted, free of charge, to any person  obtaining  a
#    copy of this  software and associated documentation files (the "Software"),
#    to deal in the Software  without  restriction, including without limitation
#    the rights to use, copy, modify, merge,  publish,  distribute,  sublicense,
#    and/or  sell  copies of  the  Software,  and to permit persons to whom  the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this  permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT  WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE  WARRANTIES  OF  MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR  ANY  CLAIM,  DAMAGES  OR  OTHER
#    LIABILITY, WHETHER IN AN  ACTION  OF  CONTRACT,  TORT OR OTHERWISE, ARISING
#    FROM,  OUT  OF  OR  IN  CONNECTION WITH THE SOFTWARE OR THE  USE  OR  OTHER
#    DEALINGS IN THE SOFTWARE.
#

#
# Imports - stdlib
#
from re import compile, sub, _pattern_type as pattern_type
from urllib.parse import urlparse

#
# Imports - private
#
from .pametis_cache import sqlite, Pametis_cache
from .pametis_spider import sitemap_spider, Pametis_spider

#
# Exception tree
#
class PametisException( Exception ): pass
class BadParam( PametisException ): pass
class AmbiguousOptions( PametisException ): pass

#
# Configuration options
#
class _OPT: pass
class OPT:
    class CACHED( _OPT ):   pass # Don't fetch the sitemap, just iterate over whatever is cached
    class REMOVE( _OPT ):   pass # Iterate over urls missing from the latest sitemap
    class RESUME( _OPT ):   pass # The current iteration resumes the previous one
    class PARTIAL( _OPT ):  pass # The curernt iteration doesn't cover the entire domain
    class NEWONLY( _OPT ):  pass # Iterate only over urls that are unknown in the cache
    class NOCACHE( _OPT ):  pass # Speedy, don't chache the sitemap
    class CACHEALL( _OPT ): pass # Chace all sitemap urls, ignoring the filter

class _Conf:
    db       = sqlite( 'pametis_cache.db' )
    spider   = sitemap_spider()
    filter   = None
    cached   = False
    remove   = False
    resume   = False
    partial  = False
    newonly  = False
    nocache  = False
    cacheall = False

#
# Helper for analyzing configuration options
#
def _configure( *args ):
    def is_ambiguous( opt0, opt1 ):
        for opt in opt1:
            if getattr( conf, opt0 ) and getattr( conf, opt ):
                raise AmbiguousOptions( 'Ambiguous options ' + opt0. upper() + ' and ' + opt. upper() )

    conf = _Conf()
    for arg in args:
        # is OPT
        try:
            if arg. __bases__[ 0 ] is _OPT:
                setattr( conf, arg. __name__. lower(), True )
                continue
        except Exception:
            pass
        # is regex or str
        if arg. __class__ is pattern_type:
            conf. filter = arg
            continue
        if type( arg ) is str:
            conf. filter = compile( arg )
            continue
        # is cache
        try:
            found = False
            for base in arg. __bases__:
                if base is Pametis_cache:
                    conf. db = arg
                    found = True
                    break
            if found:
                continue
        except Exception:
            pass
        # is spider
        try:
            found = False
            for base in arg. __class__. __bases__:
                if base is Pametis_spider:
                    conf. spider = arg
                    found = True
                    break
            if found:
                continue
        except Exception:
            pass
        # is no good
        raise BadParam( 'Unknown argument ' + repr( arg ))
    is_ambiguous( 'remove', ( 'resume', 'partial', 'newonly', 'nocache', 'cacheall' ))
    is_ambiguous( 'nocache', ( 'cached', 'partial', 'resume', 'newonly', 'cacheall' ))
    return conf

#
# Configure the package's defaults
#
def configure( *args ):
    new_conf = _configure( *args )
    for attr in dir( new_conf ):
        if not attr. startswith( '_' ):
            setattr( _Conf, attr, getattr( new_conf, attr ))

#
# Class to hold results
#
class _Res( str, object ): pass

#
# Main function, yields all sitemap leafs
#
def sitemap( url, *args ):

    # get the configuration
    url_parsed = urlparse( url )
    domain = url_parsed. hostname
    path = url_parsed. path
    conf = _configure( *args )

    # prepare in advace some common config conditions
    cache_all = conf. cacheall
    cache_any = not conf. nocache
    cache_flt = cache_any and not cache_all
    yield_all = not conf. resume and not conf. newonly

    # init cache
    new_version = False if conf. resume or conf. remove or conf. cached else True
    if cache_any:
        cache = conf. db( domain, new_version = new_version )

    # iterate over cached urls
    if conf. cached:
        for url in cache. cached():
            if not conf. filter or conf. filter. search( url ):
                res = _Res( url )
                res. lastmod, res. changefreq, res. priority = None, None, None
                yield res

    # iterate and remove non-current url
    elif conf. remove:
        for url in cache. remove():
            if not conf. filter or conf. filter. search( url ):
                res = _Res( url )
                res. lastmod, res. changefreq, res. priority = None, None, None
                yield res

    # iterate over urls obtained from the sitemap
    elif not conf. resume or not cache. is_completed():
        for link in conf. spider( url ):
            if not conf. filter or conf. filter. search( link ):
                is_current = cache. is_current( link ) if cache_any else None
                if yield_all or ( conf. newonly and is_current is None ) or ( conf. resume and not is_current ):
                    yield link
                    if cache_flt:
                        cache. cache( link )
                if cache_all:
                    cache. cache( link )
    
    if not conf. nocache and not conf. partial and not conf. remove and not conf. cached:
        cache. finish()
#
# CLI invocation
#
def main():
    from argparse import ArgumentParser
    parser = ArgumentParser( description = 'Sitemap spider' )
    parser. add_argument( '-a', '--cacheall', action='append_const', dest = 'options', const = OPT. CACHEALL, help = 'cache also urls the don\'t pass the filter' )
    parser. add_argument( '-c', '--cached',   action='append_const', dest = 'options', const = OPT. CACHED,   help = 'use cached urls' )
    parser. add_argument( '-n', '--nocach',   action='append_const', dest = 'options', const = OPT. NOCACHE,  help = 'don\'t use a cache' )
    parser. add_argument( '-N', '--newonly',  action='append_const', dest = 'options', const = OPT. NEWONLY,  help = 'show only new urls' )
    parser. add_argument( '-p', '--partial',  action='append_const', dest = 'options', const = OPT. PARTIAL,  help = 'this sitemap has only part of the domain\'s urls' )
    parser. add_argument( '-r', '--remove',   action='append_const', dest = 'options', const = OPT. REMOVE,   help = 'remove non-current urls' )
    parser. add_argument( '-R', '--resume',   action='append_const', dest = 'options', const = OPT. RESUME,   help = 'resume an incomplete iteration' )
    parser. add_argument( '--sqlite',         action='append',       dest = 'options', type = lambda x: sqlite( x ),      help = 'filename to hold sqlite cache' )
    parser. add_argument( '--postgres',       action='append',       dest = 'options', type = lambda x: postgres( x ),    help = 'url of postgres database to hold cache' )
    parser. add_argument( '--file',           action='append',       dest = 'options', type = lambda x: file_spider( x ), help = 'get urls from file rather than the web' )
    parser. add_argument( 'url', help='url of the sitemap XML or robots.txt' )
    parser. add_argument( 'filter', nargs = '?', action='append', type = lambda x: compile( x ), help='regular expression to filter urls' )
    cli = parser. parse_args()
    if cli. options:
        configure( *cli. options )
    if cli. filter != [ None ]:
        configure( filter )
    for url in sitemap( cli. url ):
        print( url )

if '__main__' == __name__:
    main()
