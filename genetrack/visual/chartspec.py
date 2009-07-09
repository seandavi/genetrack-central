"""
Parses a chart specification from a text
"""
import pyparsing
from pyparsing import *

from genetrack import logger

test_input = """

#
#track spec
#

color  =  RED; glyph=BAR; data=8946; row=new;

color=BLUE; glyph  =ORF; data= 34555; row=same

;color=GOLD; glyph=ORF; data=15664;        

data=1; glyph=AAA;

"""

#from genetrack import logger
from itertools import *
from string import strip

def split(text, sep):
    "Split and strip whitespace in one call"
    return map(strip, text.split(sep))

VALID_GLYPHS = set( "AUTO BAR LINE ORF INTERVAL BOOKMARK" )

def glyph_check(value):
    return str(value).upper()

def color_check(value):
    return str(value)

# maps dictionary keys to validation functions
validator = dict(
    data=int, layer=int, glyph=glyph_check, color=color_check, 
    height=int, row=str,
    )

# attributes that must be present
REQUIRED_ATTRS = set('data glyph'.split())

def clean(text):
    """
    Cleans input to contain only, nonempty lines ending with semicolons.
    Makes creating parsing rules easier.
    """
    lines = map(strip, text.splitlines())
    lines = filter(None, lines)
    lines = filter(lambda r: not r.startswith('#'), lines)
    lines = map( lambda x: x.strip(';'), lines)
    lines = map( lambda x: x + ';', lines)
    return lines

def parse(text):
    """
    Parses the chart minilanguage and build a chart specific json dataset.
    """
    
    # clean and split the data to simplify parsing rule
    lines = clean(text)
        
    alphanums = '#+-.' + alphas + nums 
    
    name  = Word(alphanums).setResultsName("name")
    # values may include whitespace
    value = Optional(" ") + Word(alphanums + " ").setResultsName("value")
    pair  = name + "=" + value + ";"
    expr  = OneOrMore(Group(pair)) + StringEnd()

    # a json list with dictionaries for each track
    
    # trying to produce more useful error messages
    # so there is some catch and re-raise 
    data = []
    for lineno, line in zip(count(1), lines):
        try:
            row = dict()
            for result in expr.parseString(line):  
                name = result.name.lower()
                value = result.value.upper()
                row[name] = validator[name](value)
            data.append(row)
            
            # check required keys
            diff = REQUIRED_ATTRS - set(row.keys())
            if diff:
                text = ", ".join(diff)
                raise Exception("Missing required attributes: %s -> line %s" % (text, lineno) )
                
        except ParseException, exc:
            raise Exception('format error at line %s' %( lineno))
        except KeyError, exc:
            raise Exception('Unknown attribute: %s -> line %s' % (exc, lineno))
        except ValueError, exc:
            raise Exception('Attribute validation error: %s -> line %s' % (exc, lineno))

    # may not be empty
    if not data:
        raise Exception("Field must contain at least one track. Click 'Add' above.")
                    
    return data

def test():
    data = parse(test_input)
    for row in data:
        print row

if __name__ == '__main__':
    test()