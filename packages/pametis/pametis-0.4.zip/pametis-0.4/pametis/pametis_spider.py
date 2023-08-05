#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pametis_spider - cache implementation for the pametis package
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

from gzip import decompress
from re import compile, sub, _pattern_type as pattern_type
from urllib.parse import urlparse
from urllib. request import urlopen
from xml. etree. ElementTree import fromstring

# Helper class to hold results
class _Res( str, object ): pass

#
# The spider base class
#
class Pametis_spider:
    def __call__( self, url ):
        pass

#
# Implementation of spider that reads urls from a file
#
# Every line is a url, lines beginning with a hash are treated as comments.
# An easy way to generate such a file is by using wget, see for example
# http://stackoverflow.com/questions/3948947
#
class file_spider( Pametis_spider ):
    def __init__( self, filename ):
        self. filename = filename
    def __call__( self, url ):
        with open( self. filename, 'r', encoding = 'utf-8' ) as f:
            for line in f:
                _line = _Res( line. strip() )
                _line. lastmod, _line. changefreq, _line. priority = None, None, None
                if '' != _line and not _line. startswith( '#' ):
                    yield _line

#
# Implementation of spider that reads urls from a sitemap.xml file or robots.txt
#
class sitemap_spider( Pametis_spider ):

    def __call__( self, url ):

        # helper sitemap reader
        def _reader( url ):
            with urlopen( url ) as map:
                xmlstr = map. read()
            if url. endswith( '.gz' ):
                xmlstr = decompress( xmlstr ). decode( 'utf-8' )
            else:
                xmlstr = xmlstr. decode( 'utf-8' )
            xmlstr = sub( '<(urlset|sitemapindex)[^>]*>', '<\\1>', xmlstr, count = 1 )  # Get rid of namespaces
            return fromstring( xmlstr )

        # helper function to hold results
        def _res( loc, url ):
            res = _Res( loc )
            res. lastmod, res. changefreq, res. priority = None, None, None
            for i in url:
                if i. tag in ( 'lastmod', 'changefreq', 'priority' ):
                    setattr( res, i. tag, i. text )
            return res

        # recurse over sitemap
        def _sitemap( url ):
            xml = _reader( url )
            for child in xml:
                if 'sitemap' == child. tag:
                    for loc in child. iter( 'loc' ):
                        yield from _sitemap( loc. text )
                elif 'url' == child. tag:
                    for url in child. iter( 'url' ):
                        loc = url. find( 'loc' ). text
                        yield _res( loc, url )

        # get sitemap from robots.txt and iterate
        def _robots( url ):
            with urlopen( url ) as robots:
                for line in robots:
                    _line = line. decode( 'utf-8' )
                    if _line. lower(). startswith( 'sitemap:' ):
                        yield from _sitemap( _line. split( ':', 1 )[ -1 ]. strip() )

        url_parsed = urlparse( url )
        path = url_parsed. path
        if path. endswith( 'robots.txt' ):
            yield from _robots( url )
        else:
            yield from _sitemap( url )


