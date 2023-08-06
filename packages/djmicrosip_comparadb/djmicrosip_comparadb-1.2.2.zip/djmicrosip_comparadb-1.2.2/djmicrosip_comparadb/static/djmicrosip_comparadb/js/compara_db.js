var articulos_diferencias_ids = [];
var progress = 0;
var count = 1;
var sync_count = 1;

function barra(){
	if ($("#progress-bar").width() >= $("#progress-bar").parent().width())
	{
		$("#progress-bar").width($("#progress-bar").width() - $("#progress-bar").width());
	}
	else
	{
		$("#progress-bar").width(($("#progress-bar").width() + 1));
	};
}

$("#btn_iniciar_escaneo").on("click",function(){
	$("#wait").modal('show');
	setInterval(barra, 500);
	$(this).attr("disabled",true);
	document.forms[0].submit();
});

$("#btn_iniciar_sync").on("click",function(){
	$("#wait").modal('show');
	setInterval(barra, 500);
	$(this).attr("disabled",true);
	var empresa_nombre = empresa;
	$.ajax({
		url:'/comparadb/sync',
		type:'get',
		data:{
			'empresa': empresa_nombre,
		},
		success:function(data){
			alert("Articulos Sincronizados");
			window.location = "/comparadb/articulos";
		},
		error:function(data){
			console.log("Error");
		}
	});
	// articulos_ids.forEach(function(articulo_id){
	// 	$.ajax({
	// 			url:'/comparadb/sync',
	// 			type:'get',
	// 			data:{
	// 				'articulo_id': articulo_id,
	// 				'empresa': empresa_nombre,
	// 			},
	// 			success:function(data){
	// 				var progress = sync_count / articulos_ids.length * 100;
	// 				$("#progress-bar").attr('style', 'width:'+progress+'%');
	// 				$("#progress-bar").text("Creando "+sync_count+" de "+articulos_ids.length+". "+parseFloat(progress).toFixed(2)+"%");
	// 				if (sync_count >= articulos_ids.length) {
	// 					alert("Articulos Sincronizados");
	// 					window.location = "/comparadb/articulos";
	// 				};
	// 				sync_count = sync_count + 1;
	// 			},
	// 			error:function(data){
	// 				console.log("Error");
	// 			}
	// 		});
	// });
});