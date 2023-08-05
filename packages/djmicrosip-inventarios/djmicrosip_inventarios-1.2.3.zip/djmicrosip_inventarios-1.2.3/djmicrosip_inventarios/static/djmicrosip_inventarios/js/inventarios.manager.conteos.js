function ManejadorArticulosContados(args){
  //Definir tabla para mostrar conteos
  // var tabla_conteos = args.tabla_conteos
  //modal para mostrar articulos contados y no contados
  // var modal_informacion = args.modal_informacion
  var almacen = args.almacen

  this.MostrarPorContar = function (articulo_id){
    $.ajax({
      url:'/inventarios/get_series_porcontar/', 
      type : 'get', 
      data:{
        'articulo_id': articulo_id,
        'almacen_nombre':almacen.nombre
      }, 
      success: function(data){
        var message = "Faltan de contar las siguientes series\n";
        for(serie in data.series){
          message += data.series[serie] + "\n"
        }

        alert(message)
      },
      error: function() {
        alert('fallo algo')
      },
    });
  }

  this.MostrarSeriesContadas = function(articulo_id){
    $.ajax({
      url:'/inventarios/get_series_contadas/', 
      type : 'get', 
      data:{
        'articulo_id': articulo_id,
        'almacen_nombre':almacen.nombre
      }, 
      success: function(data){
        var message = "Series contadas\n";
        for(serie in data.series){
          message += data.series[serie] + "\n"
        }

        alert(message)
      },
      error: function() {
        alert('fallo algo')
      },
    });
  }

  MostrarPorContar = this.MostrarPorContar
  MostrarSeriesContadas = this.MostrarSeriesContadas
  StartSeriesEvents = function(){
    $(".badge.seriesSinContar").on("click", function(){ 
      var articulo_id = $(this).parent().parent().parent().find("input:hidden").val()
      MostrarPorContar(articulo_id)
    });

    $(".badge.seriesContadas").on("click", function(){ 
      var articulo_id = $(this).parent().parent().parent().find("input:hidden").val()
      MostrarSeriesContadas(articulo_id)
    });
  }

  // Muestra series sin contar en la lista de ultimos articulos ingresados
  StartSeriesAddEvents = function($element, span_class_name){
    if (span_class_name=="seriesSinContar")
    {
      $element.find(".badge.seriesSinContar").on("click", function(){ 
        var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
        MostrarPorContar(articulo_id)
      });
    }
    else if (span_class_name=="seriesContadas")
    {
      $element.find(".badge.seriesSinContar").on("click", function(){ 
        var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
        MostrarSeriesContadas(articulo_id)
      });
    }
  }

  StartSeriesEvents()

  this.ShowNewEntries = function(data){
    var $articulo_tr = $("#articulo-"+data.articulo_id).parent().parent()
    var contenido_existencia = data.existencia
    var span_class_name
    if (data.tipo_seguimiento=='S') {
      var span_class_name = "seriesSinContar"
      if (data.series_por_contar<=0) {
        span_class_name = "seriesContadas"
      }
      contenido_existencia += " <a href='#'> <span class='badge "+span_class_name+"'>Faltan "+data.series_por_contar+"</a>"
    }

    // Cuando ya existe en la tabla
    if ($articulo_tr.length>0)
    {
      $articulo_tr.children(":last").html(contenido_existencia);
      var temp = $articulo_tr.addClass("warning")[0]
      $articulo_tr.remove()
      $("#ultimos_articulos_contados tbody").prepend(temp)
    }
    // Si no existe en tabla
    else
    {  
      var contados = parseInt($("#articulosContadosId").text()) + 1
      $("#articulosContadosId").text(contados)
      $articulo_tr = "<tr class='warning'><td>"+data.articulo_clave+"<input type='hidden' id='articulo-"+data.articulo_id +"' value='"+data.articulo_id+"'/> </td><td>"+data.articulo_nombre+"</td><td>"+contenido_existencia+"</td></tr>"
      $("#ultimos_articulos_contados tbody").prepend($articulo_tr)
    }

    if (data.tipo_seguimiento=='S') 
    {  
      $articulo_tr = $("#articulo-"+data.articulo_id).parent().parent()
      StartSeriesAddEvents($articulo_tr, span_class_name)
    }

  }
}

var manejadorConteos = new ManejadorArticulosContados({
	almacen:{
		nombre: $("#almacen_nombre").val()
	}
})
