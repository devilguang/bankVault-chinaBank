//写cookies
function setCookie(name,value){
    var Days = 30;
    var exp = new Date();
    exp.setTime(exp.getTime() + Days*24*60*60*1000);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}

//读取cookies
function getCookie(name){
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
 
    if(arr=document.cookie.match(reg))
 
        return unescape(arr[2]);
    else
        return null;
}

//删除cookies
function delCookie(name){
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    if(cval!=null)
        document.cookie= name + "="+cval+";expires="+exp.toGMTString();
} 

function menuHandler(item){
	if ('add' == item.name)
	{
		newWork();
	}
	else if ('remove' == item.name)
	{
		deleteWork();
	}
	else if ('archive' == item.name)
	{
		archiveWork();
	}
	else if ('outputConfig' == item.name)
	{
		outputConfig();
	}
	else if ('printTag' == item.name)
	{
		printTag();
	}
	else if ('search' == item.name)
	{
		$.messager.alert('提示', '历史查询');
	}
	else if ('outputAbstractConfig' == item.name)
	{
		outputAbstractConfig();
	}
}

function loadDataProcess(node, data){
	// $.messager.alert('提示', 'ok');
	var n = data.length
	for (var i=0; i<n; ++i){
		var m = data[i].children.length
		var works = data[i].children
		for (var j =0; j<m; ++j){
			// find a work node and then select it
			var node = $('#workSpaceTree').tree('find', works[j].id);
			$('#workSpaceTree').tree('select', node.target);
		}
	}
}
function treeSelectHandler(node){
	var isWork = node.attributes.isWork
	if (!isWork)
	{
		return ;
	}
	var title = node.text;
	var id = node.id;
	var workSeq = node.attributes.workSeq;
	var boxNumber = node.attributes.boxNumber;
	var c = '<table id="workGrid'+id+'" class="easyui-datagrid" data-options="url:\'getWorkData/'+workSeq+'\', queryParams:{processId: $(\'#processId\').val(), boxNumber: \''+boxNumber+'\', thingStatus: \'cancheck\'}, toolbar:\'#workGridToolBar'+id+'\', singleSelect:true, fitColumns:true, loaded:false, rownumbers:true, loadMsg:\''+title+'作业数据正在载入，请稍后...\', onDblClickRow:dbClickRow, pagination:true, fit:true, pageSize:20"><thead><tr><th field="serialNumber" align="center" rowspan="2">编号</th><th field="operation" formatter="operationFormatter" align="center" rowspan="2">操作</th><th align="center" colspan="3">数据复核</th></tr><tr><th field="status" formatter="statusFormatter" align="center">是否完成</th><th field="operator" formatter="operatorFormatter" align="center">复核人</th><th field="lastUpdateTime" align="center" formatter="updateDateFormatter">更新时间</th></tr></thead></table><div id="workGridToolBar'+id+'"><label for="workGrid'+id+'StatusCombobox" style="margin-left:5px;margin-right:5px;">状态</label><input id="workGrid'+id+'StatusCombobox" style="margin-right:20px;padding-top:5px;" /><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGrid'+id+'\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">var timer'+id+'; function timingUpdate(){$(\'#workGrid'+id+'\').datagrid(\'reload\'); timer'+id+'=setTimeout("timingUpdate()", 120000);  $.post("getWorkStatus/", {boxNumber:\''+boxNumber+'\'}, function(data, status){if (data.workStatus == 1){ clearTimeout(t); $.messager.alert(\'提示\', \''+title+'作业已经完成，可以导出！\'); }}, \'json\')} function clearTimer'+id+'(){ clearTimeout(timer'+id+'); } function dbClickRow(index, row){/*$.messager.alert(\'提示\', \'select\');*/} function initPagination(){$(\'#workGrid'+id+'\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});} function initToolbar(){ $(\'#workGrid'+id+'StatusCombobox\').combobox({valueField: \'id\', textField: \'text\', editable: false, data: [{id: \'cancheck\', text: \'可复核\'}, {id: \'notComplete\', text: \'未完成\'}, {id: \'all\', text: \'全部\'}, {id: \'complete\', text: \'已完成\'}, ], panelHeight: \'auto\', \'onSelect\':function(record){ $(\'#workGrid'+id+'\').datagrid(\'options\').queryParams[\'thingStatus\'] = record.id; $(\'#workGrid'+id+'\').datagrid(\'reload\'); },}).combobox(\'setValue\', \'cancheck\'); }</script>';
	addTab(title, c, 'icon-box');
}
function addTab(title, content, icon){
    if ($('#tbs').tabs('exists', title)){
        $('#tbs').tabs('select', title);
    } else {
        $('#tbs').tabs('add',{
            title:title,
            content:content,
            closable:true,
			iconCls:icon,
        });
		initPagination();
		initToolbar();
		//timingUpdate();			// 定时更新状态表
    }
}
function statusFormatter(value, row, index){
	if (value == 0){
		return '<img src="'+$('#noStatus').attr('value')+'"></img>';
	}else{
		return '<img src="'+$('#okStatus').attr('value')+'"></img>';
	}
}
function operatorFormatter(value, row, index){
	if (value == ''){
		return '-';
	}
	else{
		return value;
	}
}
function updateDateFormatter(value, row, index){
	if (value == null){
		return '-';
	}
	else{
		return value;
	}
}
function operationFormatter(value, row, index){
	if (value){
		// 实物鉴定, 频谱分析, 测量称重三环节均已完成, 可以进行复核
		var operator = $('#operator').val();
		return '<div style="float:center"><a href="exploreThing/'+row.boxNumber+'/'+row.serialNumber+'?isVerify=1&operator='+operator+'" target="blank" style="text-decoration:none;color:blue;">复核</a></div>';
	}
	else{
		return '-';
	}
	/*var operator = $('#operator').val();
	return '<div style="float:center"><a href="exploreThing/'+row.boxNumber+'/'+row.serialNumber+'?isVerify=1&operator='+operator+'" target="blank" style="text-decoration:none;color:blue;">复核</a></div>';*/
}

