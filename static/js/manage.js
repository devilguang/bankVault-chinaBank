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

function addTab(title, content, icon) {
    if ($('#tbs').tabs('exists', title)) {
        $('#tbs').tabs('select', title);
    } else {
        $('#tbs').tabs('add', {
            title: title,
            content: content,
            closable: true,
            iconCls: icon,
            border: false
        });
    }
}

function boxManage() {
    var title = '实物管理';
    var c = '<div class="easyui-layout" data-options="fit: true">' +
        '<div data-options="region:\'north\'" height="10%">' +
        '<form id="boxSearchParameter" style="display:inline-block;margin-top:12px;">' +
        '<div style="display:inline;margin-left:10px;margin-right:15px;">' +
        '<label for="boxSearchParameter-productType" style="margin-right:5px">实物类型</label>' +
        '<input id="boxSearchParameter-productType" class="easyui-combobox" name="productType" data-options="valueField: \'id\', textField: \'text\', url: \'getProductType/\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var url = \'getClassName/\'+rec.id; $(\'#boxSearchParameter-className\').combobox(\'reload\', url); $(\'#boxSearchParameter-className\').combobox(\'clear\'); $(\'#boxSearchParameter-subClassName\').combobox(\'clear\');},"/></div><div style="display:inline;margin-right:15px;"><label for="boxSearchParameter-className" style="margin-right:5px;">品名</label>' +
        '<input id="boxSearchParameter-className" class="easyui-combobox" name="className" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var typeCode = $(\'#boxSearchParameter-productType\').combobox(\'getValue\'); var url = \'getSubClassName/\'+typeCode+\'&\'+rec.id; $(\'#boxSearchParameter-subClassName\').combobox(\'reload\', url);},"/></div>' +
        '<div style="display:inline;margin-right:15px;">' +
        '<label for="boxSearchParameter-subClassName" style="margin-right:5px;">明细品名</label>' +
        '<input id="boxSearchParameter-subClassName" class="easyui-combobox" name="subClassName" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\',"/></div>' +
        '</form><a href="javascript:void(0)" class="easyui-linkbutton" onclick="boxSearch()" style="width:60px;margin-right:10px;">查询</a>' +
        '<a href="javascript:void(0)" class="easyui-linkbutton" onclick="boxSearchReset()" style="width:60px;margin-right:10px;">重置</a>' +
        '</div>' +
        '<div data-options="region:\'center\'">' +
        '<table id="workGridBoxManage" class="easyui-datagrid" data-options="url:\'getBox/\', queryParams: {status: 0}, toolbar:\'#workGridToolBarBoxManage\', onClickRow:ClickRow, singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20"><thead><tr><th field="boxNumber" align="center" width="7%">箱号</th>' +
        '<th field="productType" align="center">实物类型</th>' +
        '<th field="className" align="center">品名</th><th field="subClassName" align="center">明细品名</th><th field="wareHouse" align="center" >发行库</th><th field="amount" align="center" >件数</th><th field="operation" formatter="boxOperationFormatter" align="center" width="65%">操作</th></tr></thead></table></div></div><div id="workGridToolBarBoxManage"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGridBoxManage\').datagrid(\'reload\')">刷新</a><a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="openCreateBoxDlg()">新建</a><a href="#" class="easyui-linkbutton" iconCls="icon-allot" plain="true" onclick="openAllotBoxDlg()">拆箱</a><a href="#" class="easyui-linkbutton" iconCls="icon-merge" plain="true" onclick="openMergeBoxDlg()">并箱</a><a href="#" class="easyui-linkbutton" iconCls="icon-large_chart" plain="true" onclick="openReportBoxDlg()">报表</a><a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="deleteBox()">删除</a></div><script type="text/javascript">function initPagination(){$(\'#workGridBoxManage\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-box2');
    initPagination();
}
function boxOperationFormatter(value, row, index) {
    if (row.haveSubBox == "0") {
        return '<div style="float:left"><a href="javascript:void(0);" onclick="openAddToExistingBoxDlg(\'' + index + '\', 0)" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">并箱操作</a><a href="javascript:void(0);" onclick="openCreateWorkDlg(\'' + row.boxNumber + '\')" style="text-decoration:none;color:blue;margin-right:20px;">创建作业</a><a href="javascript:void(0);" onclick="generateBoxInfo(\'' + index + '\', 0)" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单</a><a href="javascript:void(0);" onclick="generateBoxInfoDetailedVersion(\'' + index + '\', 0)" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单(详细版)</a><a href="javascript:void(0);" onclick="putBoxIntoStore(0, \'' + index + '\', 1)" style="text-decoration:none;color:blue;margin-right:20px;">封箱入库</a><a href="javascript:void(0);" onclick="exploreBox(\'' + row.boxNumber + '\')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a><a href="javascript:void(0);" onclick="weightBox(\'' + row.boxNumber + '\')" style="text-decoration:none;color:blue;">修改</a></div>'
    } else {
        //return '<div style="float:left; min-width: 498px;"></div>'
        return '<div style="float:left" min-width: 498px;"><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;"></a></div>';
    }
}

//点击新建的方法
function openCreateBoxDlg() {
    $('#createBoxDlg').dialog('open').dialog('center').dialog('setTitle', '新建实物');
    $('#createBoxForm').form('clear');
    $('#createBox-boxNumber').siblings().find('.textbox-text').focus(function () {
        var productType = $("#createBox-productType").siblings().find('.textbox-value').val()
        var wareHouse = $("#createBox-wareHosue").siblings().find('.textbox-value').val()
        var className = $("#createBox-className").siblings().find('.textbox-value').val()
        var subClassName = $("#createBox-subClassName").siblings().find('.textbox-value').val()
        $.ajax({
            type: 'get',
            url: 'getStartSequence/',
            data: {
                codes: productType + '&' + wareHouse + '&' + className + '&' + subClassName
            }, success: function (data) {
                var data = JSON.parse(data)
                $('#createBox-startSeq').siblings().find('.textbox-text').val(data.maxSeq)
            }
        })
    })
}
function createBox() {
    $('#createBoxDlg').dialog('close');        		// 关闭对话框

    $('#createBoxForm').form({
        url: 'createBox/',
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        onSubmit: function (param) {
            return $(this).form('validate');
        },
        beforeSend: function (xhr) {
            showMask(400);
        },
        success: function (result) {
            hideMask();
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            }
            else {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#workGridBoxManage').datagrid('reload');		// 重载数据
            }
        }
    });

    $('#createBoxForm').submit();
}

//var totals = 0;
function openAllotBoxDlg() {             // 打开实物拆箱
    var row = $('#workGridBoxManage').datagrid('getSelected');
    if (!row) {
        $.messager.alert('提示', '未选择记录! 请先选择一条实物记录！');
        return;
    }
    /*var boxNumber = $(".datagrid-row-selected td>.datagrid-cell-c1-boxNumber").html();
     var productval = $(".datagrid-row-selected td>.datagrid-cell-c1-productType").html();
     if(typeof(boxNumber) == "undefined" || boxNumber == ""){
     $.messager.alert({
     title: '提示',
     msg: '请选择需要拆箱号！'
     });
     return false;
     }*/
    $('#allotBoxDlg').dialog('open').dialog('center').dialog('setTitle', '实物拆箱');
    $('#allotBoxForm').form('clear');

    $('#allotBox-boxNumber').val(row.boxNumber);
    $('#info-allotBoxNumber').text(row.boxNumber);

    $('#allotBox-thingsGrid').datagrid({
        url: 'allotBox/',
        queryParams: {boxNumber: row.boxNumber, productType: row.productType, fromSubBox: '1'},
        columns: [[
            {field: 'checkStatus', checkbox: true},
            {field: 'serialNumber', title: '编号', align: 'center'},
            /*{field:'productType',title:'实物类型', align:'center'},
             {field:'subClassName',title:'明细品名', align:'center'},
             {field:'wareHouse',title:'发行库', align:'center'},*/
        ]],
        pagination: true,
        fit: true,
        pageSize: 20,
        fitColumns: true,
        rownumbers: true,
        toolbar: '#allotBox-thingsGrid-ToolBar',
        onCheck: function (index, row) {
            var content = $('#allotBox-selectedThing').textbox('getValue');
            var reg = new RegExp(row.serialNumber + ';', 'g');
            if (!reg.test(content)) {
                content = content + row.serialNumber + ';';
                $('#allotBox-selectedThing').textbox('setValue', content);
                var n = Number($('#allotBox-selectedThingCount').text()) + 1;
                $('#allotBox-selectedThingCount').text(n);
            }
        },
        onUncheck: function (index, row) {
            var content = $('#allotBox-selectedThing').textbox('getValue');
            var target = row.serialNumber + ';';
            var reg = new RegExp(target, 'g');
            content = content.replace(reg, '');
            $('#allotBox-selectedThing').textbox('setValue', content);
            var n = Number($('#allotBox-selectedThingCount').text()) - 1;
            $('#allotBox-selectedThingCount').text(n);
        },
        onCheckAll: function (rows) {
            var content = $('#allotBox-selectedThing').textbox('getValue');

            var n = Number($('#allotBox-selectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + rows[r].serialNumber + ';';
                    n = n + 1;
                }
            }
            $('#allotBox-selectedThingCount').text(n);
            $('#allotBox-selectedThing').textbox('setValue', content);
        },
        onUncheckAll: function (rows) {
            var content = $('#allotBox-selectedThing').textbox('getValue');
            var n = Number($('#allotBox-selectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (reg.test(content)) {
                    content = content.replace(reg, '');
                    n = n - 1;
                }
            }
            $('#allotBox-selectedThingCount').text(n);
            $('#allotBox-selectedThing').textbox('setValue', content);
        },
        /*onLoadSuccess: function(data) {
         totals = data.total;
         },*/
    }).datagrid('getPager').pagination({
        layout: ['prev', 'sep', 'links', 'sep', 'next'],
        displayMsg: '当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录'
    });

    $.post("allotBox/", {
        boxNumber: row.boxNumber,
        productType: row.productType,
        fromSubBox: '1',
        rows: '20',
        page: '1'
    }, function (data) {
        var subBoxList = data.subBoxList;
        if ($.inArray(1, subBoxList) == -1)
            subBoxList.push(1);
        subBoxList.sort();
        var datalist = [];
        for (var i = 0; i < subBoxList.length; i++) {
            var map = {};
            map["id"] = subBoxList[i]; //boxNumber
            /*if(subBoxList[i]==1){
             map["text"]=row.boxNumber+"-1号箱";
             }else{
             map["text"]=row.boxNumber+"-"+subBoxList[i]+"号子箱";
             }*/
            map["text"] = row.boxNumber + "-" + subBoxList[i] + "号子箱";
            datalist.push(map);
        }
        $('#allotBox-thingsGrid-ToolBar-thingIsAllocated').combobox({
            valueField: 'id',
            textField: 'text',
            editable: false,
            data: datalist,
            panelHeight: 'auto',
            'onSelect': function (record) {
                $('#allotBox-thingsGrid').datagrid('options').queryParams['fromSubBox'] = record.id;
                $('#allotBox-thingsGrid').datagrid('reload');
            },
        }).combobox('select', '1');
        $('#allotBox1-thingsGrid-ToolBar-thingIsAllocated').combobox({
            valueField: 'id',
            textField: 'text',
            editable: false,
            data: datalist,
            panelHeight: 'auto',
            'onSelect': function (record) {
                $('#allotBox-thingsGrid').datagrid('options').queryParams['fromSubBox'] = record.id;
            },
        }).combobox('select', '1');
    }, 'json');

    $('#allotBox-selectedThing').textbox({
        fit: true,
        multiline: true,
        editable: false,
    });
    $('#allotBox-selectedThingCount').text(0);
}
function allotBox() {
    var boxNumber = $('#allotBox-boxNumber').val();
    //var grossWeight = $("#grossWeight").val();
    var selectedThings = $('#allotBox-selectedThing').textbox('getValue');
    var fromSubBox = $("#allotBox-thingsGrid-ToolBar .textbox-value").eq(0).val();
    var toSubBox = $("#allotBox-thingsGrid-ToolBar .textbox-value").eq(1).val();

    //var selcount = $("#allotBox-selectedThingCount").text();
    //var operator = $('#operator').val();
    //var fromSubBox = $("#allotBox-thingsGrid-ToolBar .textbox-value").val();
    if (selectedThings == '') {
        $.messager.alert({
            title: '提示',
            msg: '选中实物不能为空！'
        });
        return;
    }
    /*if(fromSubBox==1 && selcount==totals){
     $.messager.alert({
     title: '提示',
     msg: '该箱号不能为空！'
     });
     return ;
     }*/
    $('#allotBoxDlg').dialog('close'); //关闭对话框

    $.ajax({
        url: 'confirmAllotBox/',
        data: {boxNumber: boxNumber, selectedThings: selectedThings, fromSubBox: fromSubBox, toSubBox: toSubBox},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            showMask(400);
        },
        success: function (result) {
            hideMask();
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
            $('#workGridBoxManage').datagrid('reload');
        },
    });
}

