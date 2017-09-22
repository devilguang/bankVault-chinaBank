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
    var n = data.length;
    for (var i = 0; i < n; ++i) {
        var m = data[i].children.length;
        var works = data[i].children;
        for (var j = 0; j < m; ++j) {
            // find a work node and then select it
            var node = $('#workSpaceTree').tree('find', works[j].id);
            $('#workSpaceTree').tree('select', node.target);
        }
    }
}
function changeInputValue(idName, getIdName, productKey) {
    //名称：detailedName 型制类型： typeName 时代：peroid 制作地：producePlace  制作人：producer 铭文：carveName
    var value = $("#" + idName).val();
    var productType = $("#UpdateInfoForm").children().eq(2).children().eq(2).children().eq(1).val();
    var className = $("#BatchUpdateInfo-className").children().find('.textbox-value').val();
    var subClassName = $("#BatchUpdateInfo-subClassName").children().find('.textbox-value').val();
    var level = $("#BatchUpdateInfo-level").children().find('.textbox-value').val();
    $.ajax({
        type: 'post',
        url: 'checkInfo/',
        data: {
            subClassName:subClassName,
            className:className,
            productType: productType,
            key: productKey,
            value: value
        }, success: function (data) {
            var mes = JSON.parse(data);
            if (mes.success) {
                var vArray = mes.message;
                for (var i = 0; i < vArray.length; i++) {
                    var optionList = document.createElement('option');
                    optionList.value = vArray[i];
                    getIdName.appendChild(optionList);
                    $('#workGrid' + node.id).datagrid('reload');
                }
            } else {
                return
            }
        }
    })
}
function treeSelectHandler(node) {
    var isWork = node.attributes.isWork;
    if (!isWork) {
        return;
    }
    var title = node.text;
    var id = node.id;
    var subBoxNumber = node.attributes.subBoxNumber;
    /*var number ;
     if(subBoxNumber != ""){
     number = node.attributes.workSeq +"-"+ subBoxNumber;
     }else{
     number = node.attributes.workSeq;
     }*/
    var workSeq = node.attributes.workSeq;
    var boxNumber = node.attributes.boxNumber;
    var c = '<table id="workGrid' + id + '" class="easyui-datagrid" data-options="url:\'getWorkData/' + workSeq + '\', queryParams:{processId: $(\'#processId\').val(), boxNumber: \'' + boxNumber + '\', subBoxNumber: \'' + subBoxNumber + '\', thingStatus: \'notComplete\'}, toolbar:\'#workGridToolBar' + id + '\', singleSelect:true, fitColumns:true, loaded:false, rownumbers:true, loadMsg:\'' + title + '作业数据正在载入，请稍后...\', onDblClickRow:dbClickRow, pagination:true, fit:true, pageSize:20,"><thead><tr><th field="boxNumber" align="center">箱号</th><th field="serialNumber" align="center">实物流水号</th><th field="productType" align="center">类别</th><th field="className" align="center">品类</th><th field="subClassName" align="center">品名</th><th field="wareHouse" align="center">发行库</th><th field="status" formatter="statusFormatter" align="center">是否已更新</th><th field="operator" formatter="operatorFormatter" align="center">操作员</th><th field="lastUpdateTime" formatter="lastUpdateTimeFormatter" align="center">最新一次更新时间</th></tr></thead></table><div id="workGridToolBar' + id + '"><label for="workGrid' + id + 'StatusCombobox" style="margin-left:5px;margin-right:5px;">状态</label><input id="workGrid' + id + 'StatusCombobox" style="margin-right:20px;padding-top:5px;" /><a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="javascript:batchUpdateInfo(' + id + ')">信息缺省设置</a><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid' + id + '\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function dbClickRow(index, row){/*$.messager.alert(\'提示\', \'select\'+index);*/ updateInfo(index, row); } function initPagination(){$(\'#workGrid' + id + '\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});} function initToolbar(){ $(\'#workGrid' + id + 'StatusCombobox\').combobox({valueField: \'id\', textField: \'text\', editable: false, data: [{id: \'notComplete\', text: \'未完成\'}, {id: \'all\', text: \'全部\'}, {id: \'complete\', text: \'已完成\'}, ], panelHeight: \'auto\', \'onSelect\':function(record){ $(\'#workGrid' + id + '\').datagrid(\'options\').queryParams[\'thingStatus\'] = record.id; $(\'#workGrid' + id + '\').datagrid(\'reload\'); },}).combobox(\'setValue\', \'notComplete\'); }</script>';
    addTab(id, title, c);
    initPagination();
    initToolbar();
}
function addTab(id, title, content) {
    if ($('#tbs').tabs('exists', title)) {
        $('#tbs').tabs('select', title);
    } else {
        $('#tbs').tabs('add', {
            title: title,
            content: content,
            closable: true,
            id: id,
        });
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
// function initBatchUpdateInfoDlg(row) {
//     if (row.productType == '金银币章类') {
//         $('#batch-typeName').attr({'style': 'display:none'});
//         $('#batch-carveName').attr({'style': 'display:none'});
//         $('#batch-marginShape').attr({'style': 'display:none'});
//     }
//     if (row.productType == '银元类') {
//         $('#batch-detailedName').attr({'style': 'display:none'});
//         $('#batch-typeName').attr({'style': 'display:none'});
//         $('#batch-peroid').attr({'style': 'display:none'});
//         $('#batch-carveName').attr({'style': 'display:none'});
//         $('#batch-originalQuantity').attr({'style': 'display:none'});
//         $('#batch-marginShape').attr({'style': 'display:none'});
//     }
//
//     if (row.productType == '金银工艺品类') {
//         $('#batch-typeName').attr({'style': 'display:none'});
//         $('#batch-producePlace').attr({'style': 'display:none'});
//         $('#batch-producer').attr({'style': 'display:none'});
//         $('#batch-carveName').attr({'style': 'display:none'});
//         $('#batch-versionName').attr({'style': 'display:none'});
//         $('#batch-value').attr({'style': 'display:none'});
//         $('#batch-marginShape').attr({'style': 'display:none'});
//     }
//
//     if (row.productType == '金银锭类') {
//         $('#batch-versionName').attr({'style': 'display:none'});
//         $('#batch-value').attr({'style': 'display:none'});
//         $('#batch-marginShape').attr({'style': 'display:none'});
//     }
// }
function unInitBatchUpdateInfoDlg() {
    $('#batch-versionName').attr({'style': ''});
    $('#batch-value').attr({'style': ''});
    $('#batch-detailedName').attr({'style': ''});
    $('#batch-peroid').attr({'style': ''});
    $('#batch-originalQuantity').attr({'style': ''});
    $('#batch-producePlace').attr({'style': ''});
    $('#batch-producer').attr({'style': ''});
    $('#batch-marginShape').attr({'style': ''});
    $('#batch-typeName').attr({'style': ''});
    $('#batch-carveName').attr({'style': ''});
}
function batchUpdateInfo(id) {
    rows = $('#workGrid' + id).datagrid('getRows');
    row = rows[0];
    var subClassName = row.subClassName;
    var subArr = ['币', '元', '辅', '钱', '外元', '减元', '色元', '国内银元', '外国银元'];
    var dianArr = ['锭'];
    var gong = ['工'];
    var zhang = ['章'];
    subArr.forEach(function (item, index) {
        if (subClassName == item) {
            $("#batch_faceAmount").css({"display": "block"});//面值
            $("#batch_level").css("display", "block"); //等级
            $("#batch_peroid").css("display", "block");  //年代
            $("#batch_country").css("display", "block"); //国别
            $("#batch_zhangType").css("display", "none");//性质
            $("#batch_dingSecification").css("display", "none");//规格
            $("#batch_shape").css({"display": "none"}); //型制
        }
    });
    dianArr.forEach(function (item) {
        if (subClassName == item) {
            $("#batch_shape").css({"display": "block"}); //型制
            $("#batch_shape").children().eq(0).html('型制');
            $("#batch_level").css("display", "block"); //等级
            $("#batch_peroid").css("display", "block");  //年代
            $("#batch_country").css("display", "block"); //国别
            $("#batch_dingSecification").css("display", "block");//规格
            $("#batch_zhangType").css("display", "none");//性质
            $("#batch_faceAmount").css("display", " none");//面值
        }
    });
    gong.forEach(function (item) {
        if (subClassName == item) {
            $("#batch_shape").css("display", "block"); //器型
            $("#batch_shape").children().eq(0).html('器型');
            $("#batch_level").css("display", "block"); //等级
            $("#batch_peroid").css("display", "block");  //年代
            $("#batch_country").css("display", "block"); //国别
            $("#batch_dingSecification").css("display", "none");//规格
            $("#batch_zhangType").css("display", "none");//性质
            $("#batch_faceAmount").css("display", " none");//面值
        }
    });
    zhang.forEach(function (item) {
        if (subClassName == item) {
            $("#batch_zhangType").css("display", "block"); //性质
            $("#batch_level").css("display", "block"); //等级
            $("#batch_peroid").css("display", "block");  //年代
            $("#batch_country").css("display", "block"); //国别
            $("#batch_shape").css("display", "block"); //器型
            $("#batch_dingSecification").css("display", "none");//规格
            $("#batch_faceAmount").css("display", " none");//面值
        }
    });
    if (subClassName == '-' || subClassName == '') {
        $("#batch_level").css("display", "none"); //等级
        $("#batch_peroid").css("display", "none");  //年代
        $("#batch_country").css("display", "none"); //国别
        $("#batch_faceAmount").css("display", "none");//面值
        $("#batch_shape").css("display", "none");//形制
        $("#batch_dingSecification").css("display", "none");//规格
        $("#batch_zhangType").css("display", "none");//性质
    }
    if (row.status == 1) {
        $('#editBtn').attr('style', 'width:90px');
        $('#saveBtn').attr('style', 'width:90px; display:none;');
        $('#UpdateInfo-remark').textbox('readonly', true);
    }
    $('#BatchUpdateInfoDlg').dialog('open').dialog('center').dialog('setTitle', '信息缺省设置');
    $('#BatchUpdateInfoForm').form('clear');
    $('#BatchUpdateInfoForm').form('load', {
        productType: row.productType,
        className: row.className,
        subClassName: row.subClassName,
        wareHouse: row.wareHouse,
        boxNumber: row.boxNumber,
    });
    var arrId = ['batch_level', 'batch_peroid', 'batch_country', 'batch_faceAmount',
        'batch_dingSecification', 'batch_zhangType', 'batch_shape', 'batch_quality'];
    var toStringArr = [];
    for (var i = 0; i < arrId.length; i++) {
        toStringArr.push($("#" + arrId[i]).children().eq(0).html());
    }
    $.ajax({
        type: 'post',
        url: 'getReadyInfo/',
        data: {
            className: row.className,
            subClassName: row.subClassName,
            productType: row.productType,
            field: toStringArr.join(";")
        }, success: function (data) {
            var data = JSON.parse(data);
            data.forEach(function (item) {
                if (item.name == '国别') {
                    $("#BatchUpdateInfo-country").combobox("loadData", item.val);
                }
                if (item.name == '等级') {
                    $("#BatchUpdateInfo-level").combobox("loadData", item.val);
                }
                if (item.name == '年代') {
                    $("#BatchUpdateInfo-peroid").combobox("loadData", item.val);
                }
                if (item.name == '规格') {
                    $("#BatchUpdateInfo-dingSecification").combobox("loadData", item.val);
                }
                if (item.name == '型制') {
                    $("#BatchUpdateInfo-shape").combobox("loadData", item.val);
                }
                if (item.name == '器型') {
                    $("#BatchUpdateInfo-shape").combobox("loadData", item.val);
                }
                if (item.name == '品相') {
                    $("#BatchUpdateInfo-quality").combobox("loadData", item.val);
                }
                if (item.name == '面值') {
                    $("#BatchUpdateInfo-faceAmount").combobox("loadData", item.val);
                }
                if (item.name == '性质') {
                    $("#BatchUpdateInfo-zhangType").combobox("loadData", item.val);
                }
            })
        }
    })
    url = 'updateNumberingInfo/';
}
function saveBatchUpdateInfo() {
    var tab = $('#tbs').tabs('getSelected');
    var id = tab[0].id;
    var node = $('#workSpaceTree').tree('find', id);
    var text = node.text;
    var batch_detailedName = $("#select_detailedName").val();//名称
    var workSeq = node.attributes.workSeq;
    var batch_level = $("#batch_level").children().find('.textbox-value').val(); //等级
    var batch_peroid = $("#batch_peroid").children().find('.textbox-value').val();//年代
    var batch_country = $("#batch_country").children().find('.textbox-value').val();//国别
    var batch_quality = $("#batch_quality").children().find('.textbox-value').val();//品相
    var batch_originalQuantity = $("#batch_originalQuantity").children().find('.textbox-value').val();//成色
    var batch_year = $("#batch_year").children().find('.textbox-value').val();//年份
    var batch_faceAmount = $("#batch_faceAmount").children().find('.textbox-value').val();//面值
    var batch_dingSecification = $("#batch_dingSecification").children().find('.textbox-value').val();//规格
    var batch_zhangType = $("#batch_zhangType").children().find('.textbox-value').val();//规格
    var batch_shape = $("#batch_shape").children().find('.textbox-value').val();//器型
    var batch_carveName = $("#select_carveName").val();//铭文
    var batch_remark = $("#batch_remark").children().find('.textbox-value').val();//备注
    var arrId = ['batch_level', 'batch_peroid', 'batch_country', 'batch_quality', 'batch_originalQuantity',
        'batch_year', 'batch_faceAmount', 'batch_dingSecification', 'batch_zhangType', 'batch_shape', 'batch_carveName', 'batch_remark', 'batch_detailedName'];
    var mustId = [];
    var Compulsory = ['batch_level', 'batch_peroid', 'batch_country', 'batch_quality', 'batch_originalQuantity'];
    for (var i = 0; i < arrId.length; i++) {
        if ($("#" + arrId[i]).css("display") !== "none") {
            Compulsory.forEach(function (item) {
                if (arrId[i] == item && $("#" + item).children().find('.textbox-value').val() == '') {
                    mustId.push(item)
                }
            });
        }
    }
    if (mustId.length > 0) {
        $.messager.alert('提示', "带*号的为必填项");
        return
    }
    $.ajax({
        type: 'post',
        url: 'updateNumberingInfo/',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            level: batch_level,
            detailedName: batch_detailedName,
            peroid: batch_peroid,
            year: batch_year,
            country: batch_country,
            faceAmount: batch_faceAmount,
            dingSecification: batch_dingSecification,
            zhangType: batch_zhangType,
            shape: batch_shape,
            appearance: batch_quality,
            mark: batch_remark,
            originalQuantity: batch_originalQuantity,
            remark: batch_remark,
            operator: $('#operator').val(), //操作员
            workSeq: workSeq,
            workName: text
        }, success: function (data) {
            var data = JSON.parse(data);
            if (data.success) {
                $.messager.confirm('提示', data.message, function (r) {
                    if (r) {
                        $("#BatchUpdateInfoDlg").dialog('close');
                        $('#workGrid' + node.id).datagrid('reload');
                    }
                });
                // 重载作业数据
            } else {
                $.messager.alert('提示', data.message);
            }
            $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
        }
    });
    // $('#BatchUpdateInfoForm').form({
    //     url: url,
    //     queryParams: {
    //         csrfmiddlewaretoken: getCookie('csrftoken'),
    //         operator: $('#operator').val(),
    //         workSeq: workSeq,
    //     },
    //     onSubmit: function (param) {
    //         return $(this).form('validate');
    //     },
    //     success: function (result) {
    //         var result = eval('(' + result + ')');
    //         if (!result.success) {
    //             $.messager.alert({		// 显示失败信息
    //                 title: '提示',
    //                 msg: result.message
    //             });
    //         } else {
    //             $('#BatchUpdateInfoDlg').dialog('close');        // 关闭对话框
    //             $.messager.show({		// 显示成功信息
    //                 title: '提示',
    //                 msg: result.message,
    //                 timeout: 5000,
    //                 showType: 'slide'
    //             });
    //             $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
    //         }
    //     }
    // });
    // $('#BatchUpdateInfoForm').submit();
}
function traverseArr(array, subClassName) {
    array.forEach(function (item, index) {
        if (subClassName == item) {

        }
    })
}


//单个信息修改方法
function initUpdateInfoDlg(row) {
    var subClassName = row.subClassName;
    var subArr = ['币', '元', '辅', '钱', '外元', '减元', '色元', '国内银元', '外国银元'];
    var dianArr = ['锭'];
    var gong = ['工'];
    var zhang = ['章'];
    subArr.forEach(function (item, index) {
        if (subClassName == item) {
            $("#single_faceAmount").css({"display": "block"});//面值
            $("#single_level").css("display", "block"); //等级
            $("#single_peroid").css("display", "block");  //年代
            $("#single_country").css("display", "block"); //国别
            $("#single_zhangType").css("display", "none");//性质
            $("#single_dingSecification").css("display", "none");//规格
            $("#single_shape").css({"display": "none"}); //型制
        }
    });
    dianArr.forEach(function (item) {
        if (subClassName == item) {
            $("#single_shape").css({"display": "block"}); //型制
            $("#single_shape").children().eq(0).html('型制');
            $("#single_level").css("display", "block"); //等级
            $("#single_peroid").css("display", "block");  //年代
            $("#single_country").css("display", "block"); //国别
            $("#single_dingSecification").css("display", "block");//规格
            $("#single_zhangType").css("display", "none");//性质
            $("#single_faceAmount").css("display", " none");//面值
        }
    });
    gong.forEach(function (item) {
        if (subClassName == item) {
            $("#single_shape").css("display", "block"); //器型
            $("#single_shape").children().eq(0).html('器型');
            $("#single_level").css("display", "block"); //等级
            $("#single_peroid").css("display", "block");  //年代
            $("#single_country").css("display", "block"); //国别
            $("#single_dingSecification").css("display", "none");//规格
            $("#single_zhangType").css("display", "none");//性质
            $("#single_faceAmount").css("display", " none");//面值
        }
    });
    zhang.forEach(function (item) {
        if (subClassName == item) {
            $("#single_zhangType").css("display", "block"); //性质
            $("#single_level").css("display", "block"); //等级
            $("#single_peroid").css("display", "block");  //年代
            $("#single_country").css("display", "block"); //国别
            $("#single_shape").css("display", "block"); //器型
            $("#single_dingSecification").css("display", "none");//规格
            $("#single_faceAmount").css("display", " none");//面值
        }
    });
    if (subClassName == '-' || subClassName == '') {
        $("#single_level").css("display", "none"); //等级
        $("#single_peroid").css("display", "none");  //年代
        $("#single_country").css("display", "none"); //国别
        $("#single_faceAmount").css("display", "none");//面值
        $("#single_shape").css("display", "none");//形制
        $("#single_dingSecification").css("display", "none");//规格
        $("#single_zhangType").css("display", "none");//性质
    }
    if (row.status == 1) {
        $('#editBtn').attr('style', 'width:90px');
        $('#saveBtn').attr('style', 'width:90px; display:none;');
        $('#UpdateInfo-remark').textbox('readonly', true);
    }
    else {
        $('#editBtn').attr('style', 'width:90px; display:none;');
        $('#saveBtn').attr('style', 'width:90px');
    }

    // if (row.productType == '金银币章类') {
    //     $('#typeName').attr({'style': 'display:none'});
    //     $('#carveName').attr({'style': 'display:none'});
    //     $('#marginShape').attr({'style': 'display:none'});
    //
    //     if (row.status == 1) {
    //         $('#UpdateInfo-versionName').textbox('readonly', true);
    //         $('#UpdateInfo-value').textbox('readonly', true);
    //         $('#UpdateInfo-detailedName').textbox('readonly', true);
    //         $('#UpdateInfo-peroid').textbox('readonly', true);
    //         $('#UpdateInfo-originalQuantity').textbox('readonly', true);
    //         $('#UpdateInfo-producePlace').textbox('readonly', true);
    //         $('#UpdateInfo-producer').textbox('readonly', true);
    //     }
    // }
    // if (row.productType == '银元类') {
    //     $('#detailedName').attr({'style': 'display:none'});
    //     $('#typeName').attr({'style': 'display:none'});
    //     $('#peroid').attr({'style': 'display:none'});
    //     $('#carveName').attr({'style': 'display:none'});
    //     $('#originalQuantity').attr({'style': 'display:none'});
    //     $('#marginShape').attr({'style': 'display:none'});
    //
    //     if (row.status == 1) {
    //         $('#UpdateInfo-versionName').textbox('readonly', true);
    //         $('#UpdateInfo-value').textbox('readonly', true);
    //         $('#UpdateInfo-producePlace').textbox('readonly', true);
    //         $('#UpdateInfo-producer').textbox('readonly', true);
    //     }
    // }
    //
    // if (row.productType == '金银工艺品类') {
    //     $('#typeName').attr({'style': 'display:none'});
    //     $('#producePlace').attr({'style': 'display:none'});
    //     $('#producer').attr({'style': 'display:none'});
    //     $('#carveName').attr({'style': 'display:none'});
    //     $('#versionName').attr({'style': 'display:none'});
    //     $('#value').attr({'style': 'display:none'});
    //     $('#marginShape').attr({'style': 'display:none'});
    //
    //     if (row.status == 1) {
    //         $('#UpdateInfo-detailedName').textbox('readonly', true);
    //         $('#UpdateInfo-peroid').textbox('readonly', true);
    //         $('#UpdateInfo-originalQuantity').textbox('readonly', true);
    //     }
    // }
    //
    // if (row.productType == '金银锭类') {
    //     $('#versionName').attr({'style': 'display:none'});
    //     $('#value').attr({'style': 'display:none'});
    //     $('#marginShape').attr({'style': 'display:none'});
    //
    //     if (row.status == 1) {
    //         $('#UpdateInfo-detailedName').textbox('readonly', true);
    //         $('#UpdateInfo-peroid').textbox('readonly', true);
    //         $('#UpdateInfo-originalQuantity').textbox('readonly', true);
    //         $('#UpdateInfo-producePlace').textbox('readonly', true);
    //         $('#UpdateInfo-producer').textbox('readonly', true);
    //         $('#UpdateInfo-typeName').textbox('readonly', true);
    //         $('#UpdateInfo-carveName').textbox('readonly', true);
    //     }
    // }

}
function unInitUpdateInfoDlg() {
    // $('#versionName').attr({'style': ''});
    // $('#value').attr({'style': ''});
    // $('#detailedName').attr({'style': ''});
    // $('#peroid').attr({'style': ''});
    // $('#originalQuantity').attr({'style': ''});
    // $('#producePlace').attr({'style': ''});
    // $('#marginShape').attr({'style': ''});
    // $('#typeName').attr({'style': ''});
    // $('#carveName').attr({'style': ''});
    // $('#UpdateInfo-versionName').textbox('readonly', false);
    // $('#UpdateInfo-value').textbox('readonly', false);
    // $('#UpdateInfo-detailedName').textbox('readonly', false);
    // $('#UpdateInfo-peroid').textbox('readonly', false);
    // $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    // $('#UpdateInfo-producePlace').textbox('readonly', false);
    // $('#UpdateInfo-producer').textbox('readonly', false);
    // $('#UpdateInfo-marginShape').textbox('readonly', false);
    // $('#UpdateInfo-typeName').textbox('readonly', false);
    // $('#UpdateInfo-carveName').textbox('readonly', false);
    // $('#UpdateInfo-remark').textbox('readonly', false);
}
function closeUpdateInfo() {
    $('#UpdateInfoDlg').dialog('close');
    unInitUpdateInfoDlg();
}
function returnFloat(value) {
    var value = Math.round(parseFloat(value) * 100) / 100;
    var xsd = value.toString().split(".");
    if (xsd.length == 1) {
        value = value.toString() + ".00";
        return value;
    }
    if (xsd.length > 1) {
        if (xsd[1].length < 2) {
            value = value.toString() + "0";
        }
        return value;
    }
}

function getReadyInfoInformation(row) {
    var arrId = ['UpdateInfo-level', 'UpdateInfo-peroid', 'UpdateInfo-country', 'UpdateInfo-faceAmount',
        'UpdateInfo-dingSecification', 'UpdateInfo-zhangType', 'UpdateInfo-shape', 'UpdateInfo-quality', 'UpdateInfo-zhangType'];
    var toString = [];
    for (var i = 0; i < arrId.length; i++) {
        toString.push($("#" + arrId[i]).siblings().eq(0).html())
    }
    $.ajax({
        type: 'post',
        url: 'getReadyInfo/',
        data: {
            className: row.className,
            subClassName: row.subClassName,
            productType: row.productType,
            field: toString.join(";")
        }, success: function (data) {
            var data = JSON.parse(data);
            data.forEach(function (item) {
                if (item.name == '国别') {
                    $("#UpdateInfo-country").combobox("loadData", item.val);
                }
                if (item.name == '等级') {
                    $("#UpdateInfo-level").combobox("loadData", item.val);
                }
                if (item.name == '年代') {
                    $("#UpdateInfo-peroid").combobox("loadData", item.val);
                }
                if (item.name == '规格') {
                    $("#UpdateInfo-dingSecification").combobox("loadData", item.val);
                }
                if (item.name == '型制') {
                    $("#UpdateInfo-shape").combobox("loadData", item.val);
                }
                if (item.name == '器型') {
                    $("#UpdateInfo-shape").combobox("loadData", item.val);
                }
                if (item.name == '品相') {
                    $("#UpdateInfo-quality").combobox("loadData", item.val);
                }
                if (item.name == '面值') {
                    $("#UpdateInfo-faceAmount").combobox("loadData", item.val);
                }
                if (item.name == '性质') {
                    $("#UpdateInfo-zhangType").combobox("loadData", item.val);
                }
            })
        }
    })
}

function updateInfo(index, row) {
    $.ajax({
        url: 'getThingInfo/',
        type: 'post',
        data: {
            subClassName: row.subClassName,
            serialNumber: row.serialNumber
        }, success: function (data) {
            var data = JSON.parse(data);
            $('#UpdateInfoForm').form('load', {
                serialNumber: row.serialNumber,
                productType: row.productType,
                className: row.className,
                subClassName: row.subClassName,
                wareHouse: row.wareHouse,
                boxNumber: row.boxNumber,
                level: data.level,
                detailedName: data.detailedName,
                peroid: data.peroid,
                year: data.year,
                country: data.country,
                faceAmount: data.faceAmount,
                dingSecification: data.dingSecification,
                zhangType: data.zhangType,
                shape: data.shape,
                appearance: data.appearance,
                originalQuantity: data.originalQuantity,
                remark: data.remark,
                mark: data.mark
            });

        }
    });
    var node = $('#workSpaceTree').tree('getSelected');
    $('#workGrid' + node.id).datagrid('reload');
    initUpdateInfoDlg(row);
    getReadyInfoInformation(row);
    $('#UpdateInfoDlg').dialog('open').dialog('center').dialog('setTitle', '更新信息');
    $('#UpdateInfoForm').form('clear');
    var data;
    if (row.status == 1) {
        // 记录已更新, 待编辑
        $.ajax({
            url: 'getNumberingInfo/',
            data: {serialNumber: row.serialNumber, boxNumber: row.boxNumber, productType: row.productType},
            type: 'Get',
            async: true,
            dataType: 'json',
            success: function (result, status) {
                data = result;
                // if (row.productType == "金银锭类") {
                //     $('#UpdateInfoForm').form('load', {
                //         serialNumber: row.serialNumber,
                //         productType: row.productType,
                //         className: row.className,
                //         subClassName: row.subClassName,
                //         wareHouse: row.wareHouse,
                //         boxNumber: row.boxNumber,
                //         detailedName: data.detailedName,
                //         peroid: data.peroid,
                //         originalQuantity: data.originalQuantity,
                //         producePlace: data.producePlace,
                //         producer: data.producer,
                //         typeName: data.typeName,
                //         carveName: data.carveName,
                //         quality: data.quality,
                //         level: data.level,
                //         remark: data.remark,
                //     });
                // }
                // else if (row.productType == "金银币章类") {
                //     $('#UpdateInfoForm').form('load', {
                //         serialNumber: row.serialNumber,
                //         productType: row.productType,
                //         className: row.className,
                //         subClassName: row.subClassName,
                //         wareHouse: row.wareHouse,
                //         boxNumber: row.boxNumber,
                //         versionName: data.versionName,
                //         detailedName: data.detailedName,
                //         peroid: data.peroid,
                //         originalQuantity: data.originalQuantity,
                //         producePlace: data.producePlace,
                //         producer: data.producer,
                //         quality: data.quality,
                //         level: data.level,
                //         remark: data.remark,
                //     });
                // }
                // else if (row.productType == "银元类") {
                //     $('#UpdateInfoForm').form('load', {
                //         serialNumber: row.serialNumber,
                //         productType: row.productType,
                //         className: row.className,
                //         subClassName: row.subClassName,
                //         wareHouse: row.wareHouse,
                //         boxNumber: row.boxNumber,
                //         versionName: data.versionName,
                //         value: data.value,
                //         producePlace: data.producePlace,
                //         producer: data.producer,
                //         quality: data.quality,
                //         level: data.level,
                //         remark: data.remark,
                //     });
                // }
                // else if (row.productType == "金银工艺品类") {
                //     $('#UpdateInfoForm').form('load', {
                //         serialNumber: row.serialNumber,
                //         productType: row.productType,
                //         className: row.className,
                //         subClassName: row.subClassName,
                //         wareHouse: row.wareHouse,
                //         boxNumber: row.boxNumber,
                //         value: data.value,
                //         detailedName: data.detailedName,
                //         peroid: data.peroid,
                //         originalQuantity: data.originalQuantity,
                //         marginShape: data.marginShape,
                //         quality: data.quality,
                //         level: data.level,
                //         remark: data.remark
                //     });
            }
            // }
        });
    }
    else {
        $('#UpdateInfoForm').form('load', {
            serialNumber: row.serialNumber,
            productType: row.productType,
            className: row.className,
            subClassName: row.subClassName,
            wareHouse: row.wareHouse,
            boxNumber: row.boxNumber
        });
    }
    url = 'updateNumberingInfo/';
}
function editUpdateInfo() {

    $('#editBtn').attr('style', 'width:90px; display:none;');
    $('#saveBtn').attr('style', 'width:90px');
    var productType = $('#UpdateInfo-productType').textbox('getValue');
    // if (productType == '金银币章类') {
    //     $('#UpdateInfo-versionName').textbox('readonly', false);
    //     $('#UpdateInfo-value').textbox('readonly', false);
    //     $('#UpdateInfo-detailedName').textbox('readonly', false);
    //     $('#UpdateInfo-peroid').textbox('readonly', false);
    //     $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    //     $('#UpdateInfo-producePlace').textbox('readonly', false);
    //     $('#UpdateInfo-producer').textbox('readonly', false);
    // }
    // if (productType == '银元类') {
    //     $('#UpdateInfo-versionName').textbox('readonly', false);
    //     $('#UpdateInfo-value').textbox('readonly', false);
    //     $('#UpdateInfo-producePlace').textbox('readonly', false);
    //     $('#UpdateInfo-producer').textbox('readonly', false);
    // }
    //
    // if (productType == '金银工艺品类') {
    //     $('#UpdateInfo-detailedName').textbox('readonly', false);
    //     $('#UpdateInfo-peroid').textbox('readonly', false);
    //     $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    // }
    // if (productType == '金银锭类') {
    //     $('#UpdateInfo-detailedName').textbox('readonly', false);
    //     $('#UpdateInfo-peroid').textbox('readonly', false);
    //     $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    //     $('#UpdateInfo-producePlace').textbox('readonly', false);
    //     $('#UpdateInfo-producer').textbox('readonly', false);
    //     $('#UpdateInfo-typeName').textbox('readonly', false);
    //     $('#UpdateInfo-carveName').textbox('readonly', false);
    // }
    $('#UpdateInfo-remark').textbox('readonly', false);
}


function saveUpdateInfo() {
    var node = $('#workSpaceTree').tree('getSelected');
    var workName = node.text;
    var serialNumber = $("#single_serialNumber").children().find('.textbox-value').val();//实物编号
    var single_level = $("#single_level").children().find('.textbox-value').val(); //等级
    var single_peroid = $("#single_peroid").children().find('.textbox-value').val();//年代
    var single_country = $("#single_country").children().find('.textbox-value').val();//国别
    var single_quality = $("#single_quality").children().find('.textbox-value').val();//品相
    var single_originalQuantity = $("#single_originalQuantity").children().find('.textbox-value').val();//成色
    var single_year = $("#single_year").children().find('.textbox-value').val();//年份
    var single_faceAmount = $("#single_faceAmount").children().find('.textbox-value').val();//面值
    var single_dingSecification = $("#single_dingSecification").children().find('.textbox-value').val();//规格
    var single_zhangType = $("#single_zhangType").children().find('.textbox-value').val();//规格
    var single_shape = $("#single_shape").children().find('.textbox-value').val();//器型
    var single_carveName = $("#physical_carveName").val();//铭文
    var single_remark = $("#single_remark").children().find('.textbox-value').val();//备注
    var single_detailedName = $("#physical_detailedName").val();//名称
    var arrId = ['single_level', 'single_peroid', 'single_country', 'single_quality', 'single_originalQuantity',
        'single_year', 'single_faceAmount', 'single_dingSecification', 'single_zhangType', 'single_shape', 'single_carveName', 'single_remark', 'single_detailedName'];
    var mustId = [];
    var Compulsory = ['single_level', 'single_peroid', 'single_country', 'single_quality', 'single_originalQuantity'];
    for (var i = 0; i < arrId.length; i++) {
        if ($("#" + arrId[i]).css("display") !== "none") {
            Compulsory.forEach(function (item) {
                if (arrId[i] == item && $("#" + item).children().find('.textbox-value').val() == '') {
                    mustId.push(item)
                }
            });
        }
    }
    if (mustId.length > 0) {
        $.messager.alert('提示', "带*号的为必填项");
        return
    }
    $.ajax({
        type: 'post',
        url: 'updateNumberingInfo/',
        data: {
            serialNumber: serialNumber,
            csrfmiddlewaretoken: getCookie('csrftoken'),
            level: single_level,
            detailedName: single_detailedName,
            peroid: single_peroid,
            year: single_year,
            country: single_country,
            faceAmount: single_faceAmount,
            dingSecification: single_dingSecification,
            zhangType: single_zhangType,
            shape: single_shape,
            appearance: single_quality,
            mark: single_remark,
            originalQuantity: single_originalQuantity,
            remark: single_remark,
            operator: $('#operator').val(), //操作员
            workName: workName, //作业名
        }, success: function (data) {
            var data = JSON.parse(data);
            if (data.success) {
                $.messager.confirm('提示', data.message, function (r) {
                    if (r) {
                        $("#UpdateInfoDlg").dialog('close');
                    }
                });
                var node = $('#workSpaceTree').tree('getSelected');
                $('#workGrid' + node.id).datagrid('reload');

            } else {
                $.messager.alert('提示', data.message);
            }

        }
    });

    // $('#UpdateInfoForm').form({
    //     url: url,
    //     queryParams: {
    //         csrfmiddlewaretoken: getCookie('csrftoken'),
    //         operator: $('#operator').val(),
    //     },
    //     onSubmit: function (param) {
    //         return $(this).form('validate');
    //     },
    //     success: function (result) {
    //         var result = eval('(' + result + ')');
    //         if (!result.success) {
    //             $.messager.alert({		// 显示失败信息
    //                 title: '提示',
    //                 msg: result.message
    //             });
    //         } else {
    //             $('#workGrid1').datagrid('reload');
    //             $('#UpdateInfoDlg').dialog('close');        	 // 关闭对话框
    //             $.messager.show({		// 显示成功信息
    //                 title: '提示',
    //                 msg: result.message,
    //                 timeout: 5000,
    //                 showType: 'slide'
    //             });
    //             var node = $('#workSpaceTree').tree('getSelected');
    //             $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
    //         }
    //     }
    // });
    // $('#UpdateInfoForm').submit();
}