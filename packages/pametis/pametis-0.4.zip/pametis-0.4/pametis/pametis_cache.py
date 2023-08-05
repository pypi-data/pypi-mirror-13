#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pametis_cache - cache implementation for the pametis package
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
# stdlib imports
#
from re import compile, match

#
# The PametisCache Class
#
# This class is for an abstract db, to bind it with a specific db it has to be subclassed and have the following
# class variables defined:
#   module       - The name of the db module (e.g., 'sqlite3', 'psycopg2', etc.)
#   stub         - The anchor string used by the db module (e.g., '?', '%s', etc.)
#   args, kwargs - arguments to the connect method
#
# Further below are two factories that implement the above - sqlite and postgres.
# The cache is implemented as a db table per domain, with one row per url. 
#

class PametisCacheError( Exception ): pass
class BadDomain( PametisCacheError ): pass
class CantRemove( PametisCacheError ): pass

_DOMAIN = compile( '^[a-zA-Z0-9\\-\\.]+$' )

# Cache driver base class
class Pametis_cache:
    def __init__( self, domain, new_version = True ):
        pass
    def __del__( self ):
        pass
    def is_current( self, url ):
        pass
    def is_completed( self ):
        pass
    def cache( self, url ):
        pass
    def finish( self ):
        pass
    def cached( self ):
        pass
    def remove( self ):
        pass
    def reset( self ):
        pass

#
# An SQL implementation of the PametisCache
#
# Expects class or instance variables that will provide customization data:
#   stub - '?' / '%s' / etc., the DB-API arguments placehoder
#   args, kwargs - arguments for DB-API connect
#   module - 'sqlite3' / 'psycopg2' / etc., the module that implements the DB-API
#
class Sql_cache( Pametis_cache ):

    #
    # Initialize the instance
    #
    # If new_version is True (default), the new instance starts a new cache version. Otherwise it continues
    # the previous version (e.g., in case you want to resume a previously disrupted iteration without
    # reiterating over those urls that were already processed).
    #
    def __init__( self, domain, new_version = True ):

        if not match( _DOMAIN, domain ):
            raise BadDomain
        self. domain = domain. lower(). replace( '.', '_D_' ). replace( '-', '_H_' )
        self. stub = { '': self. stub, 'domain': self. domain }

        # initialize db
        self. db = __import__( self. module ). connect( *self. args, **self. kwargs )
        c = self. db. cursor()
        c. execute( "CREATE TABLE IF NOT EXISTS versions (domain TEXT PRIMARY KEY, current INTEGER, completed INTEGER)" )
        self. db. commit()
        c. close()

        # get current cache version for the domain
        c = self. db. cursor()
        c. execute( "SELECT current, completed FROM versions WHERE domain=%()s" % self. stub, ( self. domain, ))
        res = c. fetchall()
        if len( res ):
            self. current, self. completed = res[ 0 ]

        # if no previous version, init the cache for the domain
        else:
            self. current, self. completed = 0, 1
            c. execute( "DROP TABLE IF EXISTS %(domain)s" % self. stub )
            c. execute( "CREATE TABLE %(domain)s (url TEXT PRIMARY KEY, version INTEGER)" % self. stub )
            c. execute( "INSERT INTO versions (domain, current, completed) VALUES (%()s, 0, 1 )" % self. stub, ( self. domain, ))
        self. db. commit()
        c. close()

        # handle new version initialization
        if new_version:
            self. current += 1
            self. completed = 0
            c = self. db. cursor()
            c. execute( "UPDATE versions SET current=%()s, completed=0 WHERE domain=%()s" % self. stub, ( self. current, self. domain ))
            self. db. commit()
            c. close()

    #
    # check if cached url's version is current
    #
    # Returns None if url is not cached, False if not current, True if current
    #
    def is_current( self, url ):
        c = self. db. cursor()
        c. execute( "SELECT version FROM %(domain)s WHERE url=%()s" % self. stub, ( url, ))
        res = c. fetchall()
        version = res[ 0 ][ 0 ] == self. current if len( res ) else None
        self. db. commit()
        c. close()
        return version

    #
    # Check if most recent iteration was completed
    #
    def is_completed( self ):
        c = self. db. cursor()
        c. execute( "SELECT completed FROM versions WHERE domain=%()s" % self. stub, ( self. domain, ))
        res = c. fetchone()[ 0 ]
        self. db. commit()
        c. close()
        return res

    #
    # cache a url
    #
    def cache( self, url ):
        c = self. db. cursor()
        c. execute( "UPDATE %(domain)s SET version=%()s WHERE url=%()s" % self. stub, ( self. current, url ))
        if not c. rowcount:
            c. execute( "INSERT INTO %(domain)s (url, version) VALUES (%()s, %()s)" % self. stub, (url, self. current ))
        self. db. commit()
        c. close()

    #
    # mark version as fully cached
    #
    def finish( self ):
        self. completed = 1
        c = self. db. cursor()
        c. execute( "UPDATE versions SET completed=1 WHERE domain=%()s" % self. stub, ( self. domain, ))
        self. db. commit()
        c. close()

    #
    # iterate over cached entries
    #
    def cached( self ):
        c = self. db. cursor()
        c. execute( "SELECT url FROM %(domain)s" % self. stub )
        self. db. commit()
        for row in c:
            yield row[ 0 ]
        c. close()

    #
    # iterate over urls no longer cached and remove them
    #
    def remove( self ):
        # can't do until the current version is fully cached
        if not self. completed:
            raise CantRemove
        c = self. db. cursor()
        while True:
            c. execute( "SELECT url FROM %(domain)s WHERE version<%()s LIMIT 1" % self. stub, ( self. current, ))
            res = c. fetchall()
            if len( res ):
                url = res[ 0 ][ 0 ]
                self. db. commit()
                c. close()
                yield url
                c = self. db. cursor()
                c. execute( "DELETE FROM %(domain)s WHERE url=%()s" %self. stub, ( url, ))
                self. db. commit()
            else:
                break
        self. db. commit()
        c. close()

    #
    # destructor
    #
    def __del__( self ):
        self. db. close()
    
    #
    # reset the cache of a domain (i.e., delete it!)
    #
    # this method is lazy, only drops the table, the table will be re-created
    # if the class will be initated for the domain.
    #
    def reset( self ):
        c = self. db. cursor()
        c. execute( "DROP TABLE IF EXISTS %(domain)s" % self. stub )
        c. execute( "DELETE FROM versions WHERE domain=%()s" % self. stub, ( self. domain, ))
        self. db. commit()
        c. close()

