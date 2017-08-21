function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 获取城区信息
    $.get('/api/v1.0/areas', function (resp) {
        if(resp.errno==0){
            // 1.使用js渲染
            // for (var i=0;i<resp.data.length;i++){
            //     var areaId = resp.data[i].aid;
            //     var areaName = resp.data[i].aname;
            //     // <option value="1">东城区</option>
            //     $('#area-id').append('<option value="'+areaId+'">'+areaName+'</option>')
            // }
            // 2.使用模板
            // rendered_html = template("areas-tmpl", {areas: resp.data});
            // $("#area-id").html(rendered_html);
            renderd_html = template("areas-tmpl", {areas: resp.data});
            $("#area-id").html(renderd_html)
        }else{
            alert(resp.errmsg)
        }
    });

    // 向后端提交房屋信息
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
    //    序列化表单数据
        var formData = {};
        $(this).serializeArray().map(function (x) {
            formData[x.name] = x.value
        });
    //    facility需要单独处理
        var facility = [];
        $(":checked[name=facility]").each(function (m,n) {
            facility[m] = n.value
        });
        formData['facility'] = facility;
    //    向后端发送ajax请求
        $.ajax({
            url:'/api/v1.0/houses',
            type:'put',
            contentType:'application/json',
            dataType:'json',
            data:JSON.stringify(formData),
            success:function (resp) {
                if(4101==resp.errno){
                    location.href = '/'
                }else if(0==resp.errno){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.house_id)
                }else{
                    // alert(resp.msg);
                    // location.href = '/'
                    $(".error-msg").html(resp.errmsg);
                    $(".error-msg").show()
                }
            }
        })
    });

//    提交房源主图片
    $("#form-house-image").submit(function (e) {
    //    阻止表单默认提交
        e.preventDefault();
    //    获取house_id
        var house_id = $("#house-id").val();
    //    异步表单提交
        $(this).ajaxSubmit({
            url:'/api/v1.0/houses/images',
            type:'put',
            headers:{'X-XSRFToken':getCookie('_xsrf')},
            dataType:'json',
            data:{house_id:house_id},
            success:function (resp) {
                if(4101==resp.errno){
                    location.href = '/'
                }else if(0==resp.errno){
                    $(".house-image-cons").append("<img src='"+resp.url+"'>")
                }else{
                    alert(resp.errmsg)
                }
            }

        })
    })
});


//
// # 前端发送过来的json数据的样例
// # {
// #     "title": "",
// #     "price": "",
// #     "area_id": "1",
// #     "address": "",
// #     "room_count": "",
// #     "acreage": "",
// #     "unit": "",
// #     "capacity": "",
// #     "beds": "",
// #     "deposit": "",
// #     "min_days": "",
// #     "max_days": "",
// #     "facility": ["7", "8"]
// # }