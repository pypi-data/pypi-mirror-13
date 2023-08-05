
function cerrar_inventario(){

  var loginventario_id = $("#id_loginventario").val();
  var salida_id = $("#hidden_salida_id").val();
  var entrada_id = $("#hidden_entrada_id").val();

  var almacen_id = $("#almacen_id").val();
  var url = '/inventarios/getlogs_ini/?almacen_id='+almacen_id;

  $("#id_span_info_cierre_inventario").removeClass('hide');
  $("#btnCancel, #cerrar_inventario_confirm").hide();

  // Guardamos las existencias finales de cada articulo contado
  Promise.resolve($.get(url))
  .then(function(data){
    var promises = [];
    for(var log_id of data.logs_ini_ids)
    {
      var setlastExistenceURL = '/inventarios/setlogs_ini/?id='+log_id;
      var promise = Promise.resolve($.get(setlastExistenceURL));
      promises.push(promise);
    }

    return Promise.all(promises);
  })
  // Ajustamos las series de los articulos contados si existen articulos con series.
  .then(function(){
    var ajusteseries_URL = '/inventarios/inventarios_fisicos/ajustar_seriesinventario/?loginventario_id='+loginventario_id+'&&salida_id='+salida_id+'&&entrada_id='+entrada_id;
    return Promise.resolve($.get(ajusteseries_URL));
  })
  // Cerramos el inventario.
  .then(function(){
    var cerrar_inventario_URL = '/inventarios/close_inventario_byalmacen_view/?almacen_id='+almacen_id;
    return Promise.resolve($.get(cerrar_inventario_URL));
  })
  // Mostramos mensaje de proceso terminado
  .then(function(data){
      alert(data.mensaje);
      window.location = "/inventarios/almacenes/";
  })
  .catch(function(err){
    console.error(err);
  });
}

$("#cerrar_inventario_confirm").on("click", function(){
  cerrar_inventario();
});

function AgregarArticuloSinExistencia(args){
  var $triggerBtn = args.$triggerBtn
  var $triggerBtnByLine = args.$triggerBtnByLine

  mostrar_articulos_agregados = function(data){
    if (data.articulos_agregados > 0)
    {
      mensaje ='Se agregaron '+ data.articulos_agregados+ ' Articulos'
      if (data.articulo_pendientes > 0)
        mensaje = 'La aplicacion solo genero ' + data.articulos_agregados+ ' Articulos, faltaron de generar '+data.articulo_pendientes + ' Articulos.'
      alert(mensaje)
    }
    else
    {
      if (data.message != '')
        alert(data.message);
      else
        alert('No hay articulos por inicializar');
    }

    // limpiar formulario para agregar articulos
    $("#id_agregando_span, #id_agregando_span_all").attr("class","hide")
    $triggerBtn.show()
    $triggerBtn.attr("disabled",false)
  }

  AddArticles = function(attrs){
    var line = null
    if (attrs != undefined) {
      line = attrs.line
    }

    if ( $triggerBtn.attr("disabled") == "disabled")
      return false

    $triggerBtn.hide();
    $triggerBtn.attr("disabled",true);
    $("#btnCancel").hide()
    $("#id_agregando_span, #id_agregando_span_all").attr("class","")


    if (line == undefined) {
      $.ajax({
        url:'/inventarios/add_articulossinexistencia/', 
        type : 'get', 
        data:{
          'almacen_id' : $("#almacen_id").val(),
        }, 
        success: function(data){ 
          mostrar_articulos_agregados(data)
          $("#articulosnocont_porlinea_Modal, #articulosnocont_Modal").modal("hide")
          $("#btnCancel").show()
        },
        error: function() {
          alert('fallo algo')
        },
      }); 
    }else{
      $.ajax({
        url:'/inventarios/add_articulossinexistencia_bylinea/', 
        type : 'get', 
        data:{
          'almacen_id' : $("#almacen_id").val(),
          'linea_id': line,
          'ubicacion': $("#ubicacion").val(),
        }, 
        success: function(data){ 
          mostrar_articulos_agregados(data)
          $("#articulosnocont_porlinea_Modal, #articulosnocont_Modal").modal("hide")
          $("#btnCancel").show()
        },
        error: function() {
          alert('fallo algo')
        },
      }); 
    }
  }


  $triggerBtn.on("click", function(){
    AddArticles()
  })

  $triggerBtnByLine.on('click', function(){
    AddArticles({
      line: $("#id_linea").val()
    })
  })


}

AgregarArticuloSinExistencia({
  $triggerBtn: $("#btn_agregar_articulosinexistencia"),
  $triggerBtnByLine: $("#btn_agregar_articulosinexistencia_bylinea"),
})
