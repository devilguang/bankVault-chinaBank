//写cookies
function setCookie(name, value) {
    var Days = 30;
    var exp = new Date();
    exp.setTime(exp.getTime() + Days * 24 * 60 * 60 * 1000);
    document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
}

//读取cookies
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");

    if (arr = document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}

//删除cookies
function delCookie(name) {
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval = getCookie(name);
    if (cval != null)
        document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
}

function loadDataProcess(node, data) {
    // $.messager.alert('提示', 'ok');
    var n = data.length
    for (var i = 0; i < n; ++i) {
        var m = data[i].children.length
        var works = data[i].children
        for (var j = 0; j < m; ++j) {
            // find a box node and then select it
            var node = $('#workSpaceTree').tree('find', works[j].id);
            $('#workSpaceTree').tree('select', node.target);
        }
    }
}
function treeSelectHandler(node) {
    var isWork = node.attributes.isWork
    if (!isWork) {
        return;
    }
    var title = node.text;
    var id = node.id;
    var workSeq = node.attributes.workSeq;
    var boxNumber = node.attributes.boxNumber;
    var c = '<table id="workGrid' + id + '" class="easyui-datagrid" data-options="url:\'getWorkData/' + workSeq + '\', queryParams:{processId: $(\'#processId\').val(), boxNumber: \'' + boxNumber + '\', thingStatus: \'notComplete\'}, toolbar:\'#workGridToolBar' + id + '\', singleSelect:true, fitColumns:true, loaded:false, rownumbers:true, loadMsg:\'' + title + '作业数据正在载入，请稍后...\', onDblClickRow:dbClickRow, pagination:true, fit:true, pageSize:20"><thead><tr><th field="boxNumber">箱号</th><th field="serialNumber" align="center">实物编号</th><th field="productType" align="center">实物类型</th><th field="className" align="center">品名</th><th field="subClassName" align="center">明细品名</th><th field="wareHouse" align="center">发行库</th><th field="status" formatter="statusFormatter" align="center">是否已更新</th><th field="operator" formatter="operatorFormatter" align="center">操作员</th><th field="lastUpdateTime" formatter="lastUpdateTimeFormatter" align="center">最新一次更新时间</th></tr></thead></table><div id="workGridToolBar' + id + '"><label for="workGrid' + id + 'StatusCombobox" style="margin-left:5px;margin-right:5px;">状态</label><input id="workGrid' + id + 'StatusCombobox" style="margin-right:20px;padding-top:5px;" /><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid' + id + '\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript"> function dbClickRow(index, row){ /*$.messager.alert(\'提示\', \'select\'+index);*/ updateInfo(index, row); } function initPagination(){$(\'#workGrid' + id + '\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});} function initToolbar(){ $(\'#workGrid' + id + 'StatusCombobox\').combobox({valueField: \'id\', textField: \'text\', editable: false, data: [{id: \'notComplete\', text: \'未完成\'}, {id: \'all\', text: \'全部\'}, {id: \'complete\', text: \'已完成\'}, ], panelHeight: \'auto\', \'onSelect\':function(record){ $(\'#workGrid' + id + '\').datagrid(\'options\').queryParams[\'thingStatus\'] = record.id; $(\'#workGrid' + id + '\').datagrid(\'reload\'); },}).combobox(\'setValue\', \'notComplete\'); }</script>';
    addTab(title, c);
}
function addTab(title, content) {
    if ($('#tbs').tabs('exists', title)) {
        $('#tbs').tabs('select', title);
    } else {
        $('#tbs').tabs('add', {
            title: title,
            content: content,
            closable: true,
        });

        initPagination();
        initToolbar();
    }
}
function statusFormatter(value, row, index) {
    if (value == 0) {
        return '<img src="' + $('#noStatus').attr('value') + '"></img>';
    } else {
        return '<img src="' + $('#okStatus').attr('value') + '"></img>';
    }
}
function operatorFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}
function lastUpdateTimeFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}

