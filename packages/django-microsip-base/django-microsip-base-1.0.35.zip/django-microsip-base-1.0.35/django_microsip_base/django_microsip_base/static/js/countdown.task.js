
countdown.setLabels(
    ' milissegundo| segundo| minuto| hora| dia| semana| mes| año| década| século| milênio',
    ' milissegundos| segundos| minutos| horas| dias| semanas| meses| años| décadas| séculos| milênios',
    ' y ',
    ', ',
    'ahora');

function TaskCountDown(start, end, units, interval, next_execution){

    dateAdd = function(date, interval, units) {
      var ret = new Date(date); //don't change original date
      switch(interval.toLowerCase()) {
        case 'years'   :  ret.setFullYear(ret.getFullYear() + units);  break;
        // case 'quarter':  ret.setMonth(ret.getMonth() + 3*units);  break;
        case 'months'  :  ret.setMonth(ret.getMonth() + units);  break;
        case 'weeks'   :  ret.setDate(ret.getDate() + 7*units);  break;
        case 'days'    :  ret.setDate(ret.getDate() + units);  break;
        case 'hours'   :  ret.setTime(ret.getTime() + units*3600000);  break;
        case 'minutes' :  ret.setTime(ret.getTime() + units*60000);  break;
        // case 'second' :  ret.setTime(ret.getTime() + units*1000);  break;
        default       :  ret = undefined;  break;
      }
      return ret;
    };

    get_next_execution = function(start, interval, units){
        var next_execution = start;
        var fecha_ahora = new Date();
        while(next_execution < fecha_ahora){
            next_execution = dateAdd(next_execution, interval, units);
        }
        return next_execution;
    };

    is_valid = function(start, end, interval, units){
        if (isNaN(start.getTime())) {
            return false;
        }
        if (units === "") {
            return false;
        }
        return true;
    };

    get_next_execution_text = function(start, end, interval, units, next_execution) {
        var html = "";
        if (is_valid(start, end, interval, units)) {
            var fecha_ahora = new Date();
            var fecha_fin_valida = end.getTime() != NaN;
            tarea_vigente = true;
            if (fecha_fin_valida) {
                if (end< fecha_ahora) {
                    tarea_vigente = false;
                }
            }
            
            if (isNaN(tarea_vigente)){
                html += "Periodo de ejecución de la tarea ha caducado.";
            }
            else{
                var fecha_siguiente;
                if (isNaN(next_execution.getTime()) ) {
                    fecha_siguiente = start;
                }
                else{
                    fecha_siguiente = get_next_execution(start, interval, units);
                }
                

                if( fecha_siguiente <= fecha_ahora){
                    fecha_siguiente = fecha_ahora;
                    html += "Siguiente ejecución programada <strong>ahora</strong><br/>";
                }
                else{
                    html += "Siguiente ejecución programada en <strong>"+ countdown(fecha_siguiente).toString() +"</strong><br/>";
                }
                
                html += "<strong>Se repetira cada "+ units +" "+ interval +"</strong>";
            }
        }
        
        return html;
    };

    units = parseInt(units, 0);
    return get_next_execution_text(start, end, interval, units, next_execution);
}






