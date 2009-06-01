
/* jquery override to case insensitive contains selector */

jQuery.expr[':'].contains = function(a,i,m){
    return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase())>=0;
};


function filter(data, cond){
    /* 
    Filters an array data with a callback function.
    Returns elements that pass the condition function
    */
    var out = new Array()

    func = cond || function(x){ return x.length > 0 }

    for (var i=0; i<data.length; i=i+1){
        elem = data[i]
        if (func(elem)) {
            out.push( elem )
        }
    }
    return out
}