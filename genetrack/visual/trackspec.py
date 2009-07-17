"""
Parses a chart specification from a text
"""
import pyparsing
from pyparsing import *

test_input = """

#
#track spec
#

color=RED; glyph=BAR; data=8946; row=new;

color=BLUE; glyph  =ORF; data= 34555; row=same

;color=GOLD; glyph=ORF; data=15664;  arrow=10 ;     

data=1; glyph=AAA; color=#DD0000 10%; topaxis=true

"""

from itertools import *
from string import strip
from trackutil import *

def split(text, sep):
    "Split and strip whitespace in one call"
    return map(strip, text.split(sep))

def glyph_check(value):
    return str(value).upper()

def arrow_check(value):
    if value not in ARROWS:
        raise Exception('invalid arrow %s' % value)
    return ARROWS[value]

def target_check(value):
    if value.upper() not in ('GLOBAL', 'LAST'):
        raise Exeption('invalid target %s' % value)
    return value.upper()
    
def set_transparency(color, alpha):
    "Sets the transparency of a color"
    # courtesy of Pindi Albert
    color = color & 0x00FFFFFF # zero out any existing alpha channel
    alpha = int(alpha*255//100) << 24 # change percent to the form 0x##000000
    return color | alpha # combine color with new alpha channel

def color_check(value):
    "Gets a builtin color or hex value. Also applies transparency"
    value = value.strip(' #%').upper()
    elems = value.split() # optional second integer is the alpha channel
    color = elems[0]
    if color in COLORS:
        color = COLORS[color]
    else:    
        color = int( "0x%s" % color, 16)
    if len(elems)>1:
        color = set_transparency(color, int(elems[1]))        
    return color        

def boolean(value):
    value = value.upper()
    if value in ('TRUE', 'T', '1'):
        return 1
    elif value in ('FALSE', 'F', '0'):
        return 0
    raise Exception('invalid boolean value %s' % value)
    
# maps dictionary keys to validation functions
validator = dict(
    data=int, layer=int, glyph=glyph_check, color=color_check, 
    height=int, topx=boolean, tpad=int, bpad=int, rpad=int, lpad=int,
    h=int, w=int, arrow=arrow_check, lw=int,
    label_offset=int, target=target_check,
    rotate=float
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
        
    alphanums = '%#+-._' + alphas + nums 
    
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
                name  = result.name.lower()
                value = result.value.strip()
                func  = validator.get(name, str)
                row[name] = func(value)
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