function openMergeBoxDlg() {             // 打开实物子箱并箱
    var row = $('#workGridBoxManage').datagrid('getSelected');
    if (!row) {
        $.messager.alert('提示', '未选择记录! 请先选择一条实物记录！');
        return;
    }
    /*var boxNumber = $(".datagrid-row-selected td>.datagrid-cell-c1-boxNumber").html();
     var productval = $(".datagrid-row-selected td>.datagrid-cell-c1-productType").html();
     if(typeof(boxNumber) == "undefined" || boxNumber == ""){
     $.messager.alert({
     title: '提示',
     msg: '请选择需要并箱号！'
     });
     return false;
     }*/
    $('#mergeBoxDlg').dialog('open').dialog('center').dialog('setTitle', '实物并箱');
    $('#mergeBoxForm').form('clear');
    $('#mergeBox-boxNumber').val(row.boxNumber);
    $('#info-mergeBoxNumber').text(row.boxNumber);

    $.post("mergeBox/", {boxNumber: row.boxNumber}, function (data) {
        var subBoxList = data.subBoxList;
        //subBoxList = subBoxList.splice(1);
        var datalist = [];
        for (var i = 0; i < subBoxList.length; i++) {
            var map = {};
            map["serialNumber"] = subBoxList[i]; //boxNumber
            /*if(subBoxList[i]==0){
             map["subNumber"]=row.boxNumber+"-1号箱";
             }else{
             map["subNumber"]=row.boxNumber+"-"+subBoxList[i]+"号子箱";
             }*/
            map["subNumber"] = row.boxNumber + "-" + subBoxList[i] + "号子箱";
            datalist.push(map);
        }
        $('#mergeBox-thingsGrid').datagrid({
            //editable: false,
            //panelHeight: 'auto',
            data: datalist,
            columns: [[
                {field: 'ck', checkbox: true},
                /*{field:'serialNumber',title:'编号', align:'center'},*/
                {field: 'subNumber', title: '子箱号', align: 'center'},
            ]],
            rownumbers: true,
            fitColumns: true,
            //singleSelect: false,
            //selectOnCheck: true,
            //checkOnSelect: true,
            onCheck: function (index, row) {
                var content = $('#mergeBox-selectedThing').textbox('getValue');
                var reg = new RegExp(row.serialNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + row.serialNumber + ';';
                    $('#mergeBox-selectedThing').textbox('setValue', content);
                }
            },
            onUncheck: function (index, row) {
                var content = $('#mergeBox-selectedThing').textbox('getValue');
                var reg = new RegExp(row.serialNumber + ';', 'g');
                content = content.replace(reg, '');
                $('#mergeBox-selectedThing').textbox('setValue', content);
            },
            onCheckAll: function (rows) {
                var content = $('#mergeBox-selectedThing').textbox('getValue');
                for (var r in rows) {
                    var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                    if (!reg.test(content)) {
                        content = content + rows[r].serialNumber + ';';
                    }
                }
                $('#mergeBox-selectedThing').textbox('setValue', content);
            },
            onUncheckAll: function (rows) {
                var content = $('#mergeBox-selectedThing').textbox('getValue');
                for (var r in rows) {
                    var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                    if (reg.test(content)) {
                        content = content.replace(reg, '');
                    }
                }
                $('#mergeBox-selectedThing').textbox('setValue', content);
            },
        });
    }, 'json');

    $('#mergeBox-selectedThing').textbox({
        fit: true,
        multiline: true,
        editable: false,
    });
}
function mergeBox() {
    var boxNumber = $('#mergeBox-boxNumber').val();
    var selectedThings = $('#mergeBox-selectedThing').textbox('getValue');
    var subBox = selectedThings.split(";");
    if (selectedThings == '' || subBox.length < 3) {
        $.messager.alert({
            title: '提示',
            msg: '选中实物不能少于2个！'
        });
        return;
    }
    $('#mergeBoxDlg').dialog('close'); //关闭对话框

    $.ajax({
        url: 'confirmMergeBox/',
        data: {boxNumber: boxNumber, originSubBox: selectedThings},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            showMask(400);
        },
        success: function (result) {
            hideMask();
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
            $('#workGridBoxManage').datagrid('reload');
        },
    });
}
function openReportBoxDlg() {             // 打开实物箱体列表
    $('#reportBoxDlg').dialog('open').dialog('center').dialog('setTitle', '实物箱体列表');
    $('#reportBoxForm').form('clear');

    $('#reportBox-thingsGrid').datagrid({
        url: 'getAllBox/',
        queryParams: {},
        columns: [[
            {field: 'checkStatus', checkbox: true},
            {field: 'boxNumber', title: '箱号', align: 'center'},
            {field: 'productType', title: '实物类型', align: 'center'},
            {field: 'subClassName', title: '明细品名', align: 'center'},
            {field: 'wareHouse', title: '发行库', align: 'center'},
        ]],
        fitColumns: true,
        rownumbers: true,
        onCheck: function (index, row) {
            var content = $('#reportBox-selectedThing').textbox('getValue');
            var reg = new RegExp(row.boxNumber + ';', 'g');
            if (!reg.test(content)) {
                content = content + row.boxNumber + ';';
                $('#reportBox-selectedThing').textbox('setValue', content);
            }
        },
        onUncheck: function (index, row) {
            var content = $('#reportBox-selectedThing').textbox('getValue');
            var reg = new RegExp(row.boxNumber + ';', 'g');
            content = content.replace(reg, '');
            $('#reportBox-selectedThing').textbox('setValue', content);
        },
        onCheckAll: function (rows) {
            var content = $('#reportBox-selectedThing').textbox('getValue');
            for (var r in rows) {
                var reg = new RegExp(rows[r].boxNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + rows[r].boxNumber + ';';
                }
            }
            $('#reportBox-selectedThing').textbox('setValue', content);
        },
        onUncheckAll: function (rows) {
            var content = $('#reportBox-selectedThing').textbox('getValue');
            for (var r in rows) {
                var reg = new RegExp(rows[r].boxNumber + ';', 'g');
                if (reg.test(content)) {
                    content = content.replace(reg, '');
                }
            }
            $('#reportBox-selectedThing').textbox('setValue', content);
        },
    });
    $('#reportBox-selectedThing').textbox({
        fit: true,
        multiline: true,
        editable: false,
    });
}
function reportBox() {
    var row = $('#reportBox-thingsGrid').datagrid('getSelections');
    var map = {};
    for (var i = 0; i < row.length; i++) {
        map[row[i].boxNumber] = row[i].productType;
    }
    map = JSON.stringify(map);

    if (row.length < 1) {
        $.messager.alert({
            title: '提示',
            msg: '选中实物不能少于1个！'
        });
        return;
    }
    $('#reportBoxDlg').dialog('close'); //关闭对话框

    window.open('processInfo?map=' + map);
    /*$.ajax({url: 'processInfo/',
     data: {boxList: map},
     type: 'POST',
     async: true,
     dataType: 'json',
     beforeSend: function (xhr){
     showMask(400);
     },
     success: function(result){
     hideMask();
     if (result.success){
     $.messager.show({    // 显示成功信息
     title: '提示',
     msg: result.message,
     showType: 'slide',
     timeout: 5000
     });
     }
     else{
     $.messager.show({    // 显示失败信息
     title: '提示',
     msg: result.message,
     });
     }
     },
     });*/
}
//点击展现子箱列表
function ClickRow(index, row) {
    var selectids = $('#workGridBoxManage').datagrid('getPanel').find(".datagrid-row-selected");
    $(".ly_hides").remove();
    var clss = $("#" + selectids[1].id + " td div").eq(0).attr('class');
    clss = clss.substring(clss.indexOf('-cell-') + 6, clss.lastIndexOf('-'));
    if (row.haveSubBox == "1") {
        var boxMap = row.subBoxDict;
        var thhtml = "";
        var trhtml = "";
        for (var key in boxMap) {
            thhtml += "<tr class='ly_hides' style='height: 25px;'><td><div class='datagrid-cell-rownumber'></div></td></tr>";
            trhtml += '<tr class="ly_hides" style="height: 25px;"><td field="boxNumber"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-boxNumber">' + row.boxNumber + '-' + key + '</div></td><td field="productType"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-productType">' + row.productType + '</div></td><td field="className"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-className">' + row.className + '</div></td><td field="subClassName"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-subClassName">' + row.subClassName + '</div></td><td field="wareHouse"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-wareHouse">' + row.wareHouse + '</div></td><td field="amount"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-amount">' + boxMap[key] + '</div></td><td field="operation"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-operation"><div style="float:left"><a href="javascript:void(0);" onclick="openAddToExistingBoxDlg(\'' + index + '\', \'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">并箱操作</a><a href="javascript:void(0);" onclick="openCreateWorkDlg(\'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-right:20px;">创建作业</a><a href="javascript:void(0);" onclick="generateBoxInfo(\'' + index + '\', \'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单</a><a href="javascript:void(0);" onclick="generateBoxInfoDetailedVersion(\'' + index + '\', \'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单(详细版)</a><a href="javascript:void(0);" onclick="putBoxIntoStore(1, \'' + row.boxNumber + '-' + key + '\', 1)" style="text-decoration:none;color:blue;margin-right:20px;">封箱入库</a><a href="javascript:void(0);" onclick="exploreBox(\'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a><a href="javascript:void(0);" onclick="weightBox(\'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;">修改</a></div></div></td></tr>';
        }
        $("#" + selectids[0].id).after(thhtml);
        $("#" + selectids[1].id).after(trhtml);
    }
//return '<div style="float:left"><a href="javascript:void(0);" onclick="openAddToExistingBoxDlg(\''+index+'\')" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">并箱操作</a><a href="javascript:void(0);" onclick="openCreateWorkDlg(\''+row.boxNumber+'\')" style="text-decoration:none;color:blue;margin-right:20px;">创建作业</a><a href="javascript:void(0);" onclick="generateBoxInfo(\''+index+'\')" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单</a><a href="javascript:void(0);" onclick="generateBoxInfoDetailedVersion(\''+index+'\')" style="text-decoration:none;color:blue;margin-right:20px;">生成装箱清单(详细版)</a><a href="javascript:void(0);" onclick="putBoxIntoStore(\''+index+'\', 1)" style="text-decoration:none;color:blue;margin-right:20px;">封箱入库</a><a href="javascript:void(0);" onclick="exploreBox(\''+row.boxNumber+'\')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a></div>'
//var row = $('#workGridBoxManage').datagrid('getSelected');
//$("#datagrid-row-r1-2-"+rowIndex).after("<tr class='ly_hides' style='height: 25px;'><td field='boxNumber'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-boxNumber'>1</div></td><td field='productType'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-productType'>金银锭类</div></td><td field='className'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-className'>杂金</div></td><td field='subClassName'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-subClassName'>稀一锭</div></td><td field='wareHouse'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-wareHouse'>湖北重点库</div></td><td field='amount'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-amount'>100</div></td><td field='operation'><div style='text-align:center;height:auto;' class='datagrid-cell datagrid-cell-c1-operation'></div></td></tr>");
}
//设置箱子毛重
function weightBox(boxNumber) {
    //$('#workGridBoxManage').datagrid('selectRow', index);
    //var row = $('#workGridBoxManage').datagrid('getSelected');
    $('#weightBoxDlg').dialog('open').dialog('center').dialog('setTitle', '箱子毛重设置');
    $('#weightBoxForm').form('clear');
    $('#weightBox-boxNumber').val(boxNumber);
}
function doWeightBox() {
    var boxNumber = $('#weightBox-boxNumber').val();
    var weight = $('#weigthBox').val();
    if (weight == '') {
        $.messager.alert({
            title: '提示',
            msg: '请填写毛重值！'
        });
        return;
    }
    $('#weightBoxDlg').dialog('close');
    $.ajax({
        url: 'weightBox/',
        data: {boxNumber: boxNumber, weight: weight},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            showMask(500, '正在设置' + boxNumber + '号箱毛重，请稍后....');
        },
        success: function (data) {
            hideMask();
            if (data.success) {
                $.messager.alert('提示', boxNumber + '号箱毛重设置成功！');
            }
            else {
                $.messager.alert('提示', boxNumber + '号箱毛重设置成功！\n请重试，或者联系技术支持人员！');
            }
        },
    });
}
//封箱入库-管理员验证
function putBoxIntoStore(type, index, status) {
    $('#putBoxValidateDlg').dialog('open').dialog('center').dialog('setTitle', '管理员认证');
    $('#putBoxValidateForm').form('clear');
    $(".ly_doputBoxValidate").attr("onclick", "putBoxValidate(" + type + ", \'" + index + "\', " + status + ")");
}

