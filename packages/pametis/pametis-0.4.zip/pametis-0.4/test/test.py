#
# tests
#

#
# Imports from stdlib
#
from re import compile
from time import perf_counter as timer

#
# Private imports
#
from sys import path
from pametis import configure, sitemap, OPT, sqlite

#
# Test sitemaps
#
URL10 = 'https://raw.githubusercontent.com/avnr/pametis/master/test/sm10.xml'
URL20 = 'https://raw.githubusercontent.com/avnr/pametis/master/test/sm20.xml'
URL30 = 'https://raw.githubusercontent.com/avnr/pametis/master/test/sm30.xml'

GET_DUMMY = compile( '[1-3][1-9]' )

_sqlite = sqlite( 'test.db' )
_sqlite( 'raw.githubusercontent.com', False ). reset()
configure( _sqlite )

#
# Wrapper
#
def test( *args ):
    start = timer()
    result = [ url for url in sitemap( *args )]
    elapsed = timer() - start
    print( 'Result: ', end ='' )
    for r in result:
        print( GET_DUMMY. search( r ). group(), end= ' ' )
    print()
    print( 'Elapsed:', elapsed * 1000, 'miliseconds' )

#
# BEGIN TESTS
#

# Compare chached vs. non-cahched timing

# Cached
print()
print( 'Test: Iterate over one sitemap with cache' )
print( 'Expect: 11..19' )
test( URL10 )

# Non chached
print()
print( '---------------------------' )
print()
print( 'Test: Iterate over one sitemap without cache' )
print( 'Expect: 11..19' )
test( URL10, OPT. NOCACHE )

# Test versioning

# Add some urls
print()
print( '---------------------------' )
print()
print( 'Test: Iterate over one sitemap with cache, new set of urls' )
print( 'Expect: 21..29' )
test( URL20 )

# Remove non-current urls
print()
print( '---------------------------' )
print()
print( 'Test: Remove urls missing from latest sitemap' )
print( 'Expect: 11..19' )
test( URL30, OPT. REMOVE )

# Test partial-resume

# First batch - only partial, no resume
print()
print( '---------------------------' )
print()
print( 'Test: Iterate over partial sitemap' )
print( 'Expect: 11..19' )
test( URL10, OPT. PARTIAL )

# Middle batch - partial and resume
print()
print( '---------------------------' )
print()
print( 'Test: Continue with next sitemap, still partial' )
print( 'Expect: 21..29' )
test( URL20, OPT. PARTIAL, OPT. RESUME )

# Final batch - only resume
print()
print( '---------------------------' )
print()
print( 'Test: Final sitemap' )
print( 'Expect: 31..39' )
test( URL30, OPT. RESUME )

# Verify that versions weren't updated
print()
print( '---------------------------' )
print()
print( 'Test: Remove urls missing from latest sitemap' )
print( 'Expect: <nothing>' )
test( URL30, OPT. REMOVE )

# Show that cache has all urls
print()
print( '---------------------------' )
print()
print( 'Test: Show what is cached' )
print( 'Expect: 11..19 21..29 31..39' )
test( URL30, OPT. CACHED )

# Test partial with filter

# Iterate over filtered sitemap
EVEN = '[2468]\\.'
print()
print( '---------------------------' )
print()
print( 'Test: Fetch only even numbers' )
print( 'Expect: 22, 24, 26, 28' )
test( URL20, EVEN )

# Remove all that rest from the cache
print()
print( '---------------------------' )
print()
print( 'Test: Remove urls missing from latest sitemap' )
print( 'Expect: 11..19 21, 23, 25, 27, 29 31..39' )
test( URL30, OPT. REMOVE )

# Test new
print()
print( '---------------------------' )
print()
print( 'Test: Sitemap of all 20s but iterate only over new ones' )
print( 'Expect: 21, 23, 25, 27, 29' )
test( URL20, OPT. NEWONLY )

# Iterate with filter but cache everything
print()
print( '---------------------------' )
print()
print( 'Test: Fetch only even numbers, cache all' )
print( 'Expect: 22, 24, 26, 28' )
test( URL20, EVEN, OPT. CACHEALL )

# Now iterating over new urls should get none
print()
print( '---------------------------' )
print()
print( 'Test: Iterate all new urls' )
print( 'Expect: <none>' )
test( URL20, OPT. NEWONLY )

# Resume after completed
print()
print( '---------------------------' )
print()
print( 'Test: Resume after completed' )
print( 'Expect: <None>' )
test( URL30, OPT. RESUME )






