var url;
/*function initUpdateInfoDlg(row){
 if (row.productType == '银元类' || row.productType == '金银币章类'){
 $('#thing2').attr({'style':'display:none'});
 }
 else{
 $('#thing1').attr({'style':'display:none'});
 }

 if (row.status == 1){
 // 记录已更新, 待编辑
 $('#editBtn').attr({'style':'width:90px'});
 $('#saveBtn').attr({'style':'width:90px;display:none'});

 // 根据实物类型, 处理确认输入框的显示情况
 $('#UpdateInfogrossWeight').textbox('readonly', true);
 if (row.productType == '银元类' || row.productType == '金银币章类'){
 $('#UpdateInfodiameter').textbox('readonly', true);
 $('#UpdateInfothick').textbox('readonly', true);
 }
 else{
 $('#UpdateInfolength').textbox('readonly', true);
 $('#UpdateInfowidth').textbox('readonly', true);
 $('#UpdateInfoheight').textbox('readonly', true);
 }
 }
 else{
 // 记录未更新
 $('#editBtn').attr({'style':'width:90px;display:none'});
 $('#saveBtn').attr({'style':'width:90px'});
 }
 }*/
function unInitUpdateInfoDlg() {
    /*$('#thing2').attr({'style':''});
     $('#thing1').attr({'style':''});

     $('#UpdateInfogrossWeight').textbox('readonly', false);

     $('#UpdateInfodiameter').textbox('readonly', false);
     $('#UpdateInfothick').textbox('readonly', false);

     $('#UpdateInfolength').textbox('readonly', false);
     $('#UpdateInfowidth').textbox('readonly', false);
     $('#UpdateInfoheight').textbox('readonly', false);*/
}
function closeUpdateInfo() {
    $.ajax({
        type: "get",
        url: "http://127.0.0.1:8000/gsinfo/cancel/",
        dataType: "jsonp",
        jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
        jsonpCallback: "success_jsonpCallback",
        data: {}
    });
    $('#UpdateInfoDlg').dialog('close');
    //unInitUpdateInfoDlg();
}
$('.panel-tool').click(function () {
    $.ajax({
        type: "get",
        url: "http://127.0.0.1:8000/gsinfo/cancel/",
        dataType: "jsonp",
        jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
        jsonpCallback: "success_jsonpCallback",
        data: {}, success: function (data) {
        }
    })
})

