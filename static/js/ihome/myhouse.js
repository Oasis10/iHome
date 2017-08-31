function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function(){
    $(".auth-warn").show();

    $.get('/api/v1.0/auth',function (resp) {
       if(resp.data.real_name && resp.data.id_card){
           $(".auth-warn").hide();
           //    查询用户名下房源
        $.get('/api/v1.0/houses/users',function (resp) {
            if(4101==resp.errno){
                location.href = '/'
            }else if(0==resp.errno){
                rendered_html = template('house-list-info', {houses:resp.houses});
                $('#houses-list').append(rendered_html)
            }
        })
       }else{
           $("#houses-list").hide();
       }
   });


});

