function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

    //    向后端发送登录请求
        $.ajax({
            url:'/api/v1.0/session',
            type:'put',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            contentType:'application/json',
            dataType:'json',
            data:JSON.stringify({'mobile':mobile, 'password':passwd}),
            success:function (resp) {
                if(resp.errno != '0'){
                    $('#mobile-err span').html(resp.errmsg);
                    $('#mobile-err').show();
                }else{
                    location.href = '/';
                }
            }
        })
    });
})