function ClaveArticuloSearch(args) {
  var $articulo_clave = args.$articulo_clave;
  var $articulo = args.$articulo;
  var $modal_opciones = args.$modal_opciones;

  function CargarArticulo( articulo_id, articulo_nombre, tipo_seguimiento){
    $articulo.parent().find(".deck.div").attr('style','');
    $articulo.parent().find(".deck.div").html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
    $articulo.html('<option selected="selected" value="'+articulo_id+'"></option>');
    $("#articuloSeguimientoUnidadesId").val(tipo_seguimiento);
    $articulo.parent().find("input").hide();
    $articulo.trigger( "change" );
    $articulo.parent().show();
    $articulo.parent().parent().show();
    // if (manejarSeries == false) {
    //   $("#id_unidades").show();
    //   $("#id_unidades").focus();
    // }
  }
  // Carga las opciones de clave
  cargarOpciones = function(opciones){
    if (Object.keys(opciones).length > 0 ) {
      html_var = '';
      for (var articulo in opciones)
      {
        html_var = html_var + "<a href='#' class='clave_link'>" + articulo + "</a> " + opciones[articulo]+"<br>";
      }

      $("#opciones_clave_Modal").modal();
      $modal_opciones.find(".modal-body").html(html_var);
      $(".clave_link").on("click", function(){
        $articulo_clave.val($(this).text());
        $articulo_clave.trigger('change');
        $modal_opciones.modal('hide');
      });
    }
  };

  $articulo_clave.on("change", function(e){
    e.preventDefault();
    clave = $articulo_clave.val();
    if( clave !== null && clave !== '' ){
      $.ajax({
        url:'/inventarios/get_articulo_porclave/',
        type : 'get',
        data:{
          'clave': clave,
        },
        success: function(data){
            var opciones_clave =  data.opciones_clave;
            var articulo_nombre = data.articulo_nombre;
            var articulo_id = data.articulo_id;
            if (Object.keys(opciones_clave).length <= 0)
            {
              if (articulo_nombre === '')
              {
                alert('No se encontro ningun articulo con la clave');
              }
              else
              {
                CargarArticulo(articulo_id, articulo_nombre, 'N');
              }
            // Si hay opciones por mostrar
            }
            else
            {
              cargarOpciones(opciones_clave);
            }
        },
        error: function() {
          alert('fallo algo');
        },
      });
    }
    
  });
}

ClaveArticuloSearch({
  '$articulo_clave':$("#id_clave_articulo"),
  '$articulo':$("#id_articulo"),
  '$modal_opciones': $("#opciones_clave_Modal")
});