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
    return base_offset
}

function set_location(base_offset, image){
    // also autoloads when hitting the next page
    
    var image_w = parseInt( image.attr('width') );
    var feature = parseInt( $('#feature').val() )
    var pixel_scale = parseFloat( image.attr('pixelscale') )

    // finding the new coordinate based on the offset
    offset = base_offset - get_position(image)
    
    feature = feature + offset * pixel_scale
    
    //fill in the new coordinate
    $('#feature').val( parseInt(feature) )

    // when to trigger a page reload

    position = get_position(image)

    lower = 300
    upper = -( image_w - 500 )

    if ( (position > lower) | ( position < upper) ) {
        $('#loading').show();
        //$('#id_submit_display').click(); 	
    }

}