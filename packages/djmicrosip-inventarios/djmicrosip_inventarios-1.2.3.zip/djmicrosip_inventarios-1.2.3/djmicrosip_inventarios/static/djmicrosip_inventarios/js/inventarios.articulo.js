$("#id_articulo_text, #id_articulo_serie_text").addClass('form-control');
var es_small = $("#extra_mobile_btn:visible").length>0;
if (es_small)
{
  $("body").scrollTop(100);
}
var audio = new Audio('/static/sounds/beep-06.mp3');
audio.volume = 0.5;
function AriculoManeger(args){
  var $manejarseries = args.$manejarseries;
  var manejarseries = false;
  if ($manejarseries.length > 0)
    manejarseries = $manejarseries[0].checked;
  var $articulo = args.$articulo;
  var $articulo_serie = args.$articulo_serie;
  var $serie = args.$serie;
  var $clave = args.$clave;
  var $unidades = args.$unidades;
  var $tipo_seguimiento = args.$tipo_seguimiento;
  var $contenedor_detalles = args.$contenedor_detalles;
  var $contenedor_unidades = args.$contenedor_unidades;

  var $modal_movimientos = args.$modal_movimientos;

  var almacen_nombre = args.almacen.nombre;
  var almacen_id = args.almacen.id;
  onArticleChange = function($articulo){

    clearForm = function(){
      
      $clave.val('');
      $clave.show();
      $(".claveSearchBtn").show();
      $articulo.val('');
      $unidades.val('');
      $contenedor_detalles.hide();
      //Si es series
      if ($tipo_seguimiento.val() == 'S')
      {
        $clave.hide();
        $serie.show();
        $serie.attr("disabled",false);
        $serie.focus();
        $contenedor_unidades.find('input[type=number]').attr('style','');
        $contenedor_unidades.hide();
        $articulo.parent().hide();
      }

      var es_small = $("#extra_mobile_btn:visible").length>0;
      if (es_small)
      {
          es_small = $("#extra_mobile_btn:visible").length>0;
          if (es_small)
          {
            $("body").scrollTop(100);
          }
      }
      audio.play();
      
    };

    GetExistenciaArticulo = function (args){
      var data = args;
      
      showControlsToAddExistence = function(args){

        showDetallesMovimientos = function(){
           $.ajax({
            url:'/inventarios/get_movimientos_articulo/',
            type : 'get',
            data:{
              'almacen_id' : almacen_id,
              'articulo_id': $articulo.val()[0],
            },
            success: function(data){
              var detalles = data.detalles;
              var articulo_nombre = $articulo.parent().find(".deck.div").children().contents()[1].data;
              $modal_movimientos.find('.modal-header h4:first').html(articulo_nombre);
                
              var msg=  "<h4> Valores iniciales</h4> <strong>Existencia: </strong>"+ data.existencia_inicial+" <br/><h4> Movimientos</h4>\n <table class='table table-striped table-hover'><tr><th>Usuario/Ubicacion</th><th>Unidades</th><th>fecha</th></tr>";
              for(var detalle in detalles){
                msg += "<tr><td>"+detalles[detalle].usuario+"/"+detalles[detalle].ubicacion+"</td><td>"+ detalles[detalle].unidades +'</td><td>' +detalles[detalle].fechahora+'</td></tr>';
              }
              msg+="</table>";
              $("#movimiento_articulo_modal .modal-body").html(msg);
              $("#movimiento_articulo_modal").modal();
            },
            error: function() {
              alert('algo fallo');
            },
          });
        };


        var ya_ajustado = args.ya_ajustado;
        var tipo_seguimiento = args.articulo_seguimiento;
        $tipo_seguimiento.val(tipo_seguimiento);
        $(".claveSearchBtn").hide();
        // Si es seguimento por series y ya esta ajustado
        if (tipo_seguimiento == 'S' && ya_ajustado){
          $articulo.parent().find(".deck.div").find(".remove").trigger("click");
          $articulo.parent().parent().hide();
          $serie.focus();
          alert('Serie ya contada en el inventario');
        }
        else{
          var por_contar = '';
          var detalle_movimientos_link="";
          
          if (tipo_seguimiento == 'S'){
            $serie.attr("disabled",true);
            por_contar = "<a href='#''><span class='badge' id='porContar'>"+args.series_faltantes+"</span></a>";
            $unidades.val('1');
            $unidades.hide();
          }

          if (ya_ajustado){
            detalle_movimientos_link = "<a tabindex='-1' id='id_detalle_movimientos' href='#' role='buftton' data-toggle='modal'><i class='glyphicon glyphicon-info-sign icon-white'></i></a>";
            $('#spanEstadoConteo').attr("class","yaContado");
            $("#spanEstadoConteo").html("Ya contado "+ por_contar);
          }
          else{
            $('#spanEstadoConteo').attr("class","sinContar");
            $("#spanEstadoConteo").html("Sin contar "+por_contar);
          }

          $("#porContar").on("click", function(){
            var articulo_id = $articulo.val();
            var almacen_nombre = $("#almacen_nombre").val();
            manejadorConteos.MostrarPorContar($articulo.val()[0], almacen_nombre);
          });
          
          $contenedor_detalles.find(".articleDetailUnits").html(args.existencias + " en existencia. "+ detalle_movimientos_link);
          $contenedor_detalles.find(".articleDetailState").attr("class","yaContado");
          $contenedor_detalles.find(".articleDetailState").html("Ya contado "+ por_contar);
          
          $("#id_detalle_movimientos").on("click", function(){ showDetallesMovimientos($articulo); } );
          $contenedor_detalles.show();
          por_contar = "";
          $contenedor_unidades.show();
          var es_small = $("#extra_mobile_btn:visible").length>0;
          if (es_small) {
            $contenedor_unidades.attr('style','clear:both')  ;
          }else{
            $contenedor_unidades.attr('style','');
          }
          
          $unidades.focus();
          es_small = $("#extra_mobile_btn:visible").length>0;
          if (es_small)
          {
            $("body").scrollTop(100);
          }
          if (tipo_seguimiento == 'S'){
            $('#enviar_btn').focus();
          }
        }
      };

      $.ajax({
        url:'/inventarios/get_existencia_articulo/',
        type : 'get',
        data: data,
        success: function(data){
          showControlsToAddExistence(data);
        },
        error: function() {
          alert('fallo algo');
        },
      });
    };
    
    if( $articulo.val() === null ){
      clearForm();
      $contenedor_detalles.hide();
      $contenedor_unidades.find('input[type=number]').attr('style','');
      $contenedor_unidades.hide();
    }
    //Si se seleciono un articulo
    else{

      // $unidadesContiner.show()
      $clave.hide();
      var serie = $serie.val();
      GetExistenciaArticulo({
        'almacen': almacen_nombre,
        'articulo_id': $articulo.val()[0],
        'serie': serie,
      });
    }
  };

  $("#cancel_btn").on("click", function(){
    $articulo.parent().find(".deck.div").find(".remove").trigger("click");
    $articulo_serie.parent().find(".deck.div").find(".remove").trigger("click");
  });

  $articulo.on('change', function(){
    onArticleChange($articulo);
  });

  $articulo_serie.on('change', function(){
    onArticleChange($articulo_serie);
  });

}

var manager_articulo = new AriculoManeger({
  $manejarseries: $("#manejarSeries"),
  $articulo: $("#id_articulo"),
  $articulo_serie: $("#id_articulo_serie"),
  $serie: $("#serieArticuloId"),
  $clave: $("#id_clave_articulo"),
  $unidades: $("#id_unidades"),
  $tipo_seguimiento:  $("#articuloSeguimientoUnidadesId"),
  $contenedor_detalles:  $("#articleDetailId"),
  $modal_movimientos: $("#movimiento_articulo_modal"),
  $contenedor_unidades: $("#unidades_div"),
  almacen:{
    id:$("#almacen_id").val(),
    nombre:$("#almacen_nombre").val()
  }
});