var gui = require('nw.gui');
var win = gui.Window.get();
//window.resizeTo(window.screen.width,window.screen.height);
$(window).on('dragover', function (e) {
    e.preventDefault();
    e.originalEvent.dataTransfer.dropEffect = 'none';
});
$(window).on('drop', function (e) {
    e.preventDefault();
});


document.onselectstart = function () {
    return false;
}
document.oncontextmenu = function () {
    return false;
}
$("#container").html("");
//窗口最小化事件
function minimize(){
    win.minimize();
    isShowWindow = false;
    //win.hide();
}

//窗口最大化事件
function maxmize(){
    win.maximize();
    isShowWindow = true;
}

//窗口从最大化状态重置到之前的状态时触发的事件
function unmaximize(){
    win.unmaximize();
    isShowWindow = true;
}

//当窗口从最小化重置到上一状态时触发的事件。
function restore(){
    win.restore();
}

//关闭
function close(){
   win.hide();
    //win.close();
}

//窗口隐藏
function hide(){
    win.hide();

}

//窗口显示
function show(){
    win.show();
}


