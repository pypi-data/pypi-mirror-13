function ManejadorArticulosContados(args) {
  var almacen_nombre = args.almacen_nombre

  this.MostrarPorContar = function (articulo_id){
    $.ajax({
      url:'/inventarios/get_series_porcontar/', 
      type : 'get', 
      data:{
        'articulo_id': articulo_id,
        'almacen_nombre':almacen_nombre
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
        'almacen_nombre':almacen_nombre
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

  StartSeriesEvents()

  // Muestra series sin contar en la lista de ultimos articulos ingresados
  this.StartSeriesAddEvents = function($element, span_class_name){
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
}

function ArticuloSerieManager(args){
  var $articulo = args.$articulo_serie
  var $serie = args.$serie
  var $tipo_seguimiento = args.$tipo_seguimiento
  var almacen_id = args.almacen_id
  var $modal = args.$modal

  BuscarArticulo = function(serie){
    function CargarArticulo( articulo_id, articulo_nombre, tipo_seguimiento){  
      $articulo.parent().find(".deck.div").attr('style','');
      $articulo.parent().find(".deck.div").html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
      $articulo.html('<option selected="selected" value="'+articulo_id+'"></option>');
      $tipo_seguimiento.val(tipo_seguimiento);
      $articulo.parent().find("input").hide();
      $articulo.trigger( "change" );
      $articulo.parent().show();
      $articulo.parent().parent().show();
      // if (manejarSeries == false) {
      //   $("#id_unidades").show();
      //   $("#id_unidades").focus();
      // }
    }

    function cargarOpcionesSerie(opciones){
      html_var = '';

      for (articulo in opciones)
      { 
        html_var = html_var + "<a href='#' class='serie_link'><input type='hidden' value='"+articulo+"'/>" + opciones[articulo] + "</a><br>";
      }

      $modal.modal();
      $modal.find(".modal-body").html(html_var);
      $(".serie_link").on("click", function(){
        var articulo_id = $(this).find("input").val()
        var articulo_nombre = $(this).text()
        CargarArticulo(articulo_id, articulo_nombre, 'S')
        $modal.modal('hide')
      });
    }

    $.ajax({
        url:'/inventarios/get_articulo_porserie/', 
        type : 'get', 
        data:{
          'almacen_id': almacen_id,
          'serie': serie,
        },
        success: function(data){
            if (data.errors)
            {
              // FALTA dar opcion de selecionar articulo
              alert(data.errors)
              $articulo.parent().show()
              $articulo.parent().parent().show()
              $articulo.parent().find("input").focus()
            }
            else if(data.opciones)
            {
              cargarOpcionesSerie(data.opciones);
            }
            else
            {

              CargarArticulo(data.articulo_id, data.articulo_nombre, 'S')
            }
        },
        error: function() {
          alert('fallo algo');
        },
      });
  }

  $serie.on("change", function(e){
    e.preventDefault()
    var serie = $serie.val()
    if( serie != null && serie != '' )
    {
      BuscarArticulo(serie)
    }
  })
}

ArticuloSerieManager({
  $articulo_serie: $("#id_articulo_serie"),
  $serie: $("#serieArticuloId"),
  $tipo_seguimiento: $("#articuloSeguimientoUnidadesId"),
  $modal: $("#opciones_clave_Modal"),
  almacen_id: $("#almacen_id").val()
})