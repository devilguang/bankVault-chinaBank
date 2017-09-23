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
    var subBoxNumber = node.attributes.subBoxNumber;
    var c = '<table id="workGrid' + id + '" class="easyui-datagrid" data-options="url:\'getWorkData/' + workSeq + '\', queryParams:{processId: $(\'#processId\').val(),  boxNumber: \'' + boxNumber + '\', subBoxNumber: \'' + subBoxNumber + '\', thingStatus: \'notComplete\'}, toolbar:\'#workGridToolBar' + id + '\', singleSelect:true, fitColumns:true, loaded:false, rownumbers:true, loadMsg:\'' + title + '作业数据正在载入，请稍后...\', onDblClickRow:dbClickRow, pagination:true, fit:true, pageSize:20"><thead><tr><th field="boxNumber">箱号</th><th field="serialNumber" align="center">实物编号</th><th field="productType" align="center">实物类型</th><th field="className" align="center">品名</th><th field="subClassName" align="center">明细品名</th><th field="wareHouse" align="center">发行库</th><th field="status" formatter="statusFormatter" align="center">是否已更新</th><th field="operator" formatter="operatorFormatter" align="center">操作员</th><th field="lastUpdateTime" formatter="lastUpdateTimeFormatter" align="center">最新一次更新时间</th></tr></thead></table><div id="workGridToolBar' + id + '"><label for="workGrid' + id + 'StatusCombobox" style="margin-left:5px;margin-right:5px;">状态</label><input id="workGrid' + id + 'StatusCombobox" style="margin-right:20px;padding-top:5px;" /><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid' + id + '\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript"> function dbClickRow(index, row){ /*$.messager.alert(\'提示\', \'select\'+index);*/ updateInfo(index, row); } function initPagination(){$(\'#workGrid' + id + '\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});} function initToolbar(){ $(\'#workGrid' + id + 'StatusCombobox\').combobox({valueField: \'id\', textField: \'text\', editable: false, data: [{id: \'notComplete\', text: \'未完成\'}, {id: \'all\', text: \'全部\'}, {id: \'complete\', text: \'已完成\'}, ], panelHeight: \'auto\', \'onSelect\':function(record){ $(\'#workGrid' + id + '\').datagrid(\'options\').queryParams[\'thingStatus\'] = record.id; $(\'#workGrid' + id + '\').datagrid(\'reload\'); },}).combobox(\'setValue\', \'notComplete\'); }</script>';
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
function initUpdateInfoDlg(row) {
    if (row.productType == '银元类' || row.productType == '金银币章类') {
        $('#thing2').attr({'style': 'display:none'});
    }
    else {
        $('#thing1').attr({'style': 'display:none'});
    }

    if (row.status == 1) {
        // 记录已更新, 待编辑
        $('#editBtn').attr({'style': 'width:90px'});
        $('#saveBtn').attr({'style': 'width:90px;display:none'});

        // 根据实物类型, 处理确认输入框的显示情况
        $('#UpdateInfogrossWeight').textbox('readonly', true);
        if (row.productType == '银元类' || row.productType == '金银币章类') {
            $('#UpdateInfodiameter').textbox('readonly', true);
            $('#UpdateInfothick').textbox('readonly', true);
        }
        else {
            $('#UpdateInfolength').textbox('readonly', true);
            $('#UpdateInfowidth').textbox('readonly', true);
            $('#UpdateInfoheight').textbox('readonly', true);
        }
    }
    else {
        // 记录未更新
        $('#editBtn').attr({'style': 'width:90px;display:none'});
        $('#saveBtn').attr({'style': 'width:90px'});
    }
}
function unInitUpdateInfoDlg() {
    $('#thing2').attr({'style': ''});
    $('#thing1').attr({'style': ''});

    $('#UpdateInfogrossWeight').textbox('readonly', false);

    $('#UpdateInfodiameter').textbox('readonly', false);
    $('#UpdateInfothick').textbox('readonly', false);

    $('#UpdateInfolength').textbox('readonly', false);
    $('#UpdateInfowidth').textbox('readonly', false);
    $('#UpdateInfoheight').textbox('readonly', false);
}
function closeUpdateInfo() {
    $('#UpdateInfoDlg').dialog('close');
    unInitUpdateInfoDlg();
}

// 判断哪些东西是必填的
function isLinSan(row) {
    var grossWeight = $('#UpdateInfogrossWeight').textbox('getValue');
    var length = $('#UpdateInfolength').textbox('getValue');
    var width = $('#UpdateInfowidth').textbox('getValue');
    var height = $('#UpdateInfoheight').textbox('getValue');
    var arr = ['Update_infogrossWeight', 'Update_infolength', 'Update_infowidth', 'Update_infoheight'];
    $.ajax({
        type: 'post',
        url: 'isLinSan/',
        data: {
            boxNumber: row.boxNumber
        }, success: function (data) {
            var data = JSON.parse(data);
            if (data.success) {
                $("#Update_infogrossWeight").children().eq(3).css('display', 'inline-block');
                $("#Update_infolength").children().eq(3).css('display', 'none');
                $("#Update_infowidth").children().eq(3).css('display', 'none');
                $("#Update_infoheight").children().eq(3).css('display', 'none');
            } else {
                $("#Update_infogrossWeight").children().eq(3).css('display', 'inline-block');
                $("#Update_infolength").children().eq(3).css('display', 'inline-block');
                $("#Update_infowidth").children().eq(3).css('display', 'inline-block');
                $("#Update_infoheight").children().eq(3).css('display', 'inline-block');

            }
        }
    })
}

function updateInfo(index, row) {
    initUpdateInfoDlg(row);
    $('#UpdateInfoDlg').dialog('open').dialog('center').dialog('setTitle', '更新信息');
    $('#UpdateInfoForm').form('clear');
    isLinSan(row);
    if (row.status == 1) {
        // 记录已更新, 待编辑
        $.ajax({
            url: 'getMeasuringInfo/',
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
                        grossWeight: data.grossWeight,
                        length: data.length,
                        width: data.width,
                        height: data.height,
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
                        grossWeight: data.grossWeight,
                        diameter: data.diameter,
                        thick: data.thick,
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
                        grossWeight: data.grossWeight,
                        diameter: data.diameter,
                        thick: data.thick,
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
                        grossWeight: data.grossWeight,
                        length: data.length,
                        width: data.width,
                        height: data.height,
                    });
                }
            },
        });
    }
    else {
        $('#UpdateInfoForm').form('load', {
            productType: row.productType,
            className: row.className,
            subClassName: row.subClassName,
            wareHouse: row.wareHouse,
            boxNumber: row.boxNumber,
            serialNumber: row.serialNumber
        });
    }
    url = 'updateMeasuringInfo/';
}
function editInfo() {
    // isLinSan
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
function saveInfo() {
    var arrId = ['Update_infogrossWeight', 'Update_infolength', 'Update_infowidth', 'Update_infoheight'];
    var showId = [];
    arrId.forEach(function (item) {
        if ($("#" + item).children().eq(3).css('display') !== 'none' && $("#" + item).children().eq(2).children().eq(1).val() == '') {
            showId.push(item)
        }
    });
    if (showId.length > 0) {
        $.messager.alert({
            title: '提示',
            msg: '带*号的不能为空！'
        });
        return false;
    }
    $('#UpdateInfoForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            operator: $('#operator').val()
        },
        onSubmit: function (param) {
            var productType = $('#UpdateInfoproductType').textbox('getValue');
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({		// 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            } else {
                $('#UpdateInfoDlg').dialog('close');        // 关闭对话框
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