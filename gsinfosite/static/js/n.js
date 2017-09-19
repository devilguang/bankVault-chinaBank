﻿//写cookies
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
    $.ajax({
        type: 'post',
        url: 'checkInfo/',
        data: {
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
function initBatchUpdateInfoDlg(row) {
    if (row.productType == '金银币章类') {
        $('#batch-typeName').attr({'style': 'display:none'});
        $('#batch-carveName').attr({'style': 'display:none'});
        $('#batch-marginShape').attr({'style': 'display:none'});
    }
    if (row.productType == '银元类') {
        $('#batch-detailedName').attr({'style': 'display:none'});
        $('#batch-typeName').attr({'style': 'display:none'});
        $('#batch-peroid').attr({'style': 'display:none'});
        $('#batch-carveName').attr({'style': 'display:none'});
        $('#batch-originalQuantity').attr({'style': 'display:none'});
        $('#batch-marginShape').attr({'style': 'display:none'});
    }

    if (row.productType == '金银工艺品类') {
        $('#batch-typeName').attr({'style': 'display:none'});
        $('#batch-producePlace').attr({'style': 'display:none'});
        $('#batch-producer').attr({'style': 'display:none'});
        $('#batch-carveName').attr({'style': 'display:none'});
        $('#batch-versionName').attr({'style': 'display:none'});
        $('#batch-value').attr({'style': 'display:none'});
        $('#batch-marginShape').attr({'style': 'display:none'});
    }

    if (row.productType == '金银锭类') {
        $('#batch-versionName').attr({'style': 'display:none'});
        $('#batch-value').attr({'style': 'display:none'});
        $('#batch-marginShape').attr({'style': 'display:none'});
    }
}
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
    initBatchUpdateInfoDlg(row);
    //$.messager.alert('提示', boxNumber);
    $('#BatchUpdateInfoDlg').dialog('open').dialog('center').dialog('setTitle', '批量更新信息');
    $('#BatchUpdateInfoForm').form('clear');
    $('#BatchUpdateInfoForm').form('load', {
        productType: row.productType,
        className: row.className,
        subClassName: row.subClassName,
        wareHouse: row.wareHouse,
        boxNumber: row.boxNumber,
    });
    url = 'updateNumberingInfo/';
}
function saveBatchUpdateInfo() {
    var tab = $('#tbs').tabs('getSelected');
    var id = tab[0].id;
    var node = $('#workSpaceTree').tree('find', id);
    var workSeq = node.attributes.workSeq;
    $('#BatchUpdateInfoForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            operator: $('#operator').val(),
            workSeq: workSeq,
        },
        onSubmit: function (param) {
            return $(this).form('validate');
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({		// 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            } else {
                $('#BatchUpdateInfoDlg').dialog('close');        // 关闭对话框
                $.messager.show({		// 显示成功信息
                    title: '提示',
                    msg: result.message,
                    timeout: 5000,
                    showType: 'slide'
                });
                $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
            }
        }
    });
    $('#BatchUpdateInfoForm').submit();
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
            $("#shape").css("display", "block");
            $("#dingSecification").css("display", "block");
            $("#shape1").css("display", "block");
            $("#zhangType").css("display", "block");
        }
    });
    dianArr.forEach(function (item) {
        if (subClassName == item) {
            $("#shape1").css("display", "block"); //型制
            $("#dingSecification").css("display", "block");//规格
        }
    });
    gong.forEach(function (item) {
        if (subClassName == item) {
            $("#shape").css("display", "block"); //器型
        }
    });
    zhang.forEach(function (item) {
        if (subClassName == item) {
            $("#zhangType").css("display", "block"); //器型
        }
    });
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
    $('#versionName').attr({'style': ''});
    $('#value').attr({'style': ''});
    $('#detailedName').attr({'style': ''});
    $('#peroid').attr({'style': ''});
    $('#originalQuantity').attr({'style': ''});
    $('#producePlace').attr({'style': ''});
    $('#marginShape').attr({'style': ''});
    $('#typeName').attr({'style': ''});
    $('#carveName').attr({'style': ''});
    $('#UpdateInfo-versionName').textbox('readonly', false);
    $('#UpdateInfo-value').textbox('readonly', false);
    $('#UpdateInfo-detailedName').textbox('readonly', false);
    $('#UpdateInfo-peroid').textbox('readonly', false);
    $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    $('#UpdateInfo-producePlace').textbox('readonly', false);
    $('#UpdateInfo-producer').textbox('readonly', false);
    $('#UpdateInfo-marginShape').textbox('readonly', false);
    $('#UpdateInfo-typeName').textbox('readonly', false);
    $('#UpdateInfo-carveName').textbox('readonly', false);
    $('#UpdateInfo-remark').textbox('readonly', false);
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
function updateInfo(index, row) {
    initUpdateInfoDlg(row);
    //$.messager.alert('提示', boxNumber);
    $.ajax({
        url: 'getThingInfo/',
        type: 'post',
        data: {
            subClassName: row.subClassName,
            serialNumber: row.serialNumber
        }, success: function (data) {
            var data = JSON.parse(data);
            if (row.subClassName == "金银锭类") {
                $('#UpdateInfoForm').form('load', {
                    serialNumber: row.serialNumber,
                    productType: row.productType,
                    className: row.className,
                    subClassName: row.subClassName,
                    wareHouse: row.wareHouse,
                    boxNumber: row.boxNumber,
                    detailedName: data.detailedName,
                    peroid: data.peroid,
                    originalQuantity: data.originalQuantity,
                    producePlace: data.producePlace,
                    producer: data.producer,
                    typeName: data.typeName,
                    carveName: data.carveName,
                    quality: data.quality,
                    level: data.level,
                    remark: data.remark,
                });
            }
            else if (row.productType == "金银币章类") {
                $('#UpdateInfoForm').form('load', {
                    serialNumber: row.serialNumber,
                    productType: row.productType,
                    className: row.className,
                    subClassName: row.subClassName,
                    wareHouse: row.wareHouse,
                    boxNumber: row.boxNumber,
                    versionName: data.versionName,
                    detailedName: data.detailedName,
                    peroid: data.peroid,
                    originalQuantity: data.originalQuantity,
                    producePlace: data.producePlace,
                    producer: data.producer,
                    quality: data.quality,
                    level: data.level,
                    remark: data.remark,
                });
            }
            else if (row.productType == "银元类") {
                $('#UpdateInfoForm').form('load', {
                    serialNumber: row.serialNumber,
                    productType: row.productType,
                    className: row.className,
                    subClassName: row.subClassName,
                    wareHouse: row.wareHouse,
                    boxNumber: row.boxNumber,
                    versionName: data.versionName,
                    value: data.value,
                    producePlace: data.producePlace,
                    producer: data.producer,
                    quality: data.quality,
                    level: data.level,
                    remark: data.remark,
                });
            }
            else if (row.productType == "金银工艺品类") {
                $('#UpdateInfoForm').form('load', {
                    serialNumber: row.serialNumber,
                    productType: row.productType,
                    className: row.className,
                    subClassName: row.subClassName,
                    wareHouse: row.wareHouse,
                    boxNumber: row.boxNumber,
                    value: data.value,
                    detailedName: data.detailedName,
                    peroid: data.peroid,
                    originalQuantity: data.originalQuantity,
                    marginShape: data.marginShape,
                    quality: data.quality,
                    level: data.level,
                    remark: data.remark,
                });
            }
        }
    })

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

                if (row.productType == "金银锭类") {
                    $('#UpdateInfoForm').form('load', {
                        serialNumber: row.serialNumber,
                        productType: row.productType,
                        className: row.className,
                        subClassName: row.subClassName,
                        wareHouse: row.wareHouse,
                        boxNumber: row.boxNumber,
                        detailedName: data.detailedName,
                        peroid: data.peroid,
                        originalQuantity: data.originalQuantity,
                        producePlace: data.producePlace,
                        producer: data.producer,
                        typeName: data.typeName,
                        carveName: data.carveName,
                        quality: data.quality,
                        level: data.level,
                        remark: data.remark,
                    });
                }
                else if (row.productType == "金银币章类") {
                    $('#UpdateInfoForm').form('load', {
                        serialNumber: row.serialNumber,
                        productType: row.productType,
                        className: row.className,
                        subClassName: row.subClassName,
                        wareHouse: row.wareHouse,
                        boxNumber: row.boxNumber,
                        versionName: data.versionName,
                        detailedName: data.detailedName,
                        peroid: data.peroid,
                        originalQuantity: data.originalQuantity,
                        producePlace: data.producePlace,
                        producer: data.producer,
                        quality: data.quality,
                        level: data.level,
                        remark: data.remark,
                    });
                }
                else if (row.productType == "银元类") {
                    $('#UpdateInfoForm').form('load', {
                        serialNumber: row.serialNumber,
                        productType: row.productType,
                        className: row.className,
                        subClassName: row.subClassName,
                        wareHouse: row.wareHouse,
                        boxNumber: row.boxNumber,
                        versionName: data.versionName,
                        value: data.value,
                        producePlace: data.producePlace,
                        producer: data.producer,
                        quality: data.quality,
                        level: data.level,
                        remark: data.remark,
                    });
                }
                else if (row.productType == "金银工艺品类") {
                    $('#UpdateInfoForm').form('load', {
                        serialNumber: row.serialNumber,
                        productType: row.productType,
                        className: row.className,
                        subClassName: row.subClassName,
                        wareHouse: row.wareHouse,
                        boxNumber: row.boxNumber,
                        value: data.value,
                        detailedName: data.detailedName,
                        peroid: data.peroid,
                        originalQuantity: data.originalQuantity,
                        marginShape: data.marginShape,
                        quality: data.quality,
                        level: data.level,
                        remark: data.remark,
                    });
                }

            },
        });
    }
    else {
        $('#UpdateInfoForm').form('load', {
            serialNumber: row.serialNumber,
            productType: row.productType,
            className: row.className,
            subClassName: row.subClassName,
            wareHouse: row.wareHouse,
            boxNumber: row.boxNumber,
        });
    }
    url = 'updateNumberingInfo/';
}
function editUpdateInfo() {
    $('#editBtn').attr('style', 'width:90px; display:none;');
    $('#saveBtn').attr('style', 'width:90px');
    var productType = $('#UpdateInfo-productType').textbox('getValue');
    if (productType == '金银币章类') {
        $('#UpdateInfo-versionName').textbox('readonly', false);
        $('#UpdateInfo-value').textbox('readonly', false);
        $('#UpdateInfo-detailedName').textbox('readonly', false);
        $('#UpdateInfo-peroid').textbox('readonly', false);
        $('#UpdateInfo-originalQuantity').textbox('readonly', false);
        $('#UpdateInfo-producePlace').textbox('readonly', false);
        $('#UpdateInfo-producer').textbox('readonly', false);
    }
    if (productType == '银元类') {
        $('#UpdateInfo-versionName').textbox('readonly', false);
        $('#UpdateInfo-value').textbox('readonly', false);
        $('#UpdateInfo-producePlace').textbox('readonly', false);
        $('#UpdateInfo-producer').textbox('readonly', false);
    }

    if (productType == '金银工艺品类') {
        $('#UpdateInfo-detailedName').textbox('readonly', false);
        $('#UpdateInfo-peroid').textbox('readonly', false);
        $('#UpdateInfo-originalQuantity').textbox('readonly', false);
    }
    if (productType == '金银锭类') {
        $('#UpdateInfo-detailedName').textbox('readonly', false);
        $('#UpdateInfo-peroid').textbox('readonly', false);
        $('#UpdateInfo-originalQuantity').textbox('readonly', false);
        $('#UpdateInfo-producePlace').textbox('readonly', false);
        $('#UpdateInfo-producer').textbox('readonly', false);
        $('#UpdateInfo-typeName').textbox('readonly', false);
        $('#UpdateInfo-carveName').textbox('readonly', false);
    }
    $('#UpdateInfo-remark').textbox('readonly', false);
}
function saveUpdateInfo() {
    var colorForming = $('#originalQuantity').children().find('.textbox-value').val();
    if (colorForming == '') {
        $.messager.alert("提示", "带*号的为必填项");
        return;
    }
    $('#UpdateInfoForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            operator: $('#operator').val(),
        },
        onSubmit: function (param) {
            return $(this).form('validate');
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({		// 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            } else {
                $('#workGrid1').datagrid('reload');
                $('#UpdateInfoDlg').dialog('close');        	 // 关闭对话框
                $.messager.show({		// 显示成功信息
                    title: '提示',
                    msg: result.message,
                    timeout: 5000,
                    showType: 'slide'
                });
                var node = $('#workSpaceTree').tree('getSelected');
                $('#workGrid' + node.id).datagrid('reload');         	 // 重载作业数据
            }
        }
    });
    $('#UpdateInfoForm').submit();
}