function putBoxValidate(type, index, status) {
    var boxNumber;
    if (type == 0) {
        $('#workGridBoxManage').datagrid('selectRow', index);
        var row = $('#workGridBoxManage').datagrid('getSelected');
        boxNumber = row.boxNumber;
    } else {
        boxNumber = index;
    }
    var user = $("#userValidate").val();
    var password = $("#userpassword").val();
    if (user == "" || password == "") {
        $.messager.alert({
            title: '提示',
            msg: '请填写用户名与密码！'
        });
        return;
    }
    $('#putBoxValidateDlg').dialog('close'); //关闭对话框
    $.ajax({
        url: 'boxInOutStore/',
        data: {boxNumber: boxNumber, status: status, user: user, password: password},		// status: 1:封箱入库 0:提取出库
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            $.messager.progress({text: '正在处理' + boxNumber + '号箱出入库操作，请稍后....'});
        },
        success: function (result) {
            $.messager.progress('close');
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });

                $('#workGridBoxManage').datagrid('reload');
            }
            else {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
    });
}


function deleteBox() {
    var row = $('#workGridBoxManage').datagrid('getSelected');
    if (!row) {
        $.messager.alert('提示', '未选择记录! 请先选择一条实物记录！');
        return;
    }

    $.messager.confirm('提示', '是否确认删除' + row.boxNumber + '号箱实物?', function (action) {
        if (action) {
            // 确认删除
            $.ajax({
                url: 'deleteBox/',
                data: {boxNumber: row.boxNumber},
                type: 'POST',
                async: true,
                dataType: 'json',
                beforeSend: function (xhr) {
                    showMask(400, '正在删除' + row.boxNumber + '号箱实物, 请稍后...');
                },
                success: function (result, status) {
                    hideMask();
                    if (result.success) {
                        $.messager.show({    // 显示成功信息
                            title: '提示',
                            msg: result.message,
                            showType: 'slide',
                            timeout: 5000
                        });
                        $('#workGridBoxManage').datagrid('reload');		// 重载数据
                    }
                    else {
                        $.messager.show({    // 显示失败信息
                            title: '提示',
                            msg: result.message,
                        });
                    }
                }
            });
        }
    });
}
function boxSearch() {
    var productType = $('#boxSearchParameter-productType').combobox('getValue');
    var className = $('#boxSearchParameter-className').combobox('getValue');
    var subClassName = $('#boxSearchParameter-subClassName').combobox('getValue');

    if (productType == '' && className == '' && subClassName == '') {
        $.messager.alert('提示', '请至少选择一项查询条件!');

        return;
    }

    $('#workGridBoxManage').datagrid({
        queryParams: {
            productType: productType,
            className: className,
            subClassName: subClassName,
            status: 0,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridBoxManage').datagrid('reload');		// 重载数据
}
function boxSearchReset() {
    $('#boxSearchParameter-productType').combobox('clear');
    $('#boxSearchParameter-className').combobox('clear');
    $('#boxSearchParameter-subClassName').combobox('clear');
    $('#workGridBoxManage').datagrid({
        queryParams: {
            productType: '',
            className: '',
            subClassName: '',
            status: 0,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridBoxManage').datagrid('reload');		// 重载数据
}
function openCreateWorkDlg(boxNumber) {
    $('#createWorkDlg').dialog('open').dialog('center').dialog('setTitle', '创建作业');
    $('#createWorkForm').form('clear');

    $('#createWork-boxNumber').val(boxNumber);

    $('#createWork-thingsGrid').datagrid({
        url: 'getThing/',
        queryParams: {boxNumber: boxNumber, thingIsAllocated: 'notAllocated'},
        columns: [[
            {field: 'checkStatus', checkbox: true},
            {field: 'serialNumber', title: '编号', align: 'center'},
            {field: 'boxNumber', title: '箱号', align: 'center'},
            {field: 'productType', title: '实物类型', align: 'center'},
            {field: 'className', title: '品名', align: 'center'},
            {field: 'subClassName', title: '明细品名', align: 'center'},
            {field: 'wareHouse', title: '发行库', align: 'center'},
        ]],
        pagination: true,
        fit: true,
        pageSize: 20,
        fitColumns: true,
        rownumbers: true,
        toolbar: '#createWork-thingsGrid-ToolBar',
        onCheck: function (index, row) {
            var content = $('#createWork-selectedThing').textbox('getValue');
            var reg = new RegExp(row.serialNumber + ';', 'g');
            if (!reg.test(content)) {
                content = content + row.serialNumber + ';';
                $('#createWork-selectedThing').textbox('setValue', content);
                var n = Number($('#createWork-selectedThingCount').text()) + 1;
                $('#createWork-selectedThingCount').text(n);
            }
        },
        onUncheck: function (index, row) {
            var content = $('#createWork-selectedThing').textbox('getValue');
            var target = row.serialNumber + ';';
            var reg = new RegExp(target, 'g');
            content = content.replace(reg, '');
            $('#createWork-selectedThing').textbox('setValue', content);
            var n = Number($('#createWork-selectedThingCount').text()) - 1;
            $('#createWork-selectedThingCount').text(n);
        },
        onCheckAll: function (rows) {
            var content = $('#createWork-selectedThing').textbox('getValue');

            var n = Number($('#createWork-selectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + rows[r].serialNumber + ';';
                    n = n + 1;
                }
            }
            $('#createWork-selectedThingCount').text(n);

            $('#createWork-selectedThing').textbox('setValue', content);
        },
        onUncheckAll: function (rows) {
            var content = $('#createWork-selectedThing').textbox('getValue');

            var n = Number($('#createWork-selectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (reg.test(content)) {
                    content = content.replace(reg, '');
                    n = n - 1;
                }
            }
            $('#createWork-selectedThingCount').text(n);

            $('#createWork-selectedThing').textbox('setValue', content);
        },
    }).datagrid('getPager').pagination({
        layout: ['prev', 'sep', 'links', 'sep', 'next'],
        displayMsg: '当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录'
    });

    $('#createWork-thingsGrid-ToolBar-thingIsAllocated').combobox({
        valueField: 'id',
        textField: 'text',
        editable: false,
        data: [
            {id: 'notAllocated', text: '未分配'},
            {id: 'all', text: '全部'},
            {id: 'allocated', text: '已分配'},
        ],
        panelHeight: 'auto',
        'onSelect': function (record) {
            $('#createWork-thingsGrid').datagrid('options').queryParams['thingIsAllocated'] = record.id;
            $('#createWork-thingsGrid').datagrid('reload');
        },
    }).combobox('select', 'notAllocated');

    $('#createWork-workName').textbox({
        editable: false,
        width: '250px',
    });

    $('#createWork-amount').numberbox({
        width: '250px',
    });

    $('#createWork-selectedThing').textbox({
        fit: true,
        multiline: true,
        editable: false,
    });

    generateWorkName();
    $('#createWork-selectedThingCount').text(0);
}
function generateWorkName() {
    var boxNumber = $('#createWork-boxNumber').val();
    var result = $.ajax({
        url: 'generateWorkName/',
        data: {boxNumber: boxNumber},
        type: 'GET',
        async: false,
        dataType: 'json',
    });
    var data = eval('(' + result.responseText + ')')

    $('#createWork-workName').textbox('setValue', data.workName);
}
function generateContentForWork() {
    var amount = $('#createWork-amount').numberbox('getValue');
    var boxNumber = $('#createWork-boxNumber').val();

    if (0 == amount) {
        $('#createWork-selectedThing').textbox('reset');
        return;
    }

    $.ajax({
        url: 'generateContentForWork/',
        data: {boxNumber: boxNumber, amount: amount},
        type: 'POST',
        async: true,
        dataType: 'json',
        success: function (result) {
            rows = result.data

            var content = $('#createWork-selectedThing').textbox('getValue');
            var n = Number($('#createWork-selectedThingCount').text());

            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + rows[r].serialNumber + ';';
                    n = n + 1;
                }
            }
            $('#createWork-selectedThingCount').text(n);

            $('#createWork-selectedThing').textbox('setValue', content);
        },
    });
}
function generateBoxInfo(index, number) {
    $('#workGridBoxManage').datagrid('selectRow', index);
    var row = $('#workGridBoxManage').datagrid('getSelected');

    $('#generateBoxInfoDlg').dialog('open').dialog('center').dialog('setTitle', '生成装箱清单');
    $('#generateBoxInfoForm').form('clear');

    if (number == 0) {
        $('#generateBoxInfo-boxNumber').val(row.boxNumber);
    } else {
        $('#generateBoxInfo-boxNumber').val(number);
    }

    var today = new Date();
    $('#generateBoxInfoDateTime').datebox('setValue', today.getMonth + '/' + today.getDate() + '/' + today.getFullYear());
}
function doGenerateBoxInfo() {
    $('#generateBoxInfoDlg').dialog('close');

    var row = $('#workGridBoxManage').datagrid('getSelected');
    var date = $('#generateBoxInfoDateTime').datebox('getValue');
    var number = $('#generateBoxInfo-boxNumber').val();

    $.ajax({
        url: 'generateBoxInfo/',
        data: {boxNumber: number, dateTime: date},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在生成'+row.boxNumber+'号箱装箱清单，请稍后....'});
            showMask(500, '正在生成' + row.boxNumber + '号箱装箱清单，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                var downloadURL = data.downloadURL;
                $.messager.alert('提示', row.boxNumber + '号箱装箱清单生成成功！\r\n请点击下载:' + downloadURL);
            }
            else {
                $.messager.alert('提示', row.boxNumber + '号箱装箱清单生成失败！\n请重试，或者联系技术支持人员！');
            }
        },
    });
}
function generateBoxInfoDetailedVersion(index, number) {
    debugger;
    $('#workGridBoxManage').datagrid('selectRow', index);
    var row = $('#workGridBoxManage').datagrid('getSelected');
    if (number == 0) {
        row["newnumber"] = row.boxNumber;
    } else {
        row["newnumber"] = number;
    }
    var valid = true;
    // 目前因金银币章类、银元类、金银工艺品类装箱清单(详细版)均未确定, 所以不提供生成装箱清单(详细版)！
    var productTypes = ["金银工艺品类", "银元类", "金银币章类"]
    $.each(productTypes, function (idx, e) {
        if (row.productType == e) {
            valid = false;

            $.messager.alert({
                title: '提示',
                msg: '因金银币章类、银元类、金银工艺品类装箱清单(详细版)均未确定, 暂不提供生成装箱清单(详细版)！请联系管理员！'
            });

            return valid;
        }
    });
    if (!valid) {
        return;
    }

    $('#generateBoxInfoDetailedVersionDlg').dialog('open').dialog('center').dialog('setTitle', '生成装箱清单(详细版)');
    $('#generateBoxInfoDetailedVersionForm').form('clear');

    var today = new Date();
    $('#generateBoxInfoDetailedVersionDateTime').datebox('setValue', today.getMonth + '/' + today.getDate() + '/' + today.getFullYear());
}
function doGenerateBoxInfoDetailedVersion() {
    $('#generateBoxInfoDetailedVersionDlg').dialog('close');

    var row = $('#workGridBoxManage').datagrid('getSelected');
    var date = $('#generateBoxInfoDetailedVersionDateTime').datebox('getValue');
    $.ajax({
        url: 'generateBoxInfoDetailedVersion/',
        data: {boxNumber: row.newnumber, dateTime: date},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在生成'+row.boxNumber+'号箱装箱清单，请稍后....'});
            showMask(500, '正在生成' + row.boxNumber + '号箱装箱清单(详细版)，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                var downloadURL = data.downloadURL;
                $.messager.alert('提示', row.boxNumber + '号箱装箱清单(详细版)生成成功！\r\n请点击下载:' + downloadURL);
            }
            else {
                $.messager.alert('提示', row.boxNumber + '号箱装箱清单(详细版)生成失败！\n请重试，或者联系技术支持人员！');
            }
        },
    });
}
function generateAbstract(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    workGridWorkManage
    var row = $('#workGridWorkManage').datagrid('getSelected');

    $.ajax({
        url: 'generateAbstract/',
        data: {
            workName: row.workName,
            boxNumber: row.boxNumber,
            subBoxNumber: row.subBoxNumber,
            workSeq: row.workSeq
        },
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在导出'+row.workName+'标签，请稍后....'});
            showMask(400, '正在导出' + row.workName + '实物信息摘要，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                var downloadURL = data.downloadURL;
                $.messager.alert('提示', row.workName + '实物信息摘要生成成功！\r\n请点击<a href="' + downloadURL + '">下载</a>');
            }
            else {
                $.messager.alert('提示', '作业尚未完成！\r\n' + row.workName + '实物信息摘要生成失败！');
            }
        },
    });
}
function createWork() {
    var workName = $('#createWork-workName').textbox('getValue');
    var boxNumber = $('#createWork-boxNumber').val();
    var selectedThings = $('#createWork-selectedThing').textbox('getValue');
    var operator = $('#operator').val();

    if (selectedThings == '') {
        $.messager.alert({
            title: '提示',
            msg: '选中实物不能为空！'
        });

        return;
    }

    $('#createWorkDlg').dialog('close');

    $.ajax({
        url: 'createWork/',
        data: {workName: workName, boxNumber: boxNumber, selectedThings: selectedThings, operator: operator},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            showMask(400);
        },
        success: function (result) {
            hideMask();
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
    });
}
function openAddToExistingBoxDlg(index, number) {
    $('#workGridBoxManage').datagrid('selectRow', index);
    var row = $('#workGridBoxManage').datagrid('getSelected');

    $('#addToExistingBoxDlg').dialog('open').dialog('center').dialog('setTitle', '并箱操作');
    $('#addToExistingBoxForm').form('clear');
    if (number == 0) {
        $('#addToExistingBoxBoxNumber').text(row.boxNumber);
    } else {
        $('#addToExistingBoxBoxNumber').text(number);
    }

    $('#addToExistingBoxWareHouse').text(row.wareHouse);
    $('#addToExistingBoxProductType').text(row.productType);
    $('#addToExistingBoxClassName').text(row.className);
    $('#addToExistingBoxSubClassName').text(row.subClassName);
}
function addToExistingBox() {
    $('#addToExistingBoxDlg').dialog('close');

    var row = $('#workGridBoxManage').datagrid('getSelected');
    var number = $('#addToExistingBoxBoxNumber').text();
    var amount = $('#addToExistingBoxAmount').numberbox('getValue');
    var startSeq = $('#addToExistingBoxStartSeq').numberbox('getValue');

    $.ajax({
        url: 'addToExistingBox/',
        data: {boxNumber: number, amount: amount, startSeq: startSeq},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在处理'+row.boxNumber+'号箱并箱操作，请稍后....'});
            showMask(500, '正在处理' + row.boxNumber + '号箱并箱操作，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                $.messager.alert('提示', row.boxNumber + '号箱并箱成功！');

                $('#workGridBoxManage').datagrid('reload');		// 重载数据
            }
            else {
                $.messager.alert('提示', row.boxNumber + '号箱并箱失败！\n\r原因:' + data.message);
            }
        },
    });
}
/*function putBoxIntoStore(index, status){
 $('#workGridBoxManage').datagrid('selectRow', index);
 var row = $('#workGridBoxManage').datagrid('getSelected');

 $.ajax({
 url: 'boxInOutStore/',
 data: {boxNumber: row.boxNumber, status: status},		// status: 1:封箱入库 0:提取出库
 type: 'POST',
 async: true,
 dataType: 'json',
 beforeSend: function(xhr){
 $.messager.progress({text:'正在处理'+row.boxNumber+'号箱出入库操作，请稍后....'});
 },
 success: function(result){
 $.messager.progress('close');
 if (result.success){
 $.messager.show({    // 显示成功信息
 title: '提示',
 msg: result.message,
 showType: 'slide',
 timeout: 5000
 });

 $('#workGridBoxManage').datagrid('reload');
 }
 else{
 $.messager.alert({    // 显示失败信息
 title: '提示',
 msg: result.message,
 });
 }
 },
 });
 }*/