#
# Cache Factories
#
# Examples:
#   postgre_cache = postgres( 'postgres://postgres@localhost/mydb' )
#   sqlite_cache = sqlite( 'pametis_cache.db' )
#
# The parameters of the factories are any parameters accepted by the db module's
# connect method.
#

# cache factory for sqlite
def sqlite( *args, **kwargs ):
    class _Cache( Sql_cache, Pametis_cache ): pass
    _Cache. stub = '?'
    _Cache. args = args
    _Cache. kwargs = kwargs
    _Cache. module = 'sqlite3'
    return _Cache

# cache factory for postgres
def postgres( *args, **kwargs ):
    class _Cache( Sql_cache, Pametis_cache ): pass
    _Cache. stub = '%s'
    _Cache. args = args
    _Cache. kwargs = kwargs
    _Cache. module = 'psycopg2'
    return _Cache

#
# test the cache module and demostrate building various iterators with it
#
def cache_test():

    #
    # sample iterators
    #

    # iterate over all arguments
    def iter_all( *args ):
        cache = _cache( 'foo' )
        for url in args:
            yield url
            cache. cache( url )
        cache. finish()

    # iterate only over new arguments
    def iter_new( *args ):
        cache = _cache( 'foo' )
        for url in args:
            if cache. is_current( url ) is None:
                yield url
            cache. cache( url )
        cache. finish()

    # iterate over all arguments but abort unexpectadly
    def iter_all_partial( *args ):
        cache = _cache( 'foo' )
        for url in args:
            yield url
            cache. cache( url )

    # iterate only over new arguments but abort unexpectadly
    def iter_new_partial( *args ):
        cache = _cache( 'foo' )
        for url in args:
            if cache. is_current( url ) is None:
                yield url
            cache. cache( url )

    # resume aborted iteration over all arguments
    def iter_resume_all( *args ):
        cache = _cache( 'foo', new_version = False )
        if not cache. is_completed():
            for url in args:
                if not cache. is_current( url ):
                    yield url
                    cache. cache( url )
            cache. finish()

    # resume aborted iteration over new arguments
    def iter_resume_new( *args ):
        cache = _cache( 'foo', new_version = False )
        if not cache. is_completed():
            for url in args:
                if cache. is_current( url ) is None:
                    yield url
                cache. cache( url )
            cache. finish()

    # iterate and remove cached items which were absent from the latest version
    def iter_remove():
        cache = _cache( 'foo', new_version = False )
        for url in cache. remove():
            yield url
    
    # iterate over cached entries
    def iter_cached():
        cache = _cache( 'foo', new_version = False )
        for url in cache. cached():
            yield url

    #
    # The test
    #
    # printouts are not necessarily in the documented order
    #
    
    #_cache = postgres( 'postgres://postgres@localhost/test' )
    _cache = sqlite( 'test.db' )

    # start with a fresh cache
    _cache( 'foo' ). reset()

    # prints a b c
    for item in iter_all( 'a', 'b', 'c' ):
        print( item, end = ' ' )
    print()

    # prints a b c d
    for item in iter_all( 'a', 'b', 'c', 'd' ):
        print( item, end = ' ' )
    print()

    # prints e f
    for item in iter_new( 'a', 'b', 'c', 'd', 'e', 'f' ):
        print( item, end = ' ' )
    print()

    # prints g h
    for item in iter_new( 'a', 'e', 'g', 'h' ):
        print( item, end = ' ' )
    print()
    
    # prints a b c d e f g h
    for item in iter_cached():
        print( item, end = ' ' )
    print()

    # prints b c d f
    for item in iter_remove():
        print( item, end = ' ' )
    print()

    # prints b c d f
    for item in iter_new( 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h' ):
        print( item, end = ' ' )
    print()

    # prints a b c d
    for item in iter_all_partial( 'a', 'b', 'c', 'd' ):
        print( item, end = ' ' )
    print()

    # prints e f g h
    for item in iter_resume_all( 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h' ):
        print( item, end = ' ' )
    print()

    # prints <blank>
    for item in iter_all():
        print( item, end = ' ' )
    print()

    # prints a b c d e f g h
    for item in iter_remove():
        print( item, end = ' ' )
    print()

    # print a b
    for item in iter_new_partial( 'a', 'b' ):
        print( item, end = ' ' )
    print()

    # print c d
    for item in iter_new_partial( 'a', 'b', 'c', 'd' ):
        print( item, end = ' ' )
    print()

    # prints e f
    for item in iter_resume_new( 'a', 'b', 'c', 'd', 'e', 'f' ):
        print( item, end = ' ' )
    print()

    # prints <blank>
    for item in iter_remove():
        print( item, end = ' ' )
    print()

if '__main__' == __name__:
    cache_test()

