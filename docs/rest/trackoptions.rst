Track Options
=============

Tracks are specified in in a format similar to GFF3 attributes. Example::

	row=1; color=RED; glyph=BAR; data=8946;
	row=2; color=BLUE; glyph=ORF; data=34555;
	row=2; color=GOLD; glyph=ORF; data=15664;

Required attributes
-------------------

All of these attributes must be present. 
Some prefilled default values get added automatically when you click the *Add* button.

**row**
	Is the row onto the which the drawing will take place (will autoincrement). 
	Reusing the same row will place features on the same subtrack.

**color** 
	is the color of the features that are drawn. Choices: RED, GREEN, BLUE, BLACK, 
	PURPLE, NAVY, GOLD or a hexcolor such as #FFACFC

**glyph** 
	is the type of small graphical icon that is drawn. Choices: ORF, SPLIT-ORF, LINE,

**width** 
	is the width of the line

**data** 
	is the id of the data that will be displayed on the track


Optional (advanced) attributes
------------------------------

These attributes may be used to further customize the track.

**color2** 
	is the secondary color (default GREEN). Used only for some types of glyphs.

**label**
	is the label that is displayed

**layer** 
	is the order in which features are are drawn when reusing the same row. 
	Higher layers mask lower ones

**alpha** 
	is the transparency in percent (default 100%). Used when features overlap.

**offset** 
	is the amount the track is shifted from its default location. 
	The value may be negative.

Smoothing, fitting and predictions will be applied to all chart types that support it, 
add -NOFIT to a glyph name to turn off fitting for that glyph (example BAR -> BAR-NOFIT).

	