function exploreBox(boxNumber) {
    var title = boxNumber + '号箱实物';
    var c = '<table id="workGrid' + boxNumber + '" class="easyui-datagrid" data-options="url:\'exploreBox/\', toolbar:\'#workGridToolBar' + boxNumber + '\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20, queryParams: {boxNumber: \'' + boxNumber + '\'},"><thead><tr><th field="serialNumber" align="center" >编号</th><th field="productType" align="center">实物类型</th><th field="className" align="center">品名</th><th field="subClassName" align="center">明细品名</th><th field="wareHouse" align="center">发行库</th><th field="workName" align="center" formatter="thingWorkNameFormatter">所属作业</th><th field="status" align="center" formatter="thingStatusFormatter">是否完成</th><th field="operation" formatter="thingOperationFormatter" align="center">操作</th></tr></thead></table><div id="workGridToolBar' + boxNumber + '"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid' + boxNumber + '\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGrid' + boxNumber + '\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-user');
    initPagination();
}
function thingWorkNameFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}
function thingStatusFormatter(value, row, index) {
    if (value == 0) {
        return '<img src="' + $('#noStatus').attr('value') + '"></img>';
    } else {
        return '<img src="' + $('#okStatus').attr('value') + '"></img>';
    }
}
function thingOperationFormatter(value, row, index) {
    if (row.workName != '') {
        return '<div style="float:center"><a href="exploreThing/' + row.boxNumber + '/' + row.serialNumber + '" target="blank" style="text-decoration:none;color:blue;">查阅电子档案</a></div>';
    }
    else {
        return '-';
    }
}

