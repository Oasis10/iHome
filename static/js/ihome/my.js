function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url:'api/v1.0/session',
        type:'delete',
        headers:{'X-XSRFToken':getCookie('_xsrf')},
        dataType:'json',
        success:function (resp) {
            if(0==resp.errno){
                location.href = '/'
            }
        }
    })
}


$(document).ready(function(){
    //  初始化用户数据
    $.get('/api/v1.0/user', function (resp) {
        if(0==resp.errno){
            $('#user-name').html(resp.data.name);
            $('#user-mobile').html(resp.data.mobile);
            $('#user-avatar').prop('src', resp.data.avatar_url)
        }else{
            location.href = '/'
        }
    })
});