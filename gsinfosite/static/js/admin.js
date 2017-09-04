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

function addTab(title, content, icon){
    if ($('#tbs').tabs('exists', title)){
        $('#tbs').tabs('select', title);
    } else {
        $('#tbs').tabs('add',{
            title:title,
            content:content,
            closable:true,
			iconCls:icon,
			border:false
        });
    }
}

function userManage(){
	var title = '用户管理11';
	var c = '<table id="workGridUser" class="easyui-datagrid" data-options="url:\'getUser/\', toolbar:\'#workGridToolBarUser\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20, checkOnSelect:false, selectOnCheck:false"><thead><tr><th field="checkStatus" align="center" checkbox="true"></th><th field="nickName" align="center" width="20">用户名</th><th field="type" formatter="userTypeFormatter" align="center" width="20">用户类型</th><th field="operation" formatter="operationFormatter" align="center" width="60">操作</th</tr></thead></table><div id="workGridToolBarUser"><a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="userAdd()">添加</a><a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="userRemove()">删除</a></div><script type="text/javascript">function initPagination(){$(\'#workGridUser\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
	addTab(title, c, 'icon-user');
	initPagination();
}
function userTypeFormatter(value, row, index){
	if (value == 0){
		return '超级管理员';
	}
	else if (value == 1){
		return '管理员';
	}else if (value == 2){
		return '一般用户';
	}
}
function operationFormatter(value, row, index){
    if(row.type == 1){
        return '<div style="float:left"><a href="javascript:void(0);" onclick="updatePassword(\''+row.nickName+'\')" style="text-decoration:none;color:blue">更改密码</a><a href="javascript:void(0);" onclick="transfer(\''+row.nickName+'\')" style="text-decoration:none;color:blue;margin-left: 40px;">转为超级管理员</a></div>'
    }else{
	    return '<div style="float:left"><a href="javascript:void(0);" onclick="updatePassword(\''+row.nickName+'\')" style="text-decoration:none;color:blue">更改密码</a></div>'
    }
}