function updateInfo(index, row) {
    // $('#masking').hide()
    $("#filePathList").html('')
    var fileArr = []
    $('#UpdateInfoDlg').dialog('open').dialog('center').dialog('setTitle', '更新信息');
    $('#editBtn').attr({'style': 'width:90px;display:none'});
    $('#saveBtn').attr("onclick", "upLoadImg(" + row.boxNumber + ", \'" + row.serialNumber + "\')").css('width', '90px');
    $('#UpdateInfoForm').form('clear');
    $('.serialNumber').text(row.serialNumber);
    $.ajax({
        type: "GET",
        url: "getPictures/",
        data: {
            "boxNumber": row.boxNumber,
            "serialNumber": row.serialNumber
        }, success: function (data) {
            var data = JSON.parse(data)
            var havePic = data.havePic

            // if (havePic == false) {
            //     var timer = setInterval(function () {
            //         $.ajax({
            //             type: 'get',
            //             url: 'http://127.0.0.1:8000/gsinfo/getSeq/',
            //             dataType: "jsonp",
            //             jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
            //             jsonpCallback: "success_jsonpCallback",
            //             data: {
            //                 serialNumber: row.serialNumber
            //             }, success: function (data) {
            //                 var file = data.filePath
            //                 var rephotoPathSrc = data.rephotoPath
            //                 var stop = data.stop
            //                 if (stop == 'True') {
            //                     clearInterval(timer)
            //                     return
            //                 }
            //                 if (data.havePic == true && file) {
            //                     var imgList = document.getElementById('filePathList')
            //                     var file = data.filePath
            //                     fileArr.push(file)
            //                     var li = document.createElement('li')
            //                     li.innerHTML = '<img src ="http://127.0.0.1:8000/' + file + '"/>' +
            //                         '<div class="btnWrap"><button id="rephotograph" href="#"  class="rephotograph">重拍</button>' +
            //                         '<button id="removePic" href="#" class="easyui-linkbutton">删除</button></div>';
            //                     imgList.appendChild(li)
            //                     rephotograph() //重拍图片的方法
            //                     removePic(row.boxNumber, row.serialNumber)  //删除图片的方法
            //                 }
            //                 if (rephotoPathSrc) {
            //                     $("#filePathList>li").eq(picIndex).children().eq(0).attr('src', "http://127.0.0.1:8000/" + rephotoPathSrc)
            //                     $("#filePathList>li").eq(picIndex).children().eq(1).children().eq(0).attr('disabled', false).css('opacity', 1)
            //                 }
            //             }
            //         })
            //     }, 2000)
            //     // upLoadImg(row.boxNumber, row.serialNumber)  //上传图片的方法
            // } else {
            //     $("#saveBtn").attr('disable', true)
            //     var filePathList = data.filePathList
            //     var imgList = document.getElementById('filePathList')
            //     for (var i = 0; i < filePathList.length; i++) {
            //         var li = document.createElement('li')
            //         // http://192.168.16.4:8000
            //         li.innerHTML += '<img src ="/' + filePathList[i] + '"/>' +
            //             '<div class="btnWrap"><button id="rephotograph" href="#" class="rephotograph" >重拍</button><button id="removePic" href="#" class="easyui-linkbutton">删除</button></div>';
            //         imgList.appendChild(li);
            //         rephotograph()
            //         removePic(row.boxNumber, row.serialNumber) //删除按钮
            //     }
            //     // upLoadImg(row.boxNumber, row.serialNumber)  //上传图片的方法
            // }
            
            
        }
    });
    //url = 'updatePhotographingInfo/';
}
//点击重拍
var picIndex; //点击重拍的索引值
function rephotograph() {
    $("#filePathList>li").on('click', '.rephotograph', function () {
        $(this).attr('disabled', true).css('opacity', '0.5')
        picIndex = $(this).parents("li").index()
        var fullFile = $(this).parent().siblings().attr('src')
        var index = fullFile.indexOf('static')
        var index1 = fullFile.substr(index).lastIndexOf('\\') ? fullFile.substr(index).lastIndexOf('\\') : fullFile.substr(index).lastIndexOf('/')
        var fileName = fullFile.substr(index).substr(index1 + 1)
        $.ajax({
            type: "get",
            url: "http://127.0.0.1:8000/gsinfo/rephotograph/",
            dataType: "jsonp",
            jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
            jsonpCallback: "success_jsonpCallback",
            data: {
                fileName: fileName
            }, success: function (data) {
                $(".rephotograph").eq(picIndex).parent().siblings().attr('src', '/static/img/delete.png')
            }
        })

    })
}
//删除方法
//http://127.0.0.1:8000/static\upload\1-08-217-113-A.jpg】
function removePic(boxNumber, serialNumber) {
    $("#filePathList>li").on('click', '.easyui-linkbutton', function () {
        $(this).parent().parent().remove()
        var fullFile = $(this).parent().siblings().attr('src')
        var index = fullFile.indexOf('static')
        var index1 = fullFile.substr(index).lastIndexOf('\\') ? fullFile.substr(index).lastIndexOf('\\') : fullFile.substr(index).lastIndexOf('/')
        var fileName = fullFile.substr(index).substr(index1 + 1)
        $.ajax({
            type: 'post',
            url: 'delectPic/',
            data: {
                "boxNumber": boxNumber,
                "serialNumber": serialNumber,
                'fileName': fileName
            }
        })
    })
}
//上传图片的方法
function upLoadImg(boxNumber, serialNumber) {
    if ($("#filePathList>li").length == 0) {
        $.messager.alert({    // 显示失败信息
            title: '提示',
            msg:'请至少选择一张照片上传',
        });
        return
    }
    // $('#masking').show()
    var imgSrc = []
    var serial_number = []
    var img_path = {}
    for (var i = 0; i < $("#filePathList>li").length; i++) {
        var index1 = $("#filePathList>li").eq(i).children('img').attr('src').indexOf('static')
        imgSrc.push($("#filePathList>li").eq(i).children('img').attr('src').substr(index1))
        var index = $("#filePathList>li").eq(i).children('img').attr('src').substr(index1).split('.')[0].lastIndexOf('-')
        serial_number.push($("#filePathList>li").eq(i).children('img').attr('src').substr(index1).split('.')[0].substr(index + 1))
    }
    for (var i = 0; i < imgSrc.length; i++) {
        img_path[serial_number[i]] = imgSrc[i]
    }
    $.ajax({
        type: 'get',
        url: 'http://127.0.0.1:8000/gsinfo/upload/',
        dataType: "jsonp",
        jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
        jsonpCallback: "success_jsonpCallback",
        data: {
            img_path: JSON.stringify(img_path)
        },
         beforeSend: function (xhr) {
            $.messager.progress({text: '正在上传中，请稍后....'});
        },
        success: function (data) {
            $.ajax({
                type: 'post',
                url: 'http://192.168.16.4:8000/gsinfo/photographing/updatePhotographingInfo/',
                // dataType: "jsonp",
                // jsonp: "jsoncallback", //服务端用于接收callback调用的function名的参数
                // jsonpCallback: "success_jsonpCallback",
                data: {
                    boxNumber: boxNumber,
                    serialNumber: serialNumber,
                    pic_path: JSON.stringify(data)
                }, success: function (data) {
                    var data = JSON.parse(data)
                    if (data.success == true) {
                        $('#UpdateInfoDlg').dialog('close');
                    }
                }
            })
        }
    })
}