var url;
function newWork(){
	$('#createWorkDlg').dialog('open').dialog('center').dialog('setTitle', '开箱作业');
	$('#createWorkForm').form('clear');
	url = 'createWork/';
}
function saveWork(){
	$('#createWorkForm').form({
		url: url,
		queryParams: {
			csrfmiddlewaretoken: getCookie('csrftoken'),
			operator: $('#operator').val(),
		},
		onSubmit: function(param){
			return $(this).form('validate');
		},
		success: function(result){
			var result = eval('('+result+')');
			if (!result.success){
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
				$('#createWorkDlg').dialog('close');        // 关闭对话框
				$('#workSpaceTree').tree('reload');         // 重载作业数据
			}
		}
	});
	
	$('#createWorkForm').submit();
}

function deleteWork(){
	var node = $('#workSpaceTree').tree('getSelected');
	if (node != null){
		if (node.attributes.isBox){
			$.messager.confirm('提示','是否确定删除'+node.text+'作业？',function(r){
				if (r){
					eval('clearTimer'+node.id+'()');
					$.post('deleteWork/', {boxNumber:node.id}, function(result){
						if (result.success){
							$('#workSpaceTree').tree('reload');    // 重载作业数据
							$.messager.show({    // 显示成功信息
								title: '提示',
								msg: result.message,
								showType: 'slide',
								timeout: 5000
							});
							$('#tbs').tabs('close', node.text);   // 关闭相应TAB
						} else {
							$.messager.alert({    // 显示失败信息
								title: '提示',
								msg: result.message
							});
						}
					}, 'json');
				}
			});
		}
		else{
			$.messager.alert('提示', '未选中作业！请选择！');
		}
	}
	else {
		$.messager.alert('提示', '请先开箱作业！');
	}
}

function archiveWork(){
	var node = $('#workSpaceTree').tree('getSelected');
	if (node != null){
		if (node.attributes.isBox){
			$.post('getWorkStatus/',
				{boxNumber: node.id},
				function(data, status){
						if (data.workStatus == 0){
							$.messager.confirm('提示', node.text+'作业尚未完成，是否确定归档？', function(r){
								if (r){		// 作业未完成情况下，确认归档
									eval('clearTimer'+node.id+'()');
									$.post('archiveWork/',
										{boxNumber: node.id},
										function(result){
											if (result.success){
												$.messager.show({    // 显示成功信息
													title: '提示',
													msg: result.message,
													showType: 'slide',
													timeout: 5000
												});
												$('#workSpaceTree').tree('reload');    // 重载作业数据
												$('#tbs').tabs('close', node.text);   // 关闭相应TAB
											}
											else{
												$.messager.show({    // 显示失败信息
													title: '提示',
													msg: result.message,
												});
											}
										}, 'json');
								}
							});
						}
						else{
							eval('clearTimer'+node.id+'()');
							$.post('archiveWork/',
							{boxNumber: node.id},
							function(result){
								if (result.success){
									$.messager.show({    // 显示成功信息
										title: '提示',
										msg: result.message,
										showType: 'slide',
										timeout: 5000
									});
									$('#workSpaceTree').tree('reload');    // 重载作业数据
									$('#tbs').tabs('close', node.text);   // 关闭相应TAB
								}
								else{
									$.messager.show({    // 显示失败信息
										title: '提示',
										msg: result.message,
									});
								}
							}, 'json');
						}
				}, 'json');
		}
	}
	else {
		$.messager.alert('提示', '请先开箱作业！');
	}
}