function userAdd(){
	$('#userDlg').dialog('open').dialog('center').dialog('setTitle', '用户添加');
	$('#userForm').form('clear');
	url = 'userProcess/';
	opType = 'add';
}
function userRemove(){
	url = 'userProcess/';
	opType = 'remove';

	var rows = $('#workGridUser').datagrid('getChecked');
	var n = rows.length
	if (0 == n)
	{
		$.messager.alert('提示', '未选择记录! 请先选择一条用户记录！');
		return ;
	}

	var userArray = new Array()
	for (var i=0; i<n; ++i){
		userArray[i] = rows[i].nickName;
	}

	$.messager.confirm('提示', '是否确认删除所选用户?', function(r){
		if (r){
			$.ajax({url: url,
				data: {nickName: userArray, opType: opType},
				type: 'POST',
				async: true,
				dataType: 'json',
				success: function(result, status){
					if (result.success){
						$.messager.show({    // 显示成功信息
							title: '提示',
							msg: result.message,
							showType: 'slide',
							timeout: 5000
						});
						$('#workGridUser').datagrid('reload');		// 重载数据
					}
					else{
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
function saveUser(){
	$('#userForm').form({
		url: url,
		queryParams: {
			csrfmiddlewaretoken: getCookie('csrftoken'),
			opType: opType
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
				$('#userDlg').dialog('close');        		// 关闭对话框
				$('#workGridUser').datagrid('reload');		// 重载数据
			}
		}
	});

	$('#userForm').submit();
}
//将管理员转为超级管理员
function transfer(name){
	$.messager.confirm('提示', '是否赋予该用户超级管理员权限?', function(r){
		if (r){
			$.ajax({url: 'setSysAdmin/',
				data: {nickName: name},
				type: 'POST',
				async: true,
				dataType: 'json',
				success: function(result, status){
					if (result.success){
						$.messager.show({    // 显示成功信息
							title: '提示',
							msg: result.message,
							showType: 'slide',
							timeout: 5000
						});
						window.location.reload();
						//$('#workGridUser').datagrid('reload');		// 重载数据
					}
					else{
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
function updatePassword(nickName){	
	$('#updatePasswordDlg').dialog('open').dialog('center').dialog('setTitle', '更改密码');
	$('#updatePasswordForm').form('clear');
	$('#updatePasswordForm').form('load', {
		nickName: nickName,
	});
	url = 'updatePassword/';
}
function savePassword(){
	$('#updatePasswordForm').form({
		url: url,
		queryParams: {
			csrfmiddlewaretoken: getCookie('csrftoken'),
			fromLoc: 'admin'
		},
		onSubmit: function(param){
			var pwd = $('#updatePassword-password').textbox('getValue');
			var conf = $('#updatePassword-confirm').textbox('getValue');
			
			if (pwd == conf){
				return true;
			}
			else{
				$.messager.alert({    // 显示失败信息
					title: '提示',
					msg: '新密码与确认密码不一致！请重新填写！'
				});
				return false;
			}
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
				$('#updatePasswordDlg').dialog('close');        		// 关闭对话框
			}
		}
	});
	
	$('#updatePasswordForm').submit();
}

function authorityManage(){
	var title = '权限管理';
	var c = '<table id="workGridAuthority" class="easyui-datagrid" data-options="url:\'getAuthority/\', toolbar:\'#workGridToolBarAuthority\', singleSelect:true, fitColumns:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', pagination:true, fit:true, pageSize:20"><thead><tr><th align="center" rowspan="2" colspan="3" align="center">用户</th><th align="center" colspan="10">岗位权限&nbsp;&nbsp;(<img src="'+$('#okStatus').attr('value')+'">拥有权限</img>&nbsp;&nbsp;&nbsp;&nbsp;<img src="'+$('#noStatus').attr('value')+'">未拥有权限</img>)</th></tr><tr><th align="center" width="20" colspan="2">实物认定</th><th align="center" width="20" colspan="2">外观信息采集</th><th align="center" width="20" colspan="2">频谱分析</th><th align="center" width="20" colspan="2">测量称重</th><th align="center" width="20" colspan="2">图像采集</th></tr><tr><th field="nickName" align="center" width="10">用户名</th><th field="type" formatter="userTypeFormatter" align="center" width="10">用户类型</th><th field="manageAuthority" formatter="userOperationFormatter" align="center" width="20">操作</th><th field="checking" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="checkingAuthority" formatter="checkingAuthorityFormatter" align="center" width="10">操作</th><th field="numbering" formatter="authorityStatusFormatter"  align="center" width="10">状态</th><th field="numberingAuthority" formatter="numberingAuthorityFormatter" align="center" width="10">操作</th><th field="analyzing" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="analyzingAuthority" formatter="analyzingAuthorityFormatter" align="center" width="10">操作</th><th field="measuring" formatter="authorityStatusFormatter" align="center" width="10">状态</th><th field="measuringAuthority" formatter="measuringAuthorityFormatter" align="center" width="10">操作</th><th field="photographing" formatter="authorityStatusFormatter"  align="center" width="10">状态</th><th field="photographingAuthority" formatter="photographingAuthorityFormatter" align="center" width="10">操作</th></tr></thead></table><div id="workGridToolBarAuthority"><a href="#" class="easyui-linkbutton" iconCls="icon-reload" plain="true" onclick="javascript:$(\'#workGridAuthority\').datagrid(\'reload\')">刷新</a></div><script type="text/javascript">function initPagination(){$(\'#workGridAuthority\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
	addTab(title, c, 'icon-authority');
	initPagination();
}
function authorityStatusFormatter(value, row, index){
	if (!value){
		return '<img src="'+$('#noStatus').attr('value')+'"></img>';
	}else{
		return '<img src="'+$('#okStatus').attr('value')+'"></img>';
	}
}
function userOperationFormatter(value, row, index){
	if (1 >= row.type){
		// 只有管理员用户，才能作为现场负责人
		if (row.manage){
			return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'manage\', \'revoke\')">取消现场负责人</a>';
		}
		
		if (row.canBeManage){
			// 未设置现场负责人, 具备成为现场负责人的可能
			return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'manage\', \'grant\')">设置现场负责人</a>';
		}
		else{
			return '<span>-</span>';
		}
	}
	else{
		return '<span>-</span>';
	}
}
function checkingAuthorityFormatter(value, row, index){
	if (1 >= row.type){
		// 管理员用户，权限不可更改
		return '<span>-</span>';
	}
	if (row.checking){
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'checking\', \'revoke\')">取消</a>';
	}
	else{
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'checking\', \'grant\')">授权</a>';
	}
}
function numberingAuthorityFormatter(value, row, index){
	if (1 >= row.type){
		// 管理员用户，权限不可更改
		return '<span>-</span>';
	}
	if (row.numbering){
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'numbering\', \'revoke\')">取消</a>';
	}
	else{
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'numbering\', \'grant\')">授权</a>';
	}
}
function photographingAuthorityFormatter(value, row, index){
	if (1 >= row.type){
		// 管理员用户，权限不可更改
		return '<span>-</span>';
	}
	if (row.photographing){
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'photographing\', \'revoke\')">取消</a>';
	}
	else{
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'photographing\', \'grant\')">授权</a>';
	}
}
function analyzingAuthorityFormatter(value, row, index){
	if (1 >= row.type){
		// 管理员用户，权限不可更改
		return '<span>-</span>';
	}
	if (row.analyzing){
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'analyzing\', \'revoke\')">取消</a>';
	}
	else{
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'analyzing\', \'grant\')">授权</a>';
	}
}
function measuringAuthorityFormatter(value, row, index){
	if (1 >= row.type){
		// 管理员用户，权限不可更改
		return '<span>-</span>';
	}
	if (row.measuring){
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'measuring\', \'revoke\')">取消</a>';
	}
	else{
		return '<a href="#" style="text-decoration:none;color:blue" onclick="authorityProcess(\''+row.nickName+'\', \'measuring\', \'grant\')">授权</a>';
	}
}
function authorityProcess(nickName, authority, opType){
	$.post('authorityProcess/',
	{nickName: nickName, authority: authority, opType: opType},
	function(result, status){
		if (result.success){
			$.messager.show({    // 显示成功信息
				title: '提示',
				msg: result.message,
				showType: 'slide',
				timeout: 5000
			});
			$('#workGridAuthority').datagrid('reload');		// 重载数据
		}
		else{
			$.messager.show({    // 显示失败信息
				title: '提示',
				msg: result.message,
			});
		}
	}, 
	'json');
}

function propertyManage(){
	var title = '属性数据';
	var c = '<table id="workGridProperty" class="easyui-treegrid" data-options="url:\'getProperty/\', toolbar:\'#workGridToolBarProperty\', singleSelect:true, rownumbers:true, loadMsg:\'作业数据正在载入，请稍后...\', fit:true, idField: \'id\', treeField:\'type\', lines:true, onLoadSuccess:collapse"><thead><tr><th field="type" align="left" width="300">类型</th><th field="code" align="center" width="253" formatter="contentFormatter">编码</th><th field="remark" align="center" width="253" formatter="contentFormatter">备注</th></tr></thead></table><div id="workGridToolBarProperty"><a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="propertyAdd()">添加</a><a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="propertyRemove()">删除</a><a href="#" class="easyui-linkbutton" iconCls="icon-collapse" plain="true" onclick="collapse()">全部折叠</a><a href="#" class="easyui-linkbutton" iconCls="icon-expand" plain="true" onclick="expand()">全部打开</a></div><script type="text/javascript">function collapse(){ $(\'#workGridProperty\').treegrid(\'collapseAll\'); } function expand(){ $(\'#workGridProperty\').treegrid(\'expandAll\'); }</script>';
	addTab(title, c, 'icon-property');
}
function contentFormatter(value, row, index){
	if (value == ''){
		return '-';
	}
	else {
		return value;
	}
}

var url;
var opType;
function initPropertyDlg(){
	$('#step1').attr('style', '');
	$('#next').attr('style', '');
	$('#step2').attr('style', 'display:none');
	$('#prev').attr('style', 'display:none');
	$('#propertySave').attr('style', 'display:none');
	$('#cancel').attr('style', 'display:none');
}
function unInitPropertyDlg(){
	$('#step1').attr('style', '');
	$('#next').attr('style', '');
	$('#step2').attr('style', '');
	$('#prev').attr('style', '');
	$('#propertySave').attr('style', '');
	$('#cancel').attr('style', '');
}
function propertyAdd(){
	initPropertyDlg();
	
	$('#propertyDlg').dialog('open').dialog('center').dialog('setTitle', '属性添加');
	$('#propertyForm').form('clear');
	url = 'propertyProcess/';
	opType = 'add';
}
function propertyRemove(){
	url = 'propertyProcess/';
	opType = 'remove';
	
	var curNode = $('#workGridProperty').treegrid('getSelected');
	if (!curNode)
	{
		$.messager.alert('提示', '未选择记录! 请先选择一条属性记录！');
		return ;
	}
	
	$.messager.confirm('提示', '是否确认删除此条属性?', function(r){
		if (r){
			$.post(url,
				{id: curNode.id, opType: opType},
				function(result, status){
					if (result.success){
						$.messager.show({    // 显示成功信息
							title: '提示',
							msg: result.message,
							showType: 'slide',
							timeout: 5000
						});
						$('#workGridProperty').treegrid('reload');		// 重载数据
					}
					else{
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
function saveProperty(){
	var project = $('#property-project').combobox('getValue');
	if (project == '实物类型'){
		var productType = $('#property-productType-productType').textbox('getValue');
		var productTypeCode = $('#property-productTypeCode').textbox('getValue');
		if (productType == '' || productTypeCode == ''){
			$.messager.alert({
				title: '提示',
				msg: '实物类型或实物编码不能为空！'
			});
		}			
	}
	else if (project == '品名'){
		var productType = $('#property-className-productType').combobox('getValue');
		var className = $('#property-className-className').textbox('getValue');
		var classNameCode = $('#property-classNameCode').textbox('getValue');	
		if (productType == '' || className == '' || classNameCode == ''){
			$.messager.alert({
				title: '提示',
				msg: '实物类型、品名名称或品名编码不能为空！'
			});
		}
	}
	else if (project == '明细品名'){
		var productType = $('#property-subClassName-productType').combobox('getValue');
		var className = $('#property-subClassName-className').combobox('getValue');
		var subClassName = $('#property-subClassName-subClassName').textbox('getValue');
		var subClassNameCode = $('#property-subClassNameCode').textbox('getValue');
		if (productType == '' || className == '' || subClassName == '' || subClassNameCode == ''){
			$.messager.alert({
				title: '提示',
				msg: '实物类型、品名名称、明细品名或明细品名编码不能为空！'
			});
		}
	}
	else if (project == '发行库'){
		var wareHouseType = $('#property-wareHouseType').textbox('getValue');
		var wareHouseCode = $('#property-wareHouseCode').textbox('getValue');
		if (wareHouseType == '' || wareHouseCode == ''){
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
				$('#propertyDlg').dialog('close');        		// 关闭对话框
				$('#workGridProperty').treegrid('reload');		// 重载数据
			}
		}
	});
	
	$('#propertyForm').submit();
}

function next(){
	var project = $('#property-project').combobox('getValue');
	
	if (project != ''){
		$('#step1').attr('style', 'display:none');
		$('#next').attr('style', 'display:none');
		$('#step2').attr('style', '');
		$('#prev').attr('style', '');
		$('#propertySave').attr('style', '');
		$('#cancel').attr('style', '');
		
		if (project == '实物类型'){
			$('#productType').attr('style', '');
			$('#className').attr('style', 'display:none');
			$('#subClassName').attr('style', 'display:none');
			$('#wareHouse').attr('style', 'display:none');
		}
		else if (project == '品名'){
			$('#property-className-productType').combobox('reload');
			$('#productType').attr('style', 'display:none');
			$('#className').attr('style', '');
			$('#subClassName').attr('style', 'display:none');
			$('#wareHouse').attr('style', 'display:none');
		}
		else if (project == '明细品名'){
			$('#property-subClassName-productType').combobox('reload');
			$('#property-subClassName-className').combobox('reload');
			$('#productType').attr('style', 'display:none');
			$('#className').attr('style', 'display:none');
			$('#subClassName').attr('style', '');
			$('#wareHouse').attr('style', 'display:none');
		}
		else if (project == '发行库'){
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

function prev(){
	$('#step1').attr('style', '');
	$('#next').attr('style', '');
	$('#step2').attr('style', 'display:none');
	$('#prev').attr('style', 'display:none');
	$('#propertySave').attr('style', 'display:none');
	$('#cancel').attr('style', 'display:none');
}

function searchArchive(){
	var title = '档案查询';
	var c = '<div class="easyui-layout" data-options="fit:true"><div data-options="region:\'center\'"><table id="archiveGrid" class="easyui-datagrid" data-options="url:\'getArchive/\', border:false, rownumbers:true, fitcolumns:true, fit:true, pagination:true, pagsize:10"><thead><tr><th field="boxNumber" align="center" width="50">箱号</th><th field="productType" align="center" width="150">实物类型</th><th field="amount" align="center" width="150">数量</th><th field="archiveUrl" align="center" formatter="archiveBoxFormatter" width="430">资料</th></tr></thead></table></div></div><script type="text/javascript">$(function(){ $(\'#archiveGrid\').datagrid({ view: detailview, detailFormatter:function(index,row){ return \'<div style="padding:2px"><table class="ddv"></table></div>\';}, onExpandRow: function(index,row){ var ddv = $(this).datagrid(\'getRowDetail\',index).find(\'table.ddv\'); ddv.datagrid({url:\'getWorkData/\'+row.boxNumber, fitColumns:true, singleSelect:true, rownumbers:true, loadMsg:\'\', height:\'auto\', pagination:true, pageSize:10, queryParams:{processId:-1}, columns:[[{field:\'serialNumber\',title:\'编号\',width:100,align:\'center\'},{field:\'boxNumber\',title:\'箱号\',width:50,align:\'center\'},{field:\'className\',title:\'品名\',width:50,align:\'center\'},{field:\'subClassName\',title:\'明细品名\',width:100,align:\'center\'},{field:\'archive\',title:\'资料\',width:250,align:\'center\', formatter:archiveThingFormatter}]],onResize:function(){$(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);},onLoadSuccess:function(){setTimeout(function(){$(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);},0);}}); ddv.datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'}); $(\'#archiveGrid\').datagrid(\'fixDetailRowHeight\',index);}});}); function initPagination(){$(\'#archiveGrid\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
	addTab(title, c, 'icon-archive');
	initPagination();
}
function archiveBoxFormatter(value, row, index){
	return '<div style="float:left"><a href="getWork/'+row.boxNumber+'" style="text-decoration:none;color:blue;margin-right:20px">档案下载</a><a href="getTag/'+row.boxNumber+'" style="text-decoration:none;color:blue;margin-right:20px">标签下载</a><a href="javascript:void(0);" onclick="backToWork(\''+row.boxNumber+'\')" style="text-decoration:none;color:blue;margin-right:20px">退回作业</a></div>';
}
function archiveThingFormatter(value, row, index){
	return '<div style="float:left"><a href="getThing/'+row.boxNumber+'/'+row.serialNumber+'" style="text-decoration:none;color:blue;margin-right:20px">信息档案下载</a><a href="exploreThing/'+row.boxNumber+'/'+row.serialNumber+'" target="blank" style="text-decoration:none;color:blue;margin-right:20px">电子档案查看</a></div>';
}

function backToWork(boxNumber){
	$.post('backToWork/',
				{boxNumber: boxNumber},
				function(result, status){
					if (result.success){
						$.messager.show({    // 显示成功信息
							title: '提示',
							msg: result.message,
							showType: 'slide',
							timeout: 5000
						});
						$('#archiveGrid').datagrid('reload');		// 重载数据
					}
					else{
						$.messager.show({    // 显示失败信息
							title: '提示',
							msg: result.message,
						});
					}
				}, 
	'json');
}

function searchWork(){
	var title = '作业查询';
	var c = '<div class="easyui-layout" data-options="fit:true"><div data-options="region:\'center\'"><table id="workGrid" class="easyui-datagrid" data-options="url:\'getWorkContent/\', border:false, rownumbers:true, fitcolumns:true, fit:true, pagination:true, pagsize:10"><thead><tr><th field="boxNumber" align="center" width="50">箱号</th><th field="productType" align="center" width="150">实物类型</th><th field="amount" align="center" width="150">数量</th><th field="archiveUrl" align="center" formatter="workBoxFormatter" width="430">资料</th></tr></thead></table></div></div><script type="text/javascript">$(function(){ $(\'#workGrid\').datagrid({ view: detailview, detailFormatter:function(index,row){ return \'<div style="padding:2px"><table class="ddv"></table></div>\';}, onExpandRow: function(index,row){ var ddv = $(this).datagrid(\'getRowDetail\',index).find(\'table.ddv\'); ddv.datagrid({url:\'getWorkData/\'+row.boxNumber, fitColumns:true, singleSelect:true, rownumbers:true, loadMsg:\'\', height:\'auto\', pagination:true, pageSize:10, queryParams:{processId:-1}, columns:[[{field:\'serialNumber\',title:\'编号\',width:100,align:\'center\'},{field:\'boxNumber\',title:\'箱号\',width:50,align:\'center\'},{field:\'className\',title:\'品名\',width:50,align:\'center\'},{field:\'subClassName\',title:\'明细品名\',width:100,align:\'center\'},{field:\'archive\',title:\'资料\',width:250,align:\'center\', formatter:workThingFormatter}]],onResize:function(){$(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);},onLoadSuccess:function(){setTimeout(function(){$(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);},0);}}); ddv.datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'}); $(\'#workGrid\').datagrid(\'fixDetailRowHeight\',index);}});}); function initPagination(){$(\'#workGrid\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
	addTab(title, c, 'icon-archive');
	initPagination();
}
function workBoxFormatter(value, row, index){
	return '<div style="float:left"><a href="getWork/'+row.boxNumber+'" style="text-decoration:none;color:blue;margin-right:20px">档案下载</a><a href="getTag/'+row.boxNumber+'" style="text-decoration:none;color:blue;margin-right:20px">标签下载</a></div>';
}
function workThingFormatter(value, row, index){
	return '<div style="float:left"><a href="getThing/'+row.boxNumber+'/'+row.serialNumber+'" style="text-decoration:none;color:blue;margin-right:20px">信息档案下载</a><a href="exploreThing/'+row.boxNumber+'/'+row.serialNumber+'" target="blank" style="text-decoration:none;color:blue;margin-right:20px">电子档案查看</a></div>';
}

function searchLog(){
	var title = '日志';
	var c = '<div class="easyui-layout" data-options="fit:true"><div data-options="region:\'north\'" height="10%"><form id="LogSearchParameter" style="display:inline-block;margin-top:12px;"><div style="display:inline;margin-left:10px;margin-right:15px;"><label style="margin-right:5px">用户</label><input id="userName" class="easyui-combobox" name="userName" data-options="valueField: \'id\', textField: \'text\', url: \'getUserName/\', editable: false, panelHeight: \'auto\'"/></div><div style="display:inline;margin-right:15px;"><label style="margin-right:5px;">操作类型</label><input id="operationType" class="easyui-combobox" name="operationType" data-options="method:\'GET\', url:\'getOperationType/\', valueField: \'id\', textField: \'text\', editable: false, panelHeight: \'auto\'"/></div></form><div style="display:inline;margin-right:15px;"><a href="javascript:void(0)" class="easyui-linkbutton" onclick="LogSearch()" style="width:60px;margin-right:10px;">查询</a><a href="javascript:void(0)" class="easyui-linkbutton" onclick="LogSearchReset()" style="width:60px;margin-right:10px;">重置</a></div></div><div data-options="region:\'center\'"><table id="LogGrid" class="easyui-datagrid" data-options="method:\'GET\', url:\'getLogContent/\', border:false, rownumbers:true, fitcolumns:true, fit:true, pagination:true, pagsize:10"><thead><tr><th field="userID" align="center" width="70">用户ID</th><th field="userName" align="center" width="100">用户姓名</th><th field="when" align="center" width="150">时间</th><th field="operationType" align="center" width="100">操作类型</th><th field="content" align="center" width="200">内容</th></tr></thead></table></div></div><script type="text/javascript">function initPagination(){$(\'#LogGrid\').datagrid(\'getPager\').pagination({layout:[\'prev\', \'sep\', \'links\', \'sep\', \'next\'], displayMsg:\'当前显示第 {from} 条到第 {to} 条记录 共 {total} 条记录\'});}</script>';
	addTab(title, c, 'icon-archive');
	initPagination();
}
function LogSearch(){
	var userName = $('#userName').combobox('getText');
	var operationType = $('#operationType').combobox('getText');

	if (userName == '' && operationType == ''){
		$.messager.alert('提示', '请至少选择一项查询条件!');

		return ;
	}

	$('#LogGrid').datagrid({
		queryParams: {
			userName: userName,
			operationType: operationType,
		}
	});
	initPagination();								// 设定翻页插件
	// $('#LogGrid').datagrid('reload');		        // 重载数据
}
function LogSearchReset(){
	$('#userName').combobox('setValue', '0');
	$('#operationType').combobox('setValue', '0');

	var userName = $('#userName').combobox('getText');
	var operationType = $('#operationType').combobox('getText');
	$('#LogGrid').datagrid({
		queryParams: {
			userName: userName,
			operationType: operationType,
		}
	});
	initPagination();								// 设定翻页插件
	$('#LogGrid').datagrid('reload');		        // 重载数据
}