// browser related functionality

function get_position(image) {
    return parseInt($(image).css('left').slice(0,-2))
}

function set_position( image, x ) {
    $(image).css({'left':x});
}

function setup_image(image){
    var image_w = parseInt( image.attr('width') );
    var wport_w  = $('#viewport').width();
    
    // image should not be smaller than the viewport
    if (image_w < wport_w) {
        image_w = wport_w
    }

    base_offset = -(image_w - wport_w)/2;
    pixel_scale = parseFloat( image.attr('pixelscale') )

    // the genomic location in the feature marker
    feature     = parseInt( $('#feature').val() )

    set_position(image, base_offset);
}

function set_offset(){
    offset = BASE_OFFSET - get_image_position()
	
	$('#offset').text( offset );
	$('#width').text( IMAGE_W );
	
	feature = FEATURE + offset * PIXEL_SCALE
	
	$('#feature').val( parseInt(feature) )
	
	pos = get_image_position( )

	lower = 300
    upper = -( IMAGE_W - 500 )
	
	if ( (pos > lower) | ( pos<upper) ) {
		$('#loading').show();
		$('#id_submit_display').click(); 	
	}

	//$('#temp').text( pos );
	
	return 
}