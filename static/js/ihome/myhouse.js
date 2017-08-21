$(document).ready(function(){
    $(".auth-warn").show();

    $.get('/api/v1.0/auth',function (resp) {
       if(resp.data.real_name && resp.data.id_card){
           $(".auth-warn").hide();
       }else{
           $("#houses-list").hide();
       }
   })
});

