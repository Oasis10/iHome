function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(function () {
    var real_name = $('#real-name');
    var id_card = $('#id-card');
    // 获取用户实名制信息
    $.get('/api/v1.0/auth',function (resp) {
            var name = resp.data.real_name;
            var id = resp.data.id_card;
            if(0==resp.errno && (name && id)){
                real_name.val(resp.data.real_name);
                id_card.val(resp.data.id_card);
                // $('#sub-auth').hide()
                $('#sub-auth').remove()
            }else if(0==resp.errno){
                real_name.val(resp.data.real_name);
                id_card.val(resp.data.id_card);
            }else{
                location.href = '/'
            }
        }
   );

    // 提交用户实名制信息
    $('#form-auth').submit(function (e) {
        // 阻止表单默认提交
        e.preventDefault();
        if(!real_name.val()||!id_card.val()){
            $('.error-msg').show();
            return
        }
        var auth_data = {
          "real_name":real_name.val(),
          "id_card":id_card.val()
        };
        $.ajax({
            url:'/api/v1.0/auth',
            type:'put',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            contentType:'application/json',
            dataType:'json',
            data:JSON.stringify(auth_data),
            success:function (resp) {
                if (0==resp.errno){
                    alert(resp.errmsg)
                }else{
                    $('.error-msg').html(resp.errmsg);
                    $('.error-msg').show();
                }
            }
        })
    })
});
