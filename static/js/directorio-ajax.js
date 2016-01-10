$(document).ready(function() {
	

	$('#recomendacion').click(function(){
	        var url = document.getElementById("id_enlace");
	        var catid = url.value;
	         $.get('/like_category/', {category_id: catid}, function(data){
	                   $('#id_categoria_tags_input_tagsinput').html(data);
	                   $('#likes').hide();
	               });
	    });

});