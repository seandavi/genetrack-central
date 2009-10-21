"""
Parses a chart specification from a text
"""
import pyparsing
from pyparsing import *
from itertools import *
from string import strip
from trackutil import *

test_input = """

#
#track spec
#

color=RED; style=BAR; data=8946; row=new;

color=blue; style  =ORF; data= 34555; row=same

;color=GOLD; style=ORF; data=15664;  arrow=10; strand=- ;     

data=1; style=AREA; color=#DD0000 10%; topaxis=true; strand=+

"""



def split(text, sep):
    "Split and strip whitespace in one call"
    return map(strip, text.split(sep))

XY_STYLES = set( 'BAR LINE STEP AREA SCATTER READS FIT_LINE FIT_AREA'.split() )
STYLES = set( list(XY_STYLES) + "SEGMENT ARROW ORF ZONE MARK EXON".split() )

def style_check(value):
    "Validates styles"
    if value.upper() not in STYLES:
        raise Exception('style=%s -> unknown style value' % value)
    return value.upper()

def arrow_check(value):
    "Validates arrows"
    if value.upper() not in ARROWS:
        raise Exception('arrow=%s -> unknown arrow value' % value)
    return ARROWS[value.upper()]

def target_check(value):
    "Validates targets"
    if value.upper() not in ('GLOBAL', 'LAST'):
        raise Exeption('target=%s -> unknown target' % value)
    return value.upper()
    
def set_transparency(color, alpha):
    "Sets the transparency of a color"
    # courtesy of Pindi Albert
    color = color & 0x00FFFFFF # zero out any existing alpha channel
    alpha = int(alpha*255//100) << 24 # change percent to the form 0x##000000
    return color | alpha # combine color with new alpha channel

def color_check(value):
    "Gets a builtin color or hex value. Also applies transparency"
    # remove markups for hexcode or percentage
    value = value.strip(' #%')
    # the optional second integer is the alpha channel
    elems = value.split() 
    color = elems[0]
    if color.upper() in COLORS:
        color = COLORS[color.upper()]
    else:    
        try:
            # tries to parse a hexadecimal color value
            color = int( "0x%s" % color, 16)
        except:
            raise Exception('color=%s -> unknown color value' % value)
    if len(elems)>1:
        color = set_transparency(color, int(elems[1]))        
    return color        

def boolean(value):
    "Validates boolean type values"
    if value.upper() in ('TRUE', 'T', '1', 'YES'):
        return 1
    elif value.upper() in ('FALSE', 'F', '0', 'NO'):
        return 0
    raise Exception('%s -> unknown boolean value (yes, no, true, false, 1, 0)' % value)

def int2(value):
    "Validates integers"
    try:
        return int(value)
    except:
        raise Exception('%s is not an integer' % value)

def float2(value):
    "Validates float numbers"
    try:
        return float(value)
    except:
        raise Exception('%s is not a number' % value)

# maps dictionary keys to validation functions
validator = dict(
    data=int2, style=style_check, 
    color=color_check, color2=color_check,
    height=int2, topx=boolean, tpad=int2, bpad=int2, rpad=int2, lpad=int2,
    h=int2, w=int2, arrow=arrow_check, lw=int2,
    label_offset=int2, target=target_check, show_labels=boolean, rotate=float2,
    bgcolor=color_check, grid=boolean, spline=float2,
    scaling=float2, threshold=float2,
    newaxis=int2,
    )

# attributes that must be present
REQUIRED_ATTRS = set('data style'.split())

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
                # attribute names are forced to lowercase
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