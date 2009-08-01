// browser related functionality

function get_position(obj) {
    // gets the position of the object
    return parseInt($(obj).css('left').slice(0,-2))
}

function set_position( obj, x ) {
    // sets the position of the object
    $(obj).css({'left':x});
}

function center_image(image){
    // centers the image on the viewport
    var image_w = parseInt( image.attr('width') );
    var wport_w = $('#viewport').width();
    var offset  = -(image_w - wport_w)/2;
    set_position(image, offset);
    return offset
}

function set_feature(image, offset, feature){
    // autoloads when hitting the next page
    
    var image_w = parseInt( image.attr('width') );
    var pixel_scale = parseFloat( image.attr('pixelscale') )
    
    // finding the new offset based on image position
    var newoffset = offset - get_position(image)
    
    //feature = feature + (offset * pixel_scale)
    var newfeature = feature + newoffset * pixel_scale
    
    //fill in the new coordinate
    $('#feature').val( parseInt(newfeature) )

    // when to trigger a page reload

    position = get_position(image)

    lower = 300
    upper = -( image_w - 500 )

    if ( (position > lower) | ( position < upper) ) {
        $('#loading').show();
        $('#id_submit_display').click(); 	
    }

}