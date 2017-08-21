function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    // 判断用户是否登录,并填充用户头像
    $.get('/api/v1.0/user', function (resp) {
        if('0'==resp.errno){
        // 用户已经上传过头像
            $('#user-avatar').prop('src', resp.data.avatar_url)
        }else{
        // 用户未登录
            location.href = '/'
        }
    });

    $('#form-avatar').submit(function (e) {
    //    阻止表单默认提交
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/api/v1.0/avatar',
            type:'put',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            dataType:'json',
            success:function (resp) {
                if('0'==resp.errno){
                // 上传成功,填充用户上传的头像
                    $('#user-avatar').prop('src', resp.avatar_url)
                }else if('4101'==resp.errno){
                //    表示用户尚未登录
                    location.href = '/'
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });

//    修改用户名
    $('#form-name').submit(function (e) {
        e.preventDefault();
        var name = $('#user-name').val();
        var errmsg = $('.error-msg');
        $.ajax({
            url:'/api/v1.0/user',
            type:'post',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            data:{'name':name},
            dataType:'json',
            success:function (resp) {
                if(4101==resp.errno){
                    location.href = '/'
                }else{
                    errmsg.html(resp.errmsg);
                    errmsg.show()
                }
            }
        })
    })
});

