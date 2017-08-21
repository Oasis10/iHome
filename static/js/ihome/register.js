function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

// 生成图片验证码
function generateImageCode(){
//    生成编号
//    严格遵循唯一性，使用uuid生成id
    imageCodeId = generateUUID();

//    设置img的src属性
    var imageUrl = '/api/v1.0/imagecode?id='+imageCodeId;
    $('.image-code img').attr('src', imageUrl)
}


function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }


    // $.get("/api/v1.0/smscode", {mobile:mobile, image_code_text:imageCode, image_code_id:imageCodeId},
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');


    $.get('/api/v1.0/smscode',
        {
            mobile: mobile,
            image_code_id: imageCodeId,
            image_code_text: imageCode
        },
        function (data) {
            // 判断是否成功
            if (4003==data.errno){
                // $('#mobile-err').hide();
                $('#mobile-err span').html(data.errmsg);
                // $('#mobile-err').show();
                $('.phonecode-a').attr('onclick', 'sendSMSCode();');
            }
            else if ('0' != data.errno) {
                $('#image-code-err span').html(data.errmsg);
                $("#image-code-err").show();
                $('.phonecode-a').attr('onclick', 'sendSMSCode();');
            }
            else {
                alert(data.data);
                //    倒计时60秒，60秒后允许用户重新发送短信
                var num = 5;
                //    设置计时器
                var t = setInterval(function () {
                    //    当计时为1s时，清除计时器
                    if (1 == num) {
                        clearInterval(t);
                        $('.phonecode-a').html('获取验证码');
                        $('.phonecode-a').attr('onclick', 'sendSMSCode();');
                    }
                    else {
                        num -= 1;
                        $('.phonecode-a').html(num + 's');
                    }
                }, 1000, 5)
            }
        })
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    // 处理手机号input框的ajax请求
    $('#mobile').blur(function () {
        var mobile = $('#mobile').val();
        $.get('/api/v1.0/mobile', {'mobile':mobile}, function (resp) {
            $('#mobile-err span').html(resp.errmsg);
            $('#mobile-err').show();
        })
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
    var req = {
        'mobile':mobile,
        'sms_code':phoneCode,
        'password':passwd
    };
    //    向后端发送注册请求
        $.ajax({
            url:'/api/v1.0/user',
            type:'put',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            // "X-XSRFToken": getCookie("_xsrf")
            contentType:'application/json',
            dateType:'json',
            data:JSON.stringify(req),
            success:function (resp) {
                if('0' == resp.errno){
                    alert('注册成功！');
                    location.href = '/'
                }else if('4001' == resp.errno){
                    location.href = '/login.html'
                }else{
                // 在前端中向用户展示错误信息
                    $('#password2-err span').html(resp.errmsg);
                    $('#password2-err').show()
                }
            }
        })
    });
})