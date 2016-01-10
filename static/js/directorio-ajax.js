
    function init(data) {
        var tags = data.split(',');
	        
	        for(var i = 0; i < tags.length; i++) {
	        document.getElementById('id_categoria_tags_input_tag').value = tags[i];
	        var e = $.Event( "keypress", { which: 13 } );
			$('#id_categoria_tags_input_tag').trigger(e);		
			}
    }

$(document).ready(function() {
	
	
	$('#recomendacion').click(function(){
	        var url = document.getElementById("id_enlace");
	        var catid = url.value;
	        $.get('/like_category/', {category_id: catid}, function(data){
	                  
						init(data);
	               });
	        
	    });
	

});