function editInfo() {
    var productType = $('#UpdateInfoproductType').textbox('getValue');
    // 根据实物类型, 处理确认输入框的显示情况
    $('#UpdateInfogrossWeight').textbox('readonly', false);
    if (productType == '银元类' || productType == '金银币章类') {
        $('#UpdateInfodiameter').textbox('readonly', false);
        $('#UpdateInfothick').textbox('readonly', false);
    }
    else {
        $('#UpdateInfolength').textbox('readonly', false);
        $('#UpdateInfowidth').textbox('readonly', false);
        $('#UpdateInfoheight').textbox('readonly', false);
    }
    $('#editBtn').attr({'style': 'width:90px;display:none'});
    $('#saveBtn').attr({'style': 'width:90px'});
}

// function saveInfo() {
//     $('#UpdateInfoForm').form({
//         url: url,
//         queryParams: {
//             csrfmiddlewaretoken: getCookie('csrftoken'),
//             operator: $('#operator').val(),
//         },
//         onSubmit: function (param) {
//             /*var productType = $('#UpdateInfoproductType').textbox('getValue');
//              var grossWeight = $('#UpdateInfogrossWeight').textbox('getValue');
//              if (productType == '银元类' || productType == '金银币章类') {
//              var diameter = $('#UpdateInfodiameter').textbox('getValue');
//              var thick = $('#UpdateInfothick').textbox('getValue');
//              if (grossWeight != '' && diameter != '' && thick != '') {
//              return true;
//              }
//              else {
//              $.messager.alert({
//              title: '提示',
//              msg: '毛重、直径、厚度均不能为空！'
//              });
//              return false;
//              }
//              }
//              else {
//              var length = $('#UpdateInfolength').textbox('getValue');
//              var width = $('#UpdateInfowidth').textbox('getValue');
//              var height = $('#UpdateInfoheight').textbox('getValue');
//              if (grossWeight != '' && length != '' && width != '' && height != '') {
//              return true;
//              }
//              else {
//              $.messager.alert({
//              title: '提示',
//              msg: '毛重、长度、宽度、高度不能为空！'
//              });
//              return false;
//              }
//              }
//              // return $(this).form('validate');*/
//         },
//         success: function (result) {
//             var result = eval('(' + result + ')');
//             if (!result.success) {
//                 $.messager.alert({		// 显示失败信息
//                     title: '提示',
//                     msg: result.message
//                 });
//             } else {
//                 $('#UpdateInfoDlg').dialog('close');        // 关闭对话框
//                 $.messager.show({		// 显示成功信息
//                     title: '提示',
//                     msg: result.message,
//                     timeout: 5000,
//                     showType: 'slide'
//                 });
//                 var node = $('#workSpaceTree').tree('getSelected');
//                 $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
//             }
//         }
//     });
//
//     $('#UpdateInfoForm').submit();
// }