function outputConfig(){
	var node = $('#workSpaceTree').tree('getSelected');
	if (node != null){
		if (node.attributes.isBox){
			$.post('getWorkStatus/',
				{boxNumber: node.id},
				function(data, status){
					if (data.workStatus == 0){
						$.messager.confirm('提示', node.text+'作业尚未完成，是否确定生成信息档案？', function(r){
							if (r){ 	// 作业未完成情况下，确认生成信息档案
								$('#outputConfigDlg').dialog('open').dialog('center').dialog('setTitle', node.text+'信息档案生成');
								$('#outputConfigForm').form('clear');
								prepareDataForOutputConfig(node.id);
								url = 'outputWork/';						
							}
							else {
							}
						}); 
					}
					else{
						$('#outputConfigDlg').dialog('open').dialog('center').dialog('setTitle', node.text+'信息档案生成');
						$('#outputConfigForm').form('clear');
						prepareDataForOutputConfig(node.id);
						url = 'outputWork/';
					}
				}, 'json');
		}
		else{
			$.messager.alert('提示', '未选中作业！请先选中作业！');
		}
	}
	else{
		$.messager.alert('提示', '请先开箱作业！');
	}
}
function validateDate(fromDate, toDate){			// Month/Day/Year
	var fArray = fromDate.split('/')
	var tArray = toDate.split('/')
	
	if (fArray[2] > tArray[2]){
		return false;
	}
	
	if (fArray[2] == tArray[2] && fArray[0] > tArray[0]){
		return false;
	}
	
	if (fArray[2] == tArray[2] && fArray[0] == tArray[0] && fArray[1] == tArray[1]){
		return false;
	}
	
	return true;
}
function updateDate(date){
	var fromDate = $('#outputConfig-fromDate').datebox('getValue');
	var toDate = $('#outputConfig-toDate').datebox('getValue');
	
	if (!validateDate(fromDate, toDate)){
		$.messager.alert('提示', '起始日期一定要早于终止日期！ 请重新选择');
		
		return ;
	}
	
	$.ajax({url: 'getDurationCompleteThingAmount/',
		data: {boxNumber: boxNumber, fromDate: fromDate, toDate: toDate},
		type: 'Get',
		async: true,
		dataType: 'json',
		success: function(data, status){
			$('#outputConfig-completeAmount').textbox('setValue', data.amount)
		},
	});
}
function prepareDataForOutputConfig(boxNumber){
	$('#outputConfigForm').form('load', 'getOutputConfig/'+boxNumber);	
	var today = new Date();
	var fromDate = $('#outputConfig-fromDate').datebox('setValue', today.getMonth+'/'+today.getDate()+'/'+today.getFullYear()).datebox('getValue');
	var toDate = $('#outputConfig-toDate').datebox('setValue', today.getMonth+'/'+today.getDate()+'/'+today.getFullYear()).datebox('getValue');
	
	$.ajax({url: 'getDurationCompleteThingAmount/',
		data: {boxNumber: boxNumber, fromDate: fromDate, toDate: toDate},
		type: 'Get',
		async: true,
		dataType: 'json',
		success: function(data, status){
			$('#outputConfig-completeAmount').textbox('setValue', data.amount)
		},
	});
}
function outputWork(){
	var node = $('#workSpaceTree').tree('getSelected');
	var boxNumber = $('#outputConfig-boxNumber').val();
	var date = $('#outputConfig-date').datebox('getValue');	// get datebox value
	var seq = $('#outputConfig-sequence').val();
	$.ajax({url: url,
		data: {boxNumber: boxNumber, date: date, seq: seq},
		type: 'POST',
		async: true,
		dataType: 'json',
		beforeSend: function(xhr){
			$('#outputConfigDlg').dialog('close');        // 关闭对话框
			$.messager.progress({text:'正在导出'+node.text+'作业资料，请稍后....'});
		},
		success: function(data, status){
			$.messager.progress('close');
			if ('success' == status){
				var downloadURL = data.downloadURL;
				$.messager.alert('提示', node.text+'作业资料生成成功！\r\n请点击<a href="'+downloadURL+'">下载</a>');
			}
			else{
				$.messager.alert('提示', node.text+'作业资料生成失败！\n请重试，或者联系技术支持人员！');
			}
		},
	});
}

