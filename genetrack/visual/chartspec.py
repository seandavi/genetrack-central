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

color=RED; glyph=BAR; data=8946; row=new;

color=BLUE; glyph  =ORF; data= 34555; row=same

;color=GOLD; glyph=ORF; data=15664;        

data=1; glyph=AAA; color=DD0000;

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

VALID_COLORS = dict(
    BLUE=0x0000DD,  RED=0xDD0000,     GREEN =0x00DD00,
    GREY=0xCECECE,  LIGHT=0xEFEFEF,   BLACK=0x000000,
    WHITE=0xFFFFFF, PURPLE=0x990066,  ORANGE=0xFF3300, 
    TEAL= 0x009999, CRIMSON=0xDC143C, GOLD=0xFFD700,
    NAVY=0x000080,  SIENNA=0xA0522D,  LIGHT_GREEN=0x33FF00, 
    SPRING_GREEN=0x00FF7F, YELLOW_GREEN=0x9ACD32,
    )

def color_check(value):
    "Get a builtin color or hex value"
    #print VALID_COLORS
    value = value.upper()
    if value in VALID_COLORS:
        return VALID_COLORS[value]
    else:    
        return int( "0x%s" % value, 16)

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