
def filter(data, func=123):
    var out = new Array()
    for (entry in data){
        if (entry.lenght>0){
            out.push( entry )
        }
    }
    return out