function printTag(){
	var node = $('#workSpaceTree').tree('getSelected');
	if (node != null){
		if (node.attributes.isBox){
			$.ajax({url: 'printTag/',
				data: {boxNumber: node.id},
				type: 'POST',
				async: true,
				dataType: 'json',
				beforeSend: function(xhr){
					$.messager.progress({text:'正在导出'+node.text+'作业标签，请稍后....'});
				},
				success: function(data, status){
					$.messager.progress('close');
					if ('success' == status){
						var downloadURL = data.downloadURL;
						$.messager.alert('提示', node.text+'作业标签生成成功！\r\n请点击<a href="'+downloadURL+'">下载</a>');
					}
					else{
						$.messager.alert('提示', node.text+'作业标签生成失败！\n请重试，或者联系技术支持人员！');
					}
				},
			});
		}
		else{
			$.messager.alert('提示', '未选中作业！请先选中作业！');
		}
	}
	else {
		$.messager.alert('提示', '请先开箱作业！');
	}
}

function outputAbstractConfig(){
	var node = $('#workSpaceTree').tree('getSelected');
	if (node != null){
		if (node.attributes.isBox){
			$.post('getWorkStatus/',
				{boxNumber: node.id},
				function(data, status){
					if (data.workStatus == 0){
						$.messager.confirm('提示', node.text+'作业尚未完成，是否确定生成装箱清单？', function(r){
							if (r){ 	// 作业未完成情况下，确认生成信息档案
								$('#outputAbstractConfigDlg').dialog('open').dialog('center').dialog('setTitle', node.text+'装箱清单生成');
								$('#outputAbstractConfigForm').form('clear');
								prepareDataForOutputAbstractConfig(node.id);
								url = 'outputWork/';						
							}
							else {
							}
						}); 
					}
					else{
						$('#outputAbstractConfigDlg').dialog('open').dialog('center').dialog('setTitle', node.text+'信息档案生成');
						$('#outputAbstractConfigForm').form('clear');
						prepareDataForOutputAbstractConfig(node.id);
						url = 'outputWork/';
					}
				}, 'json');
		}
		else{
			$.messager.alert('提示', '未选中作业！请先选中作业！');
		}
	}
	else{
		$.messager.alert('提示', '请先开箱作业！');
	}
}
function prepareDataForOutputAbstractConfig(boxNumber){
	$('#outputAbstractConfigForm').form('load', 'getOutputConfig/'+boxNumber);	
	var today = new Date();
	$('#outputAbstractConfig-date').datebox('setValue', today.getMonth+'/'+today.getDate()+'/'+today.getFullYear());
	var inc = 1;
	$('#outputAbstractConfig-sequence').spinner({
		value: '1',
		min: '1',
        increment: inc,
		editable: true,
		spin: function(down){
			var val = Number($('#outputAbstractConfig-sequence').spinner('getValue'));
			if (down){     // down
				if (val > 1){
					val = val-inc;
				}
			}
			else{
				val = val+inc;
			}
			$('#outputAbstractConfig-sequence').spinner('setValue', val);
		}
    });
}
function outputAbstract(){
	var node = $('#workSpaceTree').tree('getSelected');
	var boxNumber = $('#outputAbstractConfig-boxNumber').val();
	var date = $('#outputAbstractConfig-date').datebox('getValue');	// get datebox value
	var seq = $('#outputAbstractConfig-sequence').val();
	$.ajax({url: url,
		data: {boxNumber: boxNumber, date: date, seq: seq},
		type: 'POST',
		async: true,
		dataType: 'json',
		beforeSend: function(xhr){
			$('#outputAbstractConfigDlg').dialog('close');        // 关闭对话框
			$.messager.progress({text:'正在导出'+node.text+'装箱清单，请稍后....'});
		},
		success: function(data, status){
			$.messager.progress('close');
			if ('success' == status){
				var downloadURL = data.downloadURL;
				$.messager.alert('提示', node.text+'装箱清单生成成功！\r\n请点击<a href="'+downloadURL+'">下载</a>');
			}
			else{
				$.messager.alert('提示', node.text+'装箱清单生成失败！\n请重试，或者联系技术支持人员！');
			}
		},
	});
}