function workManage() {
    var title = '作业管理';
    var c = '<div class="easyui-layout" data-options="fit: true"><div data-options="region:\'north\'" height="10%"><form id="workSearchParameter" style="display:inline-block;margin-top:12px;"><div style="display:inline;margin-left:10px;margin-right:15px;"><label for="workSearchParameterproductType" style="margin-right:5px">实物类型</label><input id="workSearchParameterproductType" class="easyui-combobox" name="productType" data-options="valueField: \'id\', textField: \'text\', url: \'getProductType/\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var url = \'getClassName/\'+rec.id; $(\'#workSearchParameterclassName\').combobox(\'reload\', url); $(\'#workSearchParameterclassName\').combobox(\'clear\'); $(\'#workSearchParametersubClassName\').combobox(\'clear\');},"/></div><div style="display:inline;margin-right:15px;"><label for="workSearchParameterclassName" style="margin-right:5px;">品名</label><input id="workSearchParameterclassName" class="easyui-combobox" name="className" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var typeCode = $(\'#workSearchParameterproductType\').combobox(\'getValue\'); var url = \'getSubClassName/\'+typeCode+\'&\'+rec.id; $(\'#workSearchParametersubClassName\').combobox(\'reload\', url);},"/></div><div style="display:inline;margin-right:15px;"><label for="workSearchParametersubClassName" style="margin-right:5px;">明细品名</label><input id="workSearchParametersubClassName" class="easyui-combobox" name="subClassName" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\',"/></div></form><a href="javascript:void(0)" class="easyui-linkbutton" onclick="workSearch()" style="width:60px;margin-right:10px;">查询</a><a href="javascript:void(0)" class="easyui-linkbutton" onclick="workSearchReset()" style="width:60px;margin-right:10px;">重置</a></div><div data-options="region:\'center\'"><table id="workGridWorkManage" class="easyui-datagrid" data-options="url:\'getWork/\', queryParams: {status: 0}, toolbar: \'#workGridToolBarWorkManage\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20,"><thead><tr><th field="workName" align="center">作业名称</th><th field="amount" align="center" >件数</th><th field="createDateTime" align="center" formatter="dateTimeFormatter">创建时间</th><th field="completePercent" align="center" formatter="completePercentFormatter">进度</th><th field="completeDateTime" align="center" formatter="dateTimeFormatter">完成时间</th><th field="operation" formatter="workOperationFormatter" align="center">操作</th></tr></thead></table></div></div><div id="workGridToolBarWorkManage"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGridWorkManage\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGridWorkManage\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-work');
    initPagination();
}
function completePercentFormatter(value, row, index) {
    return '<a href="javascript:void(0)" onclick="openDetailedCompleteInfo(' + index + ')" style="text-decoration:none;color:blue;">' + value + '%</a>';
}
function openDetailedCompleteInfo(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    $('#detailedCompleteInfoDlg').dialog('open').dialog('center').dialog('setTitle', row.workName + '完成进度详细信息');
    $('#detailedCompleteInfoForm').form('clear');

    $('#detailedCompleteInfoCheckingCompleteAmount').text(row.checkingCompleteAmount);
    $('#detailedCompleteInfoNumberingCompleteAmount').text(row.numberingCompleteAmount);
    $('#detailedCompleteInfoAnalyzingCompleteAmount').text(row.analyzingCompleteAmount);
    $('#detailedCompleteInfoMeasuringCompleteAmount').text(row.measuringCompleteAmount);
    $('#detailedCompleteInfoPhotographingCompleteAmount').text(row.photographingCompleteAmount);
}
function dateTimeFormatter(value, row, index) {
    if (value == '') {
        return '-'
    }
    else {
        return value;
    }
}
function workOperationFormatter(value, row, index) {
    if (row.status == 0) {
        // return '<div style="float:left"><a href="javascript:void(0);" onclick="workStartOrStop('+index+', 1)" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">分发</a><a href="javascript:void(0);" onclick="generateTag('+index+')" style="text-decoration:none;color:blue;margin-right:20px;">生成标签</a><a href="javascript:void(0);" onclick="generateArchives('+index+')" style="text-decoration:none;color:blue;margin-right:20px;">生成信息档案</a><a href="javascript:void(0);" onclick="exploreWork('+index+')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a><a href="javascript:void(0);" onclick="openEditWorkDlg('+index+')" style="text-decoration:none;color:blue;margin-right:20px;">编辑</a><a href="javascript:void(0);" onclick="deleteWork('+index+')" style="text-decoration:none;color:blue;margin-right:20px;">删除</a></div>'
        return '<div style="float:left"><a href="javascript:void(0);" onclick="workStartOrStop(' + index + ', 1)" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">分发</a><a href="javascript:void(0);" onclick="generateTag(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">生成标签</a><a href="javascript:void(0);" onclick="generateArchives(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">生成信息档案</a><a href="javascript:void(0);" onclick="generateAbstract(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">生成实物信息摘要</a><a href="javascript:void(0);" onclick="exploreWork(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a><a href="javascript:void(0);" onclick="deleteWork(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">删除</a></div>'
    }
    else if (row.status == 1) {
        return '<div style="float:left"><a href="javascript:void(0);" onclick="workStartOrStop(' + index + ', 0)" style="text-decoration:none;color:blue;margin-left:20px;margin-right:20px;">收回</a><a href="javascript:void(0);" onclick="exploreWork(' + index + ')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a></div>'
    }
}
function deleteWork(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    var result;
    $.messager.confirm('提示', '是否确认删除“' + row.workName + '”?', function (action) {
        if (action) {
            // 确认删除
            $.ajax({
                url: 'deleteWork/',
                data: {
                    workName: row.workName,
                    boxNumber: row.boxNumber,
                    subBoxNumber: row.subBoxNumber,
                    workSeq: row.workSeq
                },
                type: 'POST',
                async: true,
                dataType: 'json',
                beforeSend: function (xhr) {
                    // $.messager.progress({text:'正在删除'+row.workName+'，请稍后....'});
                    showMask(500, '正在删除' + row.workName + '，请稍后....');
                },
                success: function (data) {
                    // $.messager.progress('close');
                    hideMask();
                    if (data.success) {
                        $.messager.show({    // 显示成功信息
                            title: '提示',
                            msg: data.message,
                            showType: 'slide',
                            timeout: 5000
                        });

                        $('#workGridWorkManage').datagrid('reload');
                    }
                    else {
                        $.messager.alert({    // 显示失败信息
                            title: '提示',
                            msg: data.message,
                        });
                    }
                },
            });
        }
    });
}
function exploreWork(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    var title = row.workName;
    var workSeq = row.workSeq;
    var boxNumber = row.boxNumber;
    var subBoxNumber = row.subBoxNumber;
    var id = row.id;
    var c = '<table id="workGrid' + id + '" class="easyui-datagrid" data-options="url:\'getStatusData/\', toolbar:\'#workGridToolBar' + id + '\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20, queryParams: {boxNumber: \'' + boxNumber + '\', subBoxNumber: \'' + subBoxNumber + '\', workSeq: \'' + workSeq + '\'},"><thead><tr><th field="serialNumber" align="center" rowspan="2">编号</th><th field="productType" align="center" rowspan="2">实物类型</th><th field="className" align="center" rowspan="2">品名</th><th field="subClassName" align="center" rowspan="2">明细品名</th><th align="center" colspan="3">实物鉴定</th><th align="center" colspan="3">频谱分析</th><th align="center" colspan="3">测量称重</th><th align="center" colspan="3">数据复核</th><th field="operation" formatter="thingOperationFormatter" align="center" rowspan="2">操作</th></tr><tr><th field="status1st" formatter="thingStatusFormatter" align="center">是否完成</th><th field="operator1st" formatter="thingOperatorFormatter" align="center">记录人</th><th field="updateDate1st" align="center" formatter="thingUpdateDateFormatter">更新时间</th><th field="status2nd" formatter="thingStatusFormatter" align="center">是否完成</th><th field="operator2nd" formatter="thingOperatorFormatter" align="center">记录人</th><th field="updateDate2nd" align="center" formatter="thingUpdateDateFormatter">更新时间</th><th field="status3rd" formatter="thingStatusFormatter" align="center">是否完成</th><th field="operator3rd" formatter="thingOperatorFormatter" align="center">记录人</th><th field="updateDate3rd" align="center" formatter="thingUpdateDateFormatter">更新时间</th><th field="status4th" formatter="thingStatusFormatter" align="center">是否完成</th><th field="operator4th" formatter="thingOperatorFormatter" align="center">记录人</th><th field="updateDate4th" align="center" formatter="thingUpdateDateFormatter">更新时间</th></tr></thead></table><div id="workGridToolBar' + id + '"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid' + id + '\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGrid' + id + '\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-user');
    initPagination();
}
function thingOperatorFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}
function thingUpdateDateFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}

