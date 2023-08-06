$(window).scroll(function(event) {
      
      var y = $(this).scrollTop();
      if (y >= 100) {
          $('#header').addClass('navbar-fixed-top');
          $('#header').attr('style','background-color: rgb(203, 203, 203); box-shadow: 0px 2px 5px #999;')
      } else {
          $('#header').removeClass('navbar-fixed-top');
          $('#header').attr('style','background-color: white;')
      }
});

//VALIDACION DE DETALLES SELECCIONADOS PARA ACTIVAR/DESACTIVAR EL BOTON DE ASIGNAR PROVEEDOR
$(".select_detail").on("change",function(){
	if ($(".select_detail:checked").length > 0)
	{
		$("#cambiar_proveedor").show();
	}
	else
	{
		$("#cambiar_proveedor").hide();
	};
});

//ASIGNACION DE NUEVO PROVEEDOR PARA ARTICULOS SELECCIONADOS
$("#btn_nuevo_proveedor").on("click",function(){
	$(".select_detail:checked").each(function(){
		var proveedor = $("#nuevo_proveedor").val();
		var tr = $(this).parent().parent();
		$("#table_"+proveedor).find("tbody").append(tr);
		$(this).attr("checked",false);
		$(".table").each(function(){
			if ($(this).find("tbody tr").length > 0)
			{
				$(this).show();
			}
			else
			{
				$(this).hide();
			};
		});
		$('#modal_proveedor').modal('hide');
		$(".select_detail").trigger("change");
	});
});

$("#generar_ordenes").on("click", function(){
	
	$(".table:visible").each(function(){
		var detalles = [];
		$table = $(this);
		var proveedor = parseFloat($table.find("#id_proveedor").val());
		$table.find("tbody tr").each(function(){
			// debugger;
			var id_art = $(this).find(".id_articulo").val();
			var unidades = $(this).find(".unidades").val();
			detalles.push({'articulo_id': parseFloat(id_art), 'unidades':parseFloat(unidades)});
		});
		$.ajax({
 	   	url:'/reorden/crea_documento/',
 	   	type : 'get',
 	   	data : {
 	   		'proveedor':proveedor,
 	   		'detalles':JSON.stringify(detalles),
 	   		'almacen_id': parseFloat($("#almacen_id").val()),
 	   	},
 	   	success: function(data){
 	   		location.reload();
 	   	},
 	   	error:function(){
 	   	},
	});
	});
});