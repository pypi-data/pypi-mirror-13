$("#id_articulo_text, #id_articulo_serie_text").addClass('form-control');
$("input[type='text']").on('focus', function () {
  $(this).select();
});

function InventarioManager(args){
  var $manejarseries = args.$manejarseries;
  var manejarseries = false;
  if ($manejarseries.length > 0)
    manejarseries = $manejarseries[0].checked;
  var $tipo_seguimiento = args.$tipo_seguimiento;
  
  var $articulo = args.$articulo;
  var $articulo_serie = args.$articulo_serie;
  var $serie = args.$serie;
  var $clave = args.$clave;
  var $contenedor_unidades = args.$contenedor_unidades;

  var $contenedor_detalles = args.$contenedor_detalles;
  var $modal_movimientos = args.$modal_movimientos;
  var $cancel_btn = args.$cancel_btn;
  var es_small = $("#extra_mobile_btn:visible").length>0;
  var $submitBtn = args.$submitBtn;

  this.CleanForm = function(){
    $('.remove.div').trigger('click');
    $contenedor_detalles.hide();
    $contenedor_unidades.find('input[type=number]').attr('style','');
    $contenedor_unidades.hide();
    if ($manejarseries.length > 0)
      manejarseries = $manejarseries[0].checked;
    
    $serie.val('');
    $serie.attr("disabled",false);
    $clave.val('');
    $articulo_serie.parent().hide();
    $submitBtn.attr("disabled",false);
    

    if (manejarseries) {
      $serie.show();
      $clave.hide();
      $serie.parent().find("input:text").focus();
      $articulo.parent().hide();
      $articulo.val('');
    }
    else{
      $serie.hide();
      $clave.show();
      $clave.focus();
      // $articulo.focus()
      // $articulo.parent().find("input:text").focus()
      $articulo.parent().show();
    }
  };

  var clean = this.CleanForm;

  manejar_series_event = function(){
    $manejarseries.on('change', function(){
      clean();
    });
  };

  initialize = function(){
    $articulo_serie.parent().hide();
    $serie.hide();
    $contenedor_detalles.hide();

    if (es_small === false){
      $cancel_btn.hide();
    }

    $contenedor_unidades.hide();
    manejar_series_event();

    $("#extra_mobile_btn").on("click", function(){
      if($("#extra_mobile:visible").length >0)
        $("#extra_mobile").hide();
      else
        $("#extra_mobile").show();
    });

  };

  initialize();
}

var inventario_manager =  new InventarioManager({
  $manejarseries: $("#manejarSeries"),
  $tipo_seguimiento:  $("#articuloSeguimientoUnidadesId"),
  $cancel_btn: $("#cancel_btn"),
  $articulo: $("#id_articulo"),
  $articulo_serie: $("#id_articulo_serie"),
  $serie: $("#serieArticuloId"),
  $clave: $("#id_clave_articulo"),
  $contenedor_unidades: $("#unidades_div"),
  $contenedor_detalles:  $("#articleDetailId"),
  $modal_movimientos: $("#movimiento_articulo_modal"),
  $submitBtn: $("#enviar_btn")
});


function EnviarExistencias(args){
  var $contenedor_unidades = args.$contenedor_unidades;
  var $ubicacion = args.$ubicacion;
  var $unidades = args.$unidades;
  var $manejarseries = args.$manejarseries;
  var $submitBtn = args.$submitBtn;
  var documentos = args.documentos;
  var $tipo_seguimiento = args.$tipo_seguimiento;
  var almacen = args.almacen;
  var $serie = args.$serie;
  var $articulo = args.$articulo;
  var manejarseries = false;
  if ($manejarseries.length > 0)
    manejarseries = $manejarseries[0].checked;

  if (manejarseries) {
    $articulo = args.$articulo_serie;
  }

  $manejarseries.on('change', function(){
    manejarseries = $manejarseries[0].checked;
    if (manejarseries) {
      $articulo = args.$articulo_serie;
    }
    else{
     $articulo = args.$articulo;
    }
  });

  IsValid = function(){
    if ($ubicacion.val() === ''){
        // alert("El campo ubicacion es obligatorio");
        
        var ubicacion = prompt("En que ubicacion se esta contando?");
        $ubicacion.val(ubicacion);

        if ($ubicacion.val() === '') {
          return false;
        }
    }
    else if ($articulo.find("option:selected").val() === undefined)
    {
      alert("El campo articulo es obligatorio");
      $articulo.parent().find("input").focus();
      return false;
    }
    else if ($unidades.val() === '')
    {
      alert("Unidades incorrectas");
      $unidades.show();
      $unidades.focus();
      return false;
    }
    else if ($.isNumeric($unidades.val()) === false )
    {
      $unidades.show();
      alert("Unidades incorrectas");
      $unidades.focus();
      return false;
    }

    return true;
  };

  SendData = function(){
    $submitBtn.attr("disabled",true);

    // datos para enviar a servidor
    data = {
      'entrada_id': documentos.entrada_id,
      'salida_id': documentos.salida_id,
      'ubicacion': $ubicacion.val(),
      'unidades': $unidades.val(),
      'costo_unitario':0,
      'articulo_id': $articulo.val()[0],
      'almacen_nombre':almacen.nombre,
      'tipo_seguimiento': $tipo_seguimiento.val()
    };
    if ($tipo_seguimiento.val() == 'S'){
      data.serie =  $serie.val();
    }

    $.ajax({
      url:'/inventarios/agregar_existencia/',
      type : 'get',
      data:data,
      success: function(data){
        // Mostrar nuevas entradas
        manejadorConteos.ShowNewEntries(data);
        inventario_manager.CleanForm();
      }
    });
  };

  onSubmit = function(){
    // Si el formulario es valido
    if(IsValid()){
      // Envia los datos
      SendData();
    }
  };

  $submitBtn.on('click', function(){
    onSubmit();
  });
 
}



EnviarExistencias({
  $ubicacion: $("#ubicacion"),
  $unidades: $("#id_unidades"),
  $articulo: $("#id_articulo"),
  $serie: $("#serieArticuloId"),
  $articulo_serie: $("#id_articulo_serie"),
  $manejarseries: $("#manejarSeries"),
  $submitBtn: $("#enviar_btn"),
  $contenedor_unidades: $("#unidades_div"),
  documentos: {
    entrada_id:$("#hidden_entrada_id").val(),
    salida_id:$("#hidden_salida_id").val(),
  },
  $tipo_seguimiento:  $("#articuloSeguimientoUnidadesId") ,
  almacen: {
    nombre : $("#almacen_nombre").val()
  }
});

$("#ubicacionMobil").on("change", function(){
  var ubicacion = $(this).val();
  $("#ubicacion").val(ubicacion);
});

$("#manejarSeriesMobil").on("change", function(){
  $("#manejarSeries").attr('checked', $(this).attr('checked'));
  $("#manejarSeries").trigger('change');
});
