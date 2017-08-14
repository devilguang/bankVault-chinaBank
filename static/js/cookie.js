var username = $("#username");
var password = $("#password");
// 保存cookie
function setCookie(username, value, expires) {
    // 设置过期时间
    var newDate = new Date();
    newDate.setDate(newDate.getDate() + expires);

    document.cookie = username + "=" + value + (expires == undefined ? ";" : ";expires = " + newDate.toUTCString());
}

setCookie("uName",username.val(),7);
setCookie("uPassword",password.val(),7);
// 获取cookie
function getCookie(username) {
    var arr = document.cookie.split("; ");
    for (var i = 0; i < arr.length; i++) {
        var item = arr[i].split("=");
        if (item[0] == username) {
            return item[1];
        }
    }
}

// 删除cookie
function removeCookie(username) {
    setCookie(username, "", -1)
}