function workSearch() {
    var productType = $('#workSearchParameterproductType').combobox('getValue');
    var className = $('#workSearchParameterclassName').combobox('getValue');
    var subClassName = $('#workSearchParametersubClassName').combobox('getValue');

    if (productType == '' && className == '' && subClassName == '') {
        $.messager.alert('提示', '请至少选择一项查询条件!');

        return;
    }

    $('#workGridWorkManage').datagrid({
        queryParams: {
            productType: productType,
            className: className,
            subClassName: subClassName,
            status: 0,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridWorkManage').datagrid('reload');		// 重载数据
}
function workSearchReset() {
    $('#workSearchParameterproductType').combobox('clear');
    $('#workSearchParameterclassName').combobox('clear');
    $('#workSearchParametersubClassName').combobox('clear');
    $('#workGridWorkManage').datagrid({
        queryParams: {
            productType: '',
            className: '',
            subClassName: '',
            status: 0,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridWorkManage').datagrid('reload');		// 重载数据
}

function workStartOrStop(index, status) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');
    $.ajax({
        url: 'startOrStopWork/',
        data: {
            workName: row.workName,
            boxNumber: row.boxNumber,
            subBoxNumber: row.subBoxNumber,
            workSeq: row.workSeq,
            status: status
        },
        type: 'POST',
        async: true,
        dataType: 'json',
        success: function (result) {
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });

                $('#workGridWorkManage').datagrid('reload');
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
    });
}
function openEditWorkDlg(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    $('#editWorkDlg').dialog('open').dialog('center').dialog('setTitle', '编辑作业');
    $('#editWorkForm').form('clear');

    $('#editWorkboxNumber').val(row.boxNumber);
    $('#editWorkworkName').text(row.workName);
    $('#editWorkworkAmount').text(row.amount);

    $('#editWorkthingsGrid').datagrid({
        url: 'getThing/',
        queryParams: {boxNumber: row.boxNumber, workSeq: row.workSeq, thingIsAllocated: 'notAllocated'},
        columns: [[
            {field: 'checkStatus', checkbox: true},
            {field: 'serialNumber', title: '编号', align: 'center'},
            {field: 'boxNumber', title: '箱号', align: 'center'},
            {field: 'productType', title: '实物类型', align: 'center'},
            {field: 'className', title: '品名', align: 'center'},
            {field: 'subClassName', title: '明细品名', align: 'center'},
            {field: 'wareHouse', title: '发行库', align: 'center'},
        ]],
        pagination: true,
        fit: true,
        pageSize: 20,
        fitColumns: true,
        rownumbers: true,
        toolbar: '#editWorkthingsGridToolBar',
        onCheck: function (index, row) {
            var content = $('#editWorkselectedThing').textbox('getValue');
            var reg = new RegExp(row.serialNumber + ';');
            if (!reg.test(content)) {
                content = content + row.serialNumber + ';';
                $('#editWorkselectedThing').textbox('setValue', content);
                var n = Number($('#editWorkselectedThingCount').text()) + 1;
                $('#editWorkselectedThingCount').text(n);
            }
        },
        onUncheck: function (index, row) {
            var content = $('#editWorkselectedThing').textbox('getValue');
            var target = row.serialNumber + ';';
            var reg = new RegExp(target, 'g');
            content = content.replace(reg, '');
            $('#editWorkselectedThing').textbox('setValue', content);
            var n = Number($('#editWorkselectedThingCount').text()) - 1;
            $('#editWorkselectedThingCount').text(n);
        },
        onCheckAll: function (rows) {
            var content = $('#editWorkselectedThing').textbox('getValue');

            var n = Number($('#editWorkselectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (!reg.test(content)) {
                    content = content + rows[r].serialNumber + ';';
                    n = n + 1;
                }
            }
            $('#editWorkselectedThingCount').text(n);

            $('#editWorkselectedThing').textbox('setValue', content);
        },
        onUncheckAll: function (rows) {
            var content = $('#editWorkselectedThing').textbox('getValue');

            var n = Number($('#editWorkselectedThingCount').text());
            for (var r in rows) {
                var reg = new RegExp(rows[r].serialNumber + ';', 'g');
                if (reg.test(content)) {
                    content = content.replace(reg, '');
                    n = n - 1;
                }
            }
            $('#editWorkselectedThingCount').text(n);

            $('#editWorkselectedThing').textbox('setValue', content);
        },
    }).datagrid('getPager').pagination({
        layout: ['prev', 'sep', 'links', 'sep', 'next'],
        displayMsg: '当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录'
    });

    $('#editWorkthingsGridToolBarthingIsAllocated').combobox({
        valueField: 'id',
        textField: 'text',
        editable: false,
        data: [
            {id: 'notAllocated', text: '未分配'},
            // {id: 'all', text: '全部'},
            // {id: 'allocated', text: '本作业'},
        ],
        panelHeight: 'auto',
        'onSelect': function (record) {
            $('#editWorkthingsGrid').datagrid('options').queryParams['thingIsAllocated'] = record.id;
            $('#editWorkthingsGrid').datagrid('reload');
        },
    }).combobox('select', 'notAllocated');

    $('#editWorkselectedThing').textbox({
        fit: true,
        multiline: true,
        editable: false,
    });
}
function generateTag(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    $.ajax({
        url: 'generateTag/',
        data: {boxNumber: row.boxNumber, subBoxNumber: row.subBoxNumber, workSeq: row.workSeq},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在导出'+row.workName+'标签，请稍后....'});
            showMask(400, '正在导出' + row.workName + '标签，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                var downloadURL = data.downloadURL;
                $.messager.alert('提示', row.workName + '作业标签生成成功！\r\n请点击<a href="' + downloadURL + '">下载</a>');
            }
            else {
                $.messager.alert('提示', row.workName + '作业标签生成失败！\n请重试，或者联系技术支持人员！');
            }
        },
    });
}
function generateArchives(index) {
    $('#workGridWorkManage').datagrid('selectRow', index);
    var row = $('#workGridWorkManage').datagrid('getSelected');

    $('#generateArchivesDlg').dialog('open').dialog('center').dialog('setTitle', '生成信息档案');
    $('#generateArchivesForm').form('clear');

    var today = new Date();
    $('#generateArchivesDateTime').datebox('setValue', today.getMonth + '/' + today.getDate() + '/' + today.getFullYear());
}
function doGenerateArchives() {
    $('#generateArchivesDlg').dialog('close');

    var row = $('#workGridWorkManage').datagrid('getSelected');
    var date = $('#generateArchivesDateTime').datebox('getValue');

    $.ajax({
        url: 'generateArchives/',
        data: {boxNumber: row.boxNumber, subBoxNumber: row.subBoxNumber, workSeq: row.workSeq, dateTime: date},
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            // $.messager.progress({text:'正在生成'+row.workName+'信息档案，请稍后....'});
            showMask(500, '正在生成' + row.workName + '信息档案，请稍后....');
        },
        success: function (data) {
            // $.messager.progress('close');
            hideMask();
            if (data.success) {
                var downloadURL = data.downloadURL;
                $.messager.alert('提示', row.workName + '作业信息档案生成成功！\r\n请点击<a href="' + downloadURL + '">下载</a>');
            }
            else {
                $.messager.alert('提示', row.workName + '作业信息档案生成失败！\n请重试，或者联系技术支持人员！');
            }
        },
    });
}

function archivedBoxManage() {
    var title = '封箱实物管理';
    var c = '<div class="easyui-layout" data-options="fit: true"><div data-options="region:\'north\'" height="10%"><form id="archivedBoxSearchParameter" style="display:inline-block;margin-top:12px;"><div style="display:inline;margin-left:10px;margin-right:15px;"><label for="archivedBoxSearchParameterproductType" style="margin-right:5px">实物类型</label><input id="archivedBoxSearchParameterproductType" class="easyui-combobox" name="productType" data-options="valueField: \'id\', textField: \'text\', url: \'getProductType/\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var url = \'getClassName/\'+rec.id; $(\'#archivedBoxSearchParameterclassName\').combobox(\'reload\', url); $(\'#archivedBoxSearchParameterclassName\').combobox(\'clear\'); $(\'#archivedBoxSearchParametersubClassName\').combobox(\'clear\');},"/></div><div style="display:inline;margin-right:15px;"><label for="archivedBoxSearchParameterclassName" style="margin-right:5px;">品名</label><input id="archivedBoxSearchParameterclassName" class="easyui-combobox" name="className" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\', onSelect: function(rec){ var typeCode = $(\'#archivedBoxSearchParameterproductType\').combobox(\'getValue\'); var url = \'getSubClassName/\'+typeCode+\'&\'+rec.id; $(\'#archivedBoxSearchParametersubClassName\').combobox(\'reload\', url);},"/></div><div style="display:inline;margin-right:15px;"><label for="archivedBoxSearchParametersubClassName" style="margin-right:5px;">明细品名</label><input id="archivedBoxSearchParametersubClassName" class="easyui-combobox" name="subClassName" data-options="valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\',"/></div></form><a href="javascript:void(0)" class="easyui-linkbutton" onclick="archivedBoxSearch()" style="width:60px;margin-right:10px;">查询</a><a href="javascript:void(0)" class="easyui-linkbutton" onclick="archivedBoxSearchReset()" style="width:60px;margin-right:10px;">重置</a></div><div data-options="region:\'center\'"><table id="workGridArchivedBoxManage" class="easyui-datagrid" data-options="url:\'getBox/\', queryParams: {status: 1},toolbar:\'#workGridToolBarArchivedBoxManage\', onClickRow:ClickRowList, singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20"><thead><tr><th field="boxNumber" align="center" width="7%">箱号</th><th field="productType" align="center">实物类型</th><th field="className" align="center">品名</th><th field="subClassName" align="center">明细品名</th><th field="wareHouse" align="center" >发行库</th><th field="amount" align="center" >件数</th><th field="operation" formatter="archivedBoxOperationFormatter" align="center" width="15%">操作</th></tr></thead></table></div></div><div id="workGridToolBarArchivedBoxManage"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGridArchivedBoxManage\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGridArchivedBoxManage\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-user');
    initPagination();
}
function archivedBoxOperationFormatter(value, row, index) {
    if (row.haveSubBox == "0") {
        return '<div style="float:left;"><a href="javascript:void(0);" onclick="extractBoxFromStore(0, \'' + index + '\', 0)" style="text-decoration:none;color:blue;margin-right:20px;">开箱出库</a><a href="javascript:void(0);" onclick="exploreBox(\'' + row.boxNumber + '\')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a></div>';
    } else {
        //return '<div style="float:left;"></div>';
        return '<div style="float:left;"><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a><a href="javascript:void(0);" style="text-decoration:none;color:blue;margin-right:20px;"></a></div>';
    }
}
//封箱实物查询-点击展现子箱列表
function ClickRowList(index, row) {
    var selectids = $('#workGridArchivedBoxManage').datagrid('getPanel').find(".datagrid-row-selected");
    $(".ly_hidden").remove();
    var clss = $("#" + selectids[1].id + " td div").eq(0).attr('class');
    clss = clss.substring(clss.indexOf('-cell-') + 6, clss.lastIndexOf('-'));
    if (row.haveSubBox == "1") {
        var boxMap = row.subBoxDict;
        var thhtml = "";
        var trhtml = "";
        for (var key in boxMap) {
            thhtml += "<tr class='ly_hidden' style='height: 25px;'><td><div class='datagrid-cell-rownumber'></div></td></tr>";
            trhtml += '<tr class="ly_hidden" style="height: 25px;"><td field="boxNumber"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-boxNumber">' + row.boxNumber + '-' + key + '</div></td><td field="productType"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-productType">' + row.productType + '</div></td><td field="className"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-className">' + row.className + '</div></td><td field="subClassName"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-subClassName">' + row.subClassName + '</div></td><td field="wareHouse"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-wareHouse">' + row.wareHouse + '</div></td><td field="amount"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-amount">' + boxMap[key] + '</div></td><td field="operation"><div style="text-align:center;height:auto;" class="datagrid-cell datagrid-cell-' + clss + '-operation"><div style="float:left;"><a href="javascript:void(0);" onclick="extractBoxFromStore(1, \'' + row.boxNumber + '-' + key + '\', 0)" style="text-decoration:none;color:blue;margin-right:20px;">开箱出库</a><a href="javascript:void(0);" onclick="exploreBox(\'' + row.boxNumber + '-' + key + '\')" style="text-decoration:none;color:blue;margin-right:20px;">浏览</a></div></div></td></tr>';
        }
        $("#" + selectids[0].id).after(thhtml);
        $("#" + selectids[1].id).after(trhtml);
    }
}

function extractBoxFromStore(type, index, status) {
    var boxNumber;
    if (type == 0) {
        $('#workGridArchivedBoxManage').datagrid('selectRow', index);
        var row = $('#workGridArchivedBoxManage').datagrid('getSelected');
        boxNumber = row.boxNumber;
    } else {
        boxNumber = index;
    }

    $.ajax({
        url: 'boxInOutStore/',
        data: {boxNumber: boxNumber, status: status},		// status: 1:封箱入库 0:提取出库
        type: 'POST',
        async: true,
        dataType: 'json',
        beforeSend: function (xhr) {
            $.messager.progress({text: '正在处理' + boxNumber + '号箱出入库操作，请稍后....'});
        },
        success: function (result) {
            $.messager.progress('close');
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });

                $('#workGridArchivedBoxManage').datagrid('reload');
            }
            else {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
    });
}
function archivedBoxSearch() {
    var productType = $('#archivedBoxSearchParameterproductType').combobox('getValue');
    var className = $('#archivedBoxSearchParameterclassName').combobox('getValue');
    var subClassName = $('#archivedBoxSearchParametersubClassName').combobox('getValue');

    if (productType == '' && className == '' && subClassName == '') {
        $.messager.alert('提示', '请至少选择一项查询条件!');
        return;
    }

    $('#workGridArchivedBoxManage').datagrid({
        queryParams: {
            productType: productType,
            className: className,
            subClassName: subClassName,
            status: 1,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridArchivedBoxManage').datagrid('reload');		// 重载数据
}
function archivedBoxSearchReset() {
    $('#archivedBoxSearchParameterproductType').combobox('clear');
    $('#archivedBoxSearchParameterclassName').combobox('clear');
    $('#archivedBoxSearchParametersubClassName').combobox('clear');
    $('#workGridArchivedBoxManage').datagrid({
        queryParams: {
            productType: '',
            className: '',
            subClassName: '',
            status: 1,
        }
    });
    initPagination();								// 设定翻页插件
    $('#workGridArchivedBoxManage').datagrid('reload');		// 重载数据
}


function userManage() {
    var title = '用户管理';
    var c = '<table id="workGridUser" class="easyui-datagrid" data-options="url:\'getUser/\', toolbar:\'#workGridToolBarUser\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20, checkOnSelect:false, selectOnCheck:false"><thead><tr><th field="checkStatus" align="center" checkbox="true"></th><th field="nickName" align="center" width="20">用户名</th><th field="type" formatter="userTypeFormatter" align="center" width="20">用户类型</th><th field="operation" formatter="operationFormatter" align="center" width="60">操作</th</tr></thead></table><div id="workGridToolBarUser"><a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="userAdd()">添加</a><a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="userRemove()">删除</a></div><script type="text/javascript">function initPagination(){$(\'#workGridUser\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-user');
    initPagination();
}
function userTypeFormatter(value, row, index) {
    if (value == 0) {
        return '超级管理员';
    }
    else if (value == 1) {
        return '管理员';
    } else if (value == 2) {
        return '一般用户';
    }
}
function operationFormatter(value, row, index) {
    return '<div style="float:left"><a href="javascript:void(0);" onclick="updatePassword(\'' + row.nickName + '\')" style="text-decoration:none;color:blue">更改密码</a></div>'
}

function userAdd() {
    $('#userDlg').dialog('open').dialog('center').dialog('setTitle', '用户添加');
    $('#userForm').form('clear');
    url = 'userProcess/';
    opType = 'add';
}
function userRemove() {
    url = 'userProcess/';
    opType = 'remove';

    var rows = $('#workGridUser').datagrid('getChecked');
    var n = rows.length
    if (0 == n) {
        $.messager.alert('提示', '未选择记录! 请先选择一条用户记录！');
        return;
    }

    var userArray = new Array()
    for (var i = 0; i < n; ++i) {
        userArray[i] = rows[i].nickName;
    }

    $.messager.confirm('提示', '是否确认删除所选用户?', function (r) {
        if (r) {
            $.ajax({
                url: url,
                data: {nickName: userArray, opType: opType},
                type: 'POST',
                async: true,
                dataType: 'json',
                success: function (result, status) {
                    if (result.success) {
                        $.messager.show({    // 显示成功信息
                            title: '提示',
                            msg: result.message,
                            showType: 'slide',
                            timeout: 5000
                        });
                        $('#workGridUser').datagrid('reload');		// 重载数据
                    }
                    else {
                        $.messager.show({    // 显示失败信息
                            title: '提示',
                            msg: result.message,
                        });
                    }
                },
            });
        }
    });
}
function saveUser() {
    $('#userForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            opType: opType
        },
        onSubmit: function (param) {
            return $(this).form('validate');
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            }
            else {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#userDlg').dialog('close');        		// 关闭对话框
                $('#workGridUser').datagrid('reload');		// 重载数据
            }
        }
    });

    $('#userForm').submit();
}

function updatePassword(nickName) {
    $('#updatePasswordDlg').dialog('open').dialog('center').dialog('setTitle', '更改密码');
    $('#updatePasswordForm').form('clear');
    $('#updatePasswordForm').form('load', {
        nickName: nickName,
    });
    url = 'updatePassword/';
}
function savePassword() {
    $('#updatePasswordForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            fromLoc: 'admin'
        },
        onSubmit: function (param) {
            var pwd = $('#updatePassword-password').textbox('getValue');
            var conf = $('#updatePassword-confirm').textbox('getValue');

            if (pwd == conf) {
                return true;
            }
            else {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: '新密码与确认密码不一致！请重新填写！'
                });
                return false;
            }
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            }
            else {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#updatePasswordDlg').dialog('close');        		// 关闭对话框
            }
        }
    });

    $('#updatePasswordForm').submit();
}

function authorityManage() {
    var title = '权限管理';
    var c = '<table id="workGridAuthority" class="easyui-datagrid" data-options="url:\'getAuthority/\', toolbar:\'#workGridToolBarAuthority\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20"><thead><tr><th align="center" rowspan="2" colspan="2" align="center">用户</th><th align="center" colspan="8">岗位权限&nbsp;&nbsp;(<img src="' + $('#okStatus').attr('value') + '">拥有权限</img>&nbsp;&nbsp;&nbsp;&nbsp;<img src="' + $('#noStatus').attr('value') + '">未拥有权限</img>)</th></tr><tr><th align="center" width="20" colspan="2">监控输出</th><th align="center" width="20" colspan="2">实物鉴定</th><th align="center" width="20" colspan="2">频谱分析</th><th align="center" width="20" colspan="2">测量称重</th><th align="center" width="20" colspan="2">图像采集</th></tr><tr><th field="nickName" align="center" width="10">用户名</th><th field="type" formatter="userTypeFormatter" align="center" width="10">用户类型</th><th field="monitoring" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="monitoringAuthority" formatter="monitoringAuthorityFormatter" align="center" width="10">操作</th><th field="numbering" formatter="authorityStatusFormatter"  align="center" width="10">状态</th><th field="numberingAuthority" formatter="numberingAuthorityFormatter" align="center" width="10">操作</th><th field="analyzing" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="analyzingAuthority" formatter="analyzingAuthorityFormatter" align="center" width="10">操作</th><th field="measuring" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="measuringAuthority" formatter="measuringAuthorityFormatter" align="center" width="10">操作</th><th field="photographing" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="photographingAuthority" formatter="photographingAuthorityFormatter" align="center" width="10">操作</th></tr></thead></table><div id="workGridToolBarAuthority"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGridAuthority\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGridAuthority\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-authority');
    initPagination();
}
function authorityStatusFormatter(value, row, index) {
    if (!value) {
        return '<img src="' + $('#noStatus').attr('value') + '"></img>';
    } else {
        return '<img src="' + $('#okStatus').attr('value') + '"></img>';
    }
}
function monitoringAuthorityFormatter(value, row, index) {
    if (1 >= row.type) {
        // 管理员用户，权限不可更改
        return '<span>-</span>';
    }
    if (row.monitoring) {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'monitoring\', \'revoke\')">取消</a>';
    }
    else {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'monitoring\', \'grant\')">授权</a>';
    }
}
function numberingAuthorityFormatter(value, row, index) {
    if (1 >= row.type) {
        return '<span>-</span>';
    }
    if (row.numbering) {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'numbering\', \'revoke\')">取消</a>';
    }
    else {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'numbering\', \'grant\')">授权</a>';
    }
}
function analyzingAuthorityFormatter(value, row, index) {
    if (1 >= row.type) {
        return '<span>-</span>';
    }
    if (row.analyzing) {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'analyzing\', \'revoke\')">取消</a>';
    }
    else {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'analyzing\', \'grant\')">授权</a>';
    }
}
function measuringAuthorityFormatter(value, row, index) {
    if (1 >= row.type) {
        return '<span>-</span>';
    }
    if (row.measuring) {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'measuring\', \'revoke\')">取消</a>';
    }
    else {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'measuring\', \'grant\')">授权</a>';
    }
}
function photographingAuthorityFormatter(value, row, index) {
    if (1 >= row.type) {
        return '<span>-</span>';
    }
    if (row.photographing) {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'photographing\', \'revoke\')">取消</a>';
    }
    else {
        return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\'' + row.nickName + '\', \'photographing\', \'grant\')">授权</a>';
    }
}
function authorityProcess(nickName, authority, opType) {
    $.post('authorityProcess/',
        {nickName: nickName, authority: authority, opType: opType},
        function (result, status) {
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#workGridAuthority').datagrid('reload');		// 重载数据
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
        'json');
}

function propertyManage() {
    var title = '属性数据';
    var c = '<table id="workGridProperty" class="easyui-treegrid" data-options="url:\'getProperty/\', toolbar:\'#workGridToolBarProperty\', singleSelect:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', fit:true, idField: \'id\', treeField:\'type\', lines:true, onLoadSuccess:collapse"><thead><tr><th field="type" align="left" width="300">类型</th><th field="code" align="center" width="253" formatter="contentFormatter">编码</th><th field="remark" align="center" width="253" formatter="contentFormatter">备注</th></tr></thead></table><div id="workGridToolBarProperty"><a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="propertyAdd()">添加</a><a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="propertyRemove()">删除</a><a href="#" class="easyui-linkbutton" iconCls="icon-collapse" plain="true" onclick="collapse()">全部折叠</a><a href="#" class="easyui-linkbutton" iconCls="icon-expand" plain="true" onclick="expand()">全部打开</a></div><script type="text/javascript">function collapse(){ $(\'#workGridProperty\').treegrid(\'collapseAll\'); } function expand(){ $(\'#workGridProperty\').treegrid(\'expandAll\'); }</script>';
    addTab(title, c, 'icon-property');
}
function contentFormatter(value, row, index) {
    if (value == '') {
        return '-';
    }
    else {
        return value;
    }
}

var url;
var opType;
function initPropertyDlg() {
    $('#step1').attr('style', '');
    $('#next').attr('style', '');
    $('#step2').attr('style', 'display:none');
    $('#prev').attr('style', 'display:none');
    $('#propertySave').attr('style', 'display:none');
    $('#cancel').attr('style', 'display:none');
}
function unInitPropertyDlg() {
    $('#step1').attr('style', '');
    $('#next').attr('style', '');
    $('#step2').attr('style', '');
    $('#prev').attr('style', '');
    $('#propertySave').attr('style', '');
    $('#cancel').attr('style', '');
}
function propertyAdd() {
    initPropertyDlg();

    $('#propertyDlg').dialog('open').dialog('center').dialog('setTitle', '属性添加');
    $('#propertyForm').form('clear');
    url = 'propertyProcess/';
    opType = 'add';
}
function propertyRemove() {
    url = 'propertyProcess/';
    opType = 'remove';

    var curNode = $('#workGridProperty').treegrid('getSelected');
    if (!curNode) {
        $.messager.alert('提示', '未选择记录! 请先选择一条属性记录！');
        return;
    }

    $.messager.confirm('提示', '是否确认删除此条属性?', function (r) {
        if (r) {
            $.post(url,
                {id: curNode.id, opType: opType},
                function (result, status) {
                    if (result.success) {
                        $.messager.show({    // 显示成功信息
                            title: '提示',
                            msg: result.message,
                            showType: 'slide',
                            timeout: 5000
                        });
                        $('#workGridProperty').treegrid('reload');		// 重载数据
                    }
                    else {
                        $.messager.show({    // 显示失败信息
                            title: '提示',
                            msg: result.message,
                        });
                    }
                },
                'json');
        }
    });
}
function saveProperty() {
    var project = $('#property-project').combobox('getValue');
    if (project == '实物类型') {
        var productType = $('#property-productType-productType').textbox('getValue');
        var productTypeCode = $('#property-productTypeCode').textbox('getValue');
        if (productType == '' || productTypeCode == '') {
            $.messager.alert({
                title: '提示',
                msg: '实物类型或实物编码不能为空！'
            });
        }
    }
    else if (project == '品名') {
        var productType = $('#property-className-productType').combobox('getValue');
        var className = $('#property-className-className').textbox('getValue');
        var classNameCode = $('#property-classNameCode').textbox('getValue');
        if (productType == '' || className == '' || classNameCode == '') {
            $.messager.alert({
                title: '提示',
                msg: '实物类型、品名名称或品名编码不能为空！'
            });
        }
    }
    else if (project == '明细品名') {
        var productType = $('#property-subClassName-productType').combobox('getValue');
        var className = $('#property-subClassName-className').combobox('getValue');
        var subClassName = $('#property-subClassName-subClassName').textbox('getValue');
        var subClassNameCode = $('#property-subClassNameCode').textbox('getValue');
        if (productType == '' || className == '' || subClassName == '' || subClassNameCode == '') {
            $.messager.alert({
                title: '提示',
                msg: '实物类型、品名名称、明细品名或明细品名编码不能为空！'
            });
        }
    }
    else if (project == '发行库') {
        var wareHouseType = $('#property-wareHouseType').textbox('getValue');
        var wareHouseCode = $('#property-wareHouseCode').textbox('getValue');
        if (wareHouseType == '' || wareHouseCode == '') {
            $.messager.alert({
                title: '提示',
                msg: '发行库名称、发行库编码不能为空！'
            });
        }
    }

    $('#propertyForm').form({
        url: url,
        queryParams: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            opType: opType
        },
        onSubmit: function (param) {
            return $(this).form('validate');
        },
        success: function (result) {
            var result = eval('(' + result + ')');
            if (!result.success) {
                $.messager.alert({    // 显示失败信息
                    title: '提示',
                    msg: result.message
                });
            }
            else {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#propertyDlg').dialog('close');        		// 关闭对话框
                $('#workGridProperty').treegrid('reload');		// 重载数据
            }
        }
    });

    $('#propertyForm').submit();
}

function next() {
    var project = $('#property-project').combobox('getValue');

    if (project != '') {
        $('#step1').attr('style', 'display:none');
        $('#next').attr('style', 'display:none');
        $('#step2').attr('style', '');
        $('#prev').attr('style', '');
        $('#propertySave').attr('style', '');
        $('#cancel').attr('style', '');

        if (project == '实物类型') {
            $('#productType').attr('style', '');
            $('#className').attr('style', 'display:none');
            $('#subClassName').attr('style', 'display:none');
            $('#wareHouse').attr('style', 'display:none');
        }
        else if (project == '品名') {
            $('#property-className-productType').combobox('reload');
            $('#productType').attr('style', 'display:none');
            $('#className').attr('style', '');
            $('#subClassName').attr('style', 'display:none');
            $('#wareHouse').attr('style', 'display:none');
        }
        else if (project == '明细品名') {
            $('#property-subClassName-productType').combobox('reload');
            $('#property-subClassName-className').combobox('reload');
            $('#productType').attr('style', 'display:none');
            $('#className').attr('style', 'display:none');
            $('#subClassName').attr('style', '');
            $('#wareHouse').attr('style', 'display:none');
        }
        else if (project == '发行库') {
            $('#productType').attr('style', 'display:none');
            $('#className').attr('style', 'display:none');
            $('#subClassName').attr('style', 'display:none');
            $('#wareHouse').attr('style', '');
        }
    }
    else {
        $.messager.alert({
            title: '提示',
            msg: '待添加项目不能为空！请选择！',
        });
    }
}

function prev() {
    $('#step1').attr('style', '');
    $('#next').attr('style', '');
    $('#step2').attr('style', 'display:none');
    $('#prev').attr('style', 'display:none');
    $('#propertySave').attr('style', 'display:none');
    $('#cancel').attr('style', 'display:none');
}

function searchArchive() {
    var title = '档案查询';
    var c = '<div class="easyui-layout" data-options="fit:true"><div data-options="region:\'center\'"><table id="archiveGrid" class="easyui-datagrid" data-options="url:\'getArchive/\', border:false, rownumbers:true, fitcolumns:true, fit:true, pagination:true, pagsize:10"><thead><tr><th field="boxNumber" align="center" width="50">箱号</th><th field="productType" align="center" width="150">实物类型</th><th field="amount" align="center" width="150">数量</th><th field="archiveUrl" align="center" formatter="archiveBoxFormatter" width="430">资料</th></tr></thead></table></div></div><script type="text/javascript">$(function(){ $(\'#archiveGrid\').datagrid({ view: detailview, detailFormatter:function(index,row){ return \'<div style="padding:2px"><table class="ddv"></table></div>\';}, onExpandRow: function(index,row){ var ddv = $(this).datagrid(\'getRowDetail\',index).find(\'table.ddv\'); ddv.datagrid({url:\'getWorkData/\'+row.boxNumber, fitColumns:true, singleSelect:true, rownumbers:true, loadMsg:\'\', height:\'auto\', pagination:true, pageSize:10, queryParams:{processId:-1}, columns:[[{field:\'serialNumber\',title:\'编号\',width:100,align:\'center\'},{field:\'boxNumber\',title:\'箱号\',width:50,align:\'center\'},{field:\'className\',title:\'品名\',width:50,align:\'center\'},{field:\'subClassName\',title:\'明细品名\',width:100,align:\'center\'},{field:\'archive\',title:\'资料\',width:250,align:\'center\', formatter:archiveThingFormatter}]],onResize:function(){$(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);},onLoadSuccess:function(){setTimeout(function(){$(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);},0);}}); ddv.datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'}); $(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);}});}); function initPagination(){$(\'#archiveGrid\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
    addTab(title, c, 'icon-archive');
    initPagination();
}
function archiveBoxFormatter(value, row, index) {
    return '<div style="float:left"><a href="getWork/' + row.boxNumber + '" style="text-decoration:none;color:blue;margin-right:20px">档案下载</a><a href="getTag/' + row.boxNumber + '" style="text-decoration:none;color:blue;margin-right:20px">标签下载</a><a href="javascript:void(0);" onclick="backToWork(\'' + row.boxNumber + '\')" style="text-decoration:none;color:blue;margin-right:20px">退回作业</a></div>';
}
function archiveThingFormatter(value, row, index) {
    return '<div style="float:left"><a href="getThing/' + row.boxNumber + '/' + row.serialNumber + '" style="text-decoration:none;color:blue;margin-right:20px">信息档案下载</a><a href="exploreThing/' + row.boxNumber + '/' + row.serialNumber + '" target="blank" style="text-decoration:none;color:blue;margin-right:20px">电子档案查看</a></div>';
}

function backToWork(boxNumber) {
    $.post('backToWork/',
        {boxNumber: boxNumber},
        function (result, status) {
            if (result.success) {
                $.messager.show({    // 显示成功信息
                    title: '提示',
                    msg: result.message,
                    showType: 'slide',
                    timeout: 5000
                });
                $('#archiveGrid').datagrid('reload');		// 重载数据
            }
            else {
                $.messager.show({    // 显示失败信息
                    title: '提示',
                    msg: result.message,
                });
            }
        },
        'json');
}

function searchWork() {
    var title = '全文检索';
    var c = '<div class="easyui-layout" data-options="fit:true">' +
                '<div id="tt" class="easyui-tabs" style="width:100%;height:100%;">'+
                    '<div title="常规检索" style="padding:20px;display:none">'+
        '<iframe src="search/" frameborder="0" style="width:100%;height: 100%;"></iframe>'+'</div>'+
                    '<div class="advancedSearch_btn" title="高级检索" style="overflow:auto;padding:20px;display:none;">高级检索</div>'+
        '<iframe class="advancedSearch" src="/gsinfo/advancedSearch" frameborder="0" style="width:100%;height: 100%;"></iframe>'+
                '</div>'+
             '</div>'+
        '<script type="text/javascript">' +
            '$(".advancedSearch_btn").click(function（){' +
        '})'
        '</script>';
    addTab(title, c, 'icon-archive');
    /**
     *   '$(function(){ $(\'#workGrid\').datagrid({ view: detailview, detailFormatter:function(index,row){ ' +
        'return \'<div style="padding:2px"><table class="ddv"></table></div>\';}, ' +
        'onExpandRow: function(index,row){ var ddv = $(this).datagrid(\'getRowDetail\',index).find(\'table.ddv\');' +
        ' ddv.datagrid({url:\'getWorkData/\'+row.boxNumber, fitColumns:true, singleSelect:true, rownumbers:true, loadMsg:\'\', height:\'auto\', pagination:true, pageSize:10, queryParams:{processId:-1}, columns:[[{field:\'serialNumber\',title:\'编号\',width:100,align:\'center\'},{field:\'boxNumber\',title:\'箱号\',width:50,align:\'center\'},{field:\'className\',title:\'品名\',width:50,align:\'center\'},{field:\'subClassName\',title:\'明细品名\',width:100,align:\'center\'},{field:\'archive\',title:\'资料\',width:250,align:\'center\', formatter:workThingFormatter}]],onResize:function(){$(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);},onLoadSuccess:function(){setTimeout(function(){$(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);},0);}}); ddv.datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'}); $(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);}});}); function initPagination(){$(\'#workGrid\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}' +


    '<div data-options="region:\'center\'">' +
        '<table id="workGrid" class="easyui-datagrid" data-options="url:\'getWorkContent/\', border:false, rownumbers:true, fitcolumns:true, fit:true, pagination:true, pagsize:10">' +
        '<thead>' +
        '<tr>' +
        '<th field="boxNumber" align="center" width="50">箱号</th>' +
        '<th field="productType" align="center" width="150">实物类型</th>' +
        '<th field="amount" align="center" width="150">数量</th>' +
        '<th field="archiveUrl" align="center" formatter="workBoxFormatter" width="430">资料</th>' +
        '</tr>' +
        '</thead>' +
        '</table>' +
        '</div>' +





     */
    // initPagination();
}

function workBoxFormatter(value, row, index) {
    return '<div style="float:left"><a href="getWork/' + row.boxNumber + '" style="text-decoration:none;color:blue;margin-right:20px">档案下载</a><a href="getTag/' + row.boxNumber + '" style="text-decoration:none;color:blue;margin-right:20px">标签下载</a></div>';
}
function workThingFormatter(value, row, index) {
    return '<div style="float:left"><a href="getThing/' + row.boxNumber + '/' + row.serialNumber + '" style="text-decoration:none;color:blue;margin-right:20px">信息档案下载</a><a href="exploreThing/' + row.boxNumber + '/' + row.serialNumber + '" target="blank" style="text-decoration:none;color:blue;margin-right:20px">电子档案查看</a></div>';
}