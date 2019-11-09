/**
 * 2016年1月11日
 * 重新封装canvas画图类
 * 将定义统一的放在一起
 */

/**
 * 第一部分，常量定义
 * @type {number}
 */
var maximizeState = 0;  //窗口最大化状态,默认为0,若最大化按钮被点击的话,这个参数将变为1。再次点击则变为0
var sourceCanvasSize = {width: 0, height: 0};  //定义画布的大小
//var arrowyheight = 0;  // arrow offset 
var _sourceCanvas = null; //源图像所在画布
var _tempsourceContext = null; //剪切板复制源画像画布上下文内容
var _sourceContext = null; //源图像画布上下文内容
var _textCanvas = null; //文本画布
var _textContext = null; //文本画布上下文内容
var _drawCanvas = null; //画图画布（目前主要支持矩形等图形）
var _drawContext = null; //画图画布上下文内容
var _paint = false; //是否可以画
var _drawMode = ""; //操作类型
var _color = "#fa7c44"; //颜色
var fontcolor = "#fa7c44";
var isReDrawFlag = false;
var _lineWidth = 1;  //铅笔线宽
var _brushWidth = 15; 	//画刷线宽
var _eraserWidth = 20;	//橡皮擦大小
var _fill = false; //是否填充
var _backgroundColor = "#FFFFCC"; //橡皮擦色值
var sizeIndex = 0;
var fontSize = 22;
var _lineObj = null;
var _eraserObj = null;
var _syncEraserObj = null;
var _syncLineObj = null;  //同步
var _syncSquareObj = null;
var _syncCircleObj = null;
var _syncArrowObj = null;
var _syncLineObj = null;
var _syncTextObj = null;
var isSaveImage = false;
var _drawCache = new Array();   //画图缓存
var _redoCache = new Array();   //恢复操作
var clientWidth;
var clientHeight;
var canWidth = '0px', canHeight = '0px';
var map = new Map();  //回滚使用
var imgUrl = null;
var is_clipboard_true = 1;  //剪切板状态
var is_clipboard_false = 0;  //非剪切板
var is_clipboard_status = 0;	
var img = null;
var loading = false;
var tempPage = "";

var reSizeTimeId = null;

// Load native UI library.
var gui = require('nw.gui');
var win = gui.Window.get();



var _Isreset=false;
// We can not create a clipboard, we have to receive the system clipboard
var isShowWindow = true;
var FULLSCREEN = "0";
var WINDOW = "1";
var AREA = "2";
var spawn = require('child_process').spawn;
var exec = require('child_process').exec;
var fs = require('fs');

/*  var tray = new gui.Tray({title: '放德截图', icon: 'img/logo.png'});

    tray.tooltip = '点此打开';
    isShowWindow = true;*/
    //添加一个菜单
//    var menu = new gui.Menu();
//    menu.append(new gui.MenuItem({type: 'checkbox', label: '选择我'}));
//    tray.menu = menu;
    //click事件
   /* tray.on('click',
            function () {
		if(is_clipboard_status == 1){
			is_clipboard_status = 0;
			show();
			return;
		}

                if (isShowWindow) {
                    win.minimize();
                    isShowWindow = false;
                }
                else {	
                    win.unmaximize();
                    isShowWindow = true;
                    exec("wmctrl -a 方德截图 && wmctrl -r 方德截图 -b add,maximized_vert,maximized_horz", function (err, stdout, stderr) {
                        console.log(stdout);
                    });
//                }
                }
            }
    );
*/

function delay(obj, obj2, obj3) {
    var python = spawn('python', ['nfs_python/nfs_timecount.py', obj]);
    python.stdout.on('data', function (data) {
        if (data.toString() != "") {
            if (obj2 == 'screenorwindow') {
                setTimeout(function(){
                    captureFullScreenOrWindow(obj3,is_clipboard_false);
                },200);
            } else {
                setTimeout(function(){
                    captureFree(AREA);
                },200);
            }
        }
    });
}


//截取全屏
function captureFullScreenOrWindow(obj,clipboard_flag) {
    resetCanvas();
    var python = spawn('sh', ['/usr/bin/action',obj,clipboard_flag]);
     	
    python.stdout.on('data', function (data) {
        //过滤data数据
        urlData = data.toString();
	loagImage(urlData);
    });

    python.stderr.on('data', function (data) {
	if(!data.toString().indexOf('WARNING')){
			show();
	} 
    });
}

//剪切板
function captureclipboard(obj) {
    is_clipboard_status = 1;
    hide();
    var python = spawn('sh', ['/usr/bin/action', obj,is_clipboard_true]);
    python.stdout.on('data', function (data) {
        //show();
    });

    python.stderr.on('data', function (data) {
	//if(!data.toString().indexOf('WARNING')){
	//		show();
	//} 
    });
}


function captureFree(obj) {
    resetCanvas();
    var python = "";
    if(obj == "clipboard"){
	 python = spawn('sh', ['/usr/bin/action',obj,is_clipboard_true]);
    }else{
	 python = spawn('sh', ['/usr/bin/action',obj,is_clipboard_false]);
    }	
    
    python.stdout.on('data', function (data) {
        //过滤data数据
	if(!(obj == "clipboard")){
		urlData = data.toString();
		if(urlData.trim() == ""){
		/*var result="";
		$.MessageBox({
					title:'警告',
					content:'无法截图图像,所有可行的方法均已失效!',
					type:'information',background:'white',
					buttons:{confirm:{title:'确定',style:'continue'}},
					userkey:true

						},function(response)
						{
							return;
						});
		show();*/
			captureFullScreenOrWindow(FULLSCREEN,is_clipboard_false);

			}else{
			loagImage(urlData);
		}
	}else{
		 show();
	}
    });


    python.stderr.on('data', function (data) {
        if(!(obj == "clipboard")){
		if(!data.toString().indexOf('WARNING')){
			show();
		}		
        }

    });
}

//function showFree(obj){
//    var command = 'xsel -b -c';
//    exec(command, function (err, stdout) {
//       loagImage(obj);
//       show();
//    });
//}




$(document).ready(function () {
     //win.maximize();
   	
     isCheck_PirntDir();
     $("#commitBtn").click(function () {

        var words = $(".text_box").val();
        if (words != "") {
            isReDrawFlag = true;
            $(this).attr("disabled", true); 
        } 
	_drawCanvas.style.zIndex = -1;
    });

    $("#cancelBtn").click(function () {
        $(".text_box").val("");
        $(".font").hide();
        $("#commitBtn").attr("disabled", false);
        isReDrawFlag = false;
    });    


     //文字颜色选择
    $("#fontColor>li").click(function () {
        $(this).css("border", "1px solid #68777a");
        $(this).siblings().css("border", "");
        var colorTemp = $(this).css("background-color");
        fontcolor = colorTemp;
        $("#tt").css("color",fontcolor);
        $("#tt").focus();
    });

    //窗口监听事件
    win.on('resize', function () {
        //maxmize();
	    //var height= $(window).height() - 120;
	    var height = $(window).height()  - ($(".top_main").height() + $(".bottom_main").height());

	    var width = $(window).width() - $(".center_left").width();
	    $(".center_left").css("height", height);
	            $(".center_right").css({"height": height, "width": width});
	    
	    reSizeTimeId = setTimeout(resizeDiv, 50);


    });

    //---------------------添加快捷键------------------------
    var option = {
        key: "Ctrl+Alt+A",
        active: function () {
            restore();
            setTimeout(function () {
                $(".free_a").trigger("click");
            }, 500);

        },
        failed: function (msg) {
            console.log(msg);
        }
    };

    var shortcut = new gui.Shortcut(option);


    var option2 = {
        key: "Ctrl+Alt+Q",
        active: function () {
            restore();
            setTimeout(function () {
                $(".top_button_left .full_a").trigger("click");
            }, 500);

        },
        failed: function (msg) {
            console.log(msg);
        }
    };

    var shortcut2 = new gui.Shortcut(option2);

    var option3 = {
        key: "Ctrl+Alt+W",
        active: function () {
            restore();
            setTimeout(function () {
                $(".window_a").trigger("click");
            }, 500);

        },
        failed: function (msg) {
            // :(, fail to register the |key| or couldn't parse the |key|.
            console.log(msg);
        }
    };

    var shortcut3 = new gui.Shortcut(option3);

    var option4 = {
        key:"Ctrl+Alt+Z",
        active:function(){
            undo();
        },
        failed:function(msg){
            console.log(msg);
        }
    }

    var shortcut4 = new gui.Shortcut(option4);

   /* var option5 = {
        key:"Alt+R",
        active:function(){
	    restore();
            //调用截图到剪切板
            setTimeout(function () {
                captureclipboard(FULLSCREEN);
            }, 500);

        },
        failed:function(msg){
            console.log(msg);
        }
    }

    var shortcut5 = new gui.Shortcut(option5);

    var option6 = {
        key:"Alt+T",
        active:function(){
            restore();
            //调用截图到剪切板
            setTimeout(function () {
                captureclipboard(WINDOW);
            }, 500);

        },
        failed:function(msg){
            console.log(msg);
        }
    }

    var shortcut6 = new gui.Shortcut(option6);

    var option7 = {
        key:"Alt+Y",
        active:function(){
	    restore();
            //调用截图到剪切板
            setTimeout(function () {
		captureclipboard("free");
            }, 500);

        },
        failed:function(msg){
            console.log(msg);
        }
    }

    var shortcut7 = new gui.Shortcut(option7);
*/

    gui.App.registerGlobalHotKey(shortcut);
    gui.App.registerGlobalHotKey(shortcut2);
    gui.App.registerGlobalHotKey(shortcut3);
    gui.App.registerGlobalHotKey(shortcut4);
 //   gui.App.registerGlobalHotKey(shortcut5);
 //   gui.App.registerGlobalHotKey(shortcut6);
 //   gui.App.registerGlobalHotKey(shortcut7);
    //--------------------截图操作--------------------------
    //最小化按钮点击事件
    $(".little_a").click(function () {
        minimize();
    });

    //最大化按钮点击事件
    $(".middle_a").click(function () {
        if (maximizeState == 0) {
            maxmize();
	    var img=document.getElementById("middle_a_id");
            img.style.backgroundImage="url(img/middle_restore.png)";
            $(".middle_a:hover").css("background","url(img/middle_restore_hover.png)");
            maximizeState = 1;
        } else {
            unmaximize();
	    var img=document.getElementById("middle_a_id");
            img.style.backgroundImage="url(img/middle.png)";
	    $(".middle_a:hover").css("background","url(img/middle_hover.png)");

            maximizeState = 0;
        }
    });

    //关闭按钮点击事件
    $(".close_a").click(function () {
	    if(!_sourceCanvas)
               win.close();
	    if(_Isreset || !isSaveImage)
      // 	_Isreset && !isSaveImage
        {
               $.MessageBox({
                              title: '警告',
                              content: '图片未保存，是否退出',
                              type: 'confirmation', background: 'write',
                              buttons: { cancel: {title: '确定', style: 'cancel' },confirm:{title: '取消', style: 'continue'} },
                              usekey: true
                              },function(response) {
                                                        if(! response)
                                                         {
                                                             gui.App.unregisterGlobalHotKey(shortcut);
                                                             gui.App.unregisterGlobalHotKey(shortcut2);
                                                             gui.App.unregisterGlobalHotKey(shortcut3);
                                                             gui.App.unregisterGlobalHotKey(shortcut4);
							     win.close();
							  }
                                                          });


            }

	else
	{

        gui.App.unregisterGlobalHotKey(shortcut);
        gui.App.unregisterGlobalHotKey(shortcut2);
        gui.App.unregisterGlobalHotKey(shortcut3);
        gui.App.unregisterGlobalHotKey(shortcut4);
//        gui.App.unregisterGlobalHotKey(shortcut5);
//        gui.App.unregisterGlobalHotKey(shortcut6);
//        gui.App.unregisterGlobalHotKey(shortcut7);
        win.close();
	}
    });

    //全屏截图，实现通过调用底层python脚本实现
    $(".top_button_left .full_a").click(function (e) {

        hide();

        var t = parseInt($('#time').val());
        if (t > 0) {
            delay(t, "screenorwindow", FULLSCREEN,is_clipboard_false);
        } else {
            setTimeout(function(){
                captureFullScreenOrWindow(FULLSCREEN,is_clipboard_false);
            },500);
        }
    });




    //截取当前活动窗口
    $(".window_a").click(function (e) {
        hide();

        var t = parseInt($('#time').val());
        if (t > 0) {
            delay(t, "screenorwindow", WINDOW,is_clipboard_false);
        } else {
            setTimeout(function(){
                captureFullScreenOrWindow(WINDOW,is_clipboard_false);
            },500);

        }
    });


    //自由截图
    $(".free_a").click(function (e) {

        hide();

        var t = parseInt($('#time').val());
        if (t > 0) {
            delay(t, "area", "");
        } else {
          //  setTimeout(function(){
                captureFree(AREA);
            // },500);

        }
    });



    //-----------------------------------------------

    //改变绘图工具菜单栏
    $(".center_left > li ").click(function () {
        var _index = $(this).index();
        switch (_index) {
            case 0:
                _drawMode = 'rect';
                $(".line04 > img").attr("src", "img/line05.png");
                $(".line04 > img").show();
		$('.font').hide();
                break;
            case 1:
                _drawMode = 'ellipse';
                $(".line04 > img").attr("src", "img/line04.png");
                $(".line04 > img").show();
		$('.font').hide();
                break;
            case 2:
                _drawMode = 'arrow';
                $(".line04 > img").hide();
		$('.font').hide();
                break;
            case 3:
                _drawMode = "pencil";
                $(".line04 > img").hide();
		$('.font').hide();
                break;
            case 4:
                //回滚操作
		$('.font').hide();
		undo();
                break;
            case 5:
                _drawMode = "text";
                $(".line04 > img").hide();
		if (_sourceCanvas != undefined) {
			$('.font').show();
			if(_textCanvas!=undefined){
               			 _textCanvas.fontSize = fontSize+"px";
           		}
			$("#tt").css({'font-size':fontSize+"px",'color':fontcolor});
			$(".text_box").focus();
		}
                break;
            case 6:
                _drawMode = "eraser";
                $(".line04 > img").hide();
		$('.font').hide();
                break;
        }
        $(this).addClass("press");
        $(this).siblings().removeClass("press");
        changeIndex();
        changeEvent();
    });
	
  

    //保存图片
    $("#saveImage").click(function (e) {
        if (!isSaveImage) {
            if (_sourceCanvas != undefined) {
		$("#cancelBtn").trigger("click");
		isSaveImage =true;
		_sourceContext.drawImage(_textCanvas,0,0);
		_sourceCanvas.style.zIndex = 1;   //测试
	        var base64Data = _sourceCanvas.toDataURL().replace(/^data:image\/\w+;base64,/, "");
		saveImage(base64Data);
		_Isreset = false;
            }
        }

    });


    $("#clipboardImage").click(function (e) {

        if (_sourceCanvas != undefined)
	{
	    $("#cancelBtn").trigger("click");
            _tempsourceContext.drawImage(_textCanvas,0,0);

	    var tempsourceCanvas = _sourceCanvas
	    var base64Data = tempsourceCanvas.toDataURL().replace(/^data:image\/\w+;base64,/, "");
            saveTempImage(base64Data);
            
	    var python = require('child_process').spawn('python', ['nfs_python/nfs_clipboard.py', encodeURI(tempPage) ]);
	    python.stdout.on('data', function (data) {
		if(data!=null && data.toString().trim() != "" ){
                
		}else{

		}
	    });

	    python.stderr.on('data', function (data) {
	    });
	}

    });


    $("#clearImage").click(function (e) {

            $('#container').html("");

            _sourceCanvas = undefined;
            _sourceContext = undefined;
	    _tempsourceContext = undefined;
            _drawCanvas = undefined;
            _drawContext = undefined;
            _textCanvas = undefined;
            _textContext = undefined;
            isSaveImage = false;
            //清空数组内容
            map.clear();
    });



    function resizeDiv()
    {
	var height = $(window).height()  - ($(".top_main").height() + $(".bottom_main").height());

        var width = $(window).width() - $(".center_left").width();
	$(".center_left").css("height", height);
	$(".center_right").css({"height": height, "width": width});
	clearTimeout(reSizeTimeId);

    }

    function saveTempImage(str)
    {
        var dataBuffer = new Buffer(str, 'base64');
	var imgUrlTemp = imgUrl.replace(new RegExp('\n', 'g'),'');
	var filePath = imgUrlTemp.substr(0,imgUrlTemp.lastIndexOf('/')) + '/out.png';
	tempPage = filePath ;
	fs.writeFile(filePath, dataBuffer, function (err)
	{
	    if (err) {
		console.log(err.message);
	    }
	    else {
	    }
	});
    }


    function saveImage(str) {
        var dataBuffer = new Buffer(str, 'base64');
        var imgUrlTemp = imgUrl.replace(new RegExp('\n', 'g'),'');
        var filePath = imgUrlTemp.substr(0,imgUrlTemp.lastIndexOf('/')) + '/out.png';
        //var filePath = getFilePath()+ '/out.png';
        fs.writeFile(filePath, dataBuffer, function (err) {
            if (err) {
                console.log(err.message);
                isSaveImage = false;
		_sourceCanvas.style.zIndex = -1;
		 _sourceContext.drawImage(img, 0, 0);
		
            } else {
                //调用后台方法
                var python = require('child_process').spawn('python', ['nfs_python/nfs_dialog.py', filePath]);
                python.stdout.on('data',function (data) {
		   
                    if(data.toString().length<=1){
                        fs.unlinkSync(filePath);
                        isSaveImage= false;
			_sourceCanvas.style.zIndex = -1;
			 _sourceContext.drawImage(img, 0, 0);
                        return;
                    }else{
                        //成功之后，需要清除文件
                        fs.unlinkSync(filePath);
                        fs.unlinkSync(imgUrlTemp);
                        //清空界面
                        $('#container').html("");
                        $('.tip').css('display','block');
                        $('.tip').html('保存成功');
                        setTimeout(function(){
                            $('.tip').css('display','none');
                        },2000);
                        _sourceCanvas = undefined;
                        _sourceContext = undefined;
			_tempsourceContext = undefined;
                        _drawCanvas = undefined;
                        _drawContext = undefined;
                        _textCanvas = undefined;
                        _textContext = undefined;
                        isSaveImage = false;
			//清空数组内容
			map.clear();
                    }

                });

                python.stderr.on('data', function (data) {
                    $('.tip').css('display','block');
               //     $('.tip').html('保存失败');
                    isSaveImage = false;
		      _sourceContext.drawImage(img, 0, 0);
		      _tempsourceContext.drawImage(img,0,0);
                    setTimeout(function(){
                        $('.tip').css('display','none');
                    },2000);
                });
            }
        });
    }


    //色值的改变
    $("#borderColor > li").click(function () {

        $(this).css("border", "1px solid #68777a");
        $(this).siblings().css("border", "");
        var colorTemp = $(this).css("background-color");
        $(".color").css("background-color", colorTemp);
        _color = colorTemp;
        //改变文字颜色
	if(_textCanvas!=undefined){
		_textCanvas.color = colorTemp;
	}
        
    });

    //大小选择
    $(".line_box>li").click(function () {
        $(this).addClass("presssize");
        $(this).siblings().removeClass("presssize");
        sizeIndex = $(this).index();
        changeLineWidth();
    });

    //添加加减按钮事件
    $("#add").click(function () {
        var size = $("#fontsize").val();
        if (size < 72) {
	    $(this).css("background","repeat scroll 0 0 rgba(255, 235, 205,50)");
	    $("#subtract").css("background","repeat scroll 0 0 rgba(255, 235, 205,50)");
	    if(typeof($(this).attr("disable")) != "undefined"){
		 $(this).removeAttr("disable");
	    }
            size = parseInt(size) + 2;
            $("#fontsize").val(size);
            fontSize = size;
            if(_textCanvas!=undefined){
                _textCanvas.fontSize = fontSize+"px";
            }
            $("#tt").css("font-size",fontSize+"px");
            $("#tt").focus();
        }else{
	    $(this).css("background","repeat scroll 0 0 rgba(192,192,192,50)")
	    $(this).attr("disable","disabled");
	}

    });

    $("#subtract").click(function () {
        var size = $("#fontsize").val();
        if (size > 8) {
	     $(this).css("background","repeat scroll 0 0 rgba(255, 235, 205,50)");
 	     $("#add").css("background","repeat scroll 0 0 rgba(255, 235, 205,50)");
	    if(typeof($(this).attr("disable")) != "undefined"){
		 $(this).removeAttr("disable");
	    }
            size = parseInt(size) - 2;
            $("#fontsize").val(size);
            fontSize = size;
            if(_textCanvas!=undefined){
                _textCanvas.fontSize = fontSize+"px";
            }
            $("#tt").css("font-size",fontSize+"px");
            $("#tt").focus();
        }else{
	    $(this).css("background","repeat scroll 0 0 rgba(192,192,192,50)")
	    $(this).attr("disable","disabled");
	}
    });
  
    //show();
   
});

function resetCanvas(){
			$('#container').html("");
			$('#showTxt').hide();                        
			_sourceCanvas = undefined;
                        _sourceContext = undefined;
	                _tempsourceContext = undefined;
                        _drawCanvas = undefined;
                        _drawContext = undefined;
                        _textCanvas = undefined;
                        _textContext = undefined;
                        isSaveImage = false;
			//清空数组内容
			map.clear();
}


//修改线条值
function changeLineWidth(){
    switch (sizeIndex) {
        case 0:
            if (_drawMode == 'arrow') {
                _brushWidth = 15;
            } else if (_drawMode == "eraser") {
                _eraserWidth = 20;
            } else {
                _lineWidth = 1;
            }
            _fill = false;
            break;
        case 1:
            if (_drawMode == 'arrow') {
                _brushWidth = 30;
            } else if (_drawMode == "eraser") {
                _eraserWidth = 30;
            } else {
                _lineWidth = 5;
            }
            _fill = false;
            break;
        case 2:
            if (_drawMode == 'arrow') {
                _brushWidth = 50;
            } else if (_drawMode == 'eraser') {
                _eraserWidth = 40;
            }
            else {
                _lineWidth = 10;
            }
            _fill = false;
            break;
        case 3:
            _fill = true;
            break;
    }
}

//改变字体线宽，这里是通过点击工具栏触发的
function changeIndex() {
    //这里不仅仅改变line_box的显示，同时需要修改linewidth
    if (sizeIndex == 0 || sizeIndex == 1 || sizeIndex == 2) {
        $(".line_box>li:eq(sizeIndex)").addClass("presssize").siblings().removeClass("presssize");
    } else {
        if (_drawMode == 'rect' || _drawMode == 'ellipse') {
            $(".line_box>li:eq(sizeIndex)").addClass("presssize").siblings().removeClass("presssize");
        } else if (_drawMode == 'arrow' || _drawMode == 'pencil' || _drawMode == 'eraser') {
            $(".line_box>li:eq(0)").addClass("presssize");
            $(".line_box>li:gt(0)").removeClass("presssize");
            sizeIndex = 0;
        }
    }
    changeLineWidth();
}


/**
 * 绑定事件
 *
 */
function changeEvent() {
    
    if (_sourceCanvas != undefined && _textCanvas != undefined && _drawCanvas!=undefined ){
	if(_drawMode == "rect" || _drawMode == "ellipse" || _drawMode == "arrow" || _drawMode == "pencil" || _drawMode == "eraser") {
		   //_textCanvas.removeTextInputEvent();
		_textCanvas.removeEventListener("mousedown", mouseDown);
        	_drawCanvas.style.zIndex = 2;
        	_drawCanvas.addEventListener("mousedown", mouseDown);
        	_drawCanvas.addEventListener("mousemove", mouseMove);
        	document.addEventListener("mouseup", mouseUp);
	}else{
		//_textCanvas.listenTextInput();
       		 _drawCanvas.style.zIndex = -1;
        	_drawCanvas.removeEventListener("mousedown", mouseDown);
        	_drawCanvas.removeEventListener("mousemove", mouseMove);
        	document.removeEventListener("mouseup", mouseUp);
		_textCanvas.addEventListener("mousedown", mouseDown);
	}
    }
}


/**
 * 根据python脚本传递过来的图片地址，加载画布
 * @param url
 */
function loagImage(url) {
    //加载之前先清空画布内容
    $("#container").html("");
    img = new Image()
    img.src = url;
    loading = true;
    img.onload = function () {
	imgUrl = url;
        //计算出div的宽和高
        //计算出div的宽和高
        if (clientWidth == undefined) {
            //clientWidth = document.documentElement.clientWidth;
	    clientWidth = window.screen.width;
        }
        if (clientHeight == undefined) {
            //clientHeight = document.documentElement.clientHeight;
	    clientHeight = window.screen.height - 40;        
	}

        //var divHeight = clientHeight - ($(".top_main").height() + $(".bottom_main").height());
        //var divWidth = clientWidth - $(".center_left").width();

        if(maximizeState  == 0)
        {
            var divHeight = 445;
	    var divWidth = 710;
        }
	else
        {
            var divHeight = clientHeight - ($(".top_main").height() + $(".bottom_main").height());
	    var divWidth = clientWidth - $(".center_left").width();
	}

        $(".center_left").css("height", divHeight);
        $(".center_right").css({"height": divHeight, "width": divWidth});

        sourceCanvasSize.width = img.width;  //根据图片的高度和宽度初始化画布大小(画布大小将根据可见范围来设定)
        sourceCanvasSize.height = img.height;
//	sourceCanvasSize.width = divWidth;  //根据图片的高度和宽度初始化画布大小(画布大小将根据可见范围来设定)
  //      sourceCanvasSize.height = divHeight;	

        //依次添加三个canvas
        var draw = document.getElementById("container");

        _sourceCanvas = document.createElement("canvas");
        _sourceCanvas.width = img.width;
        _sourceCanvas.height = img.height;
 
        _sourceCanvas.style.zIndex = -2;
        _sourceCanvas.style.position = "absolute";
        _sourceCanvas.style.top = 0;
	_sourceCanvas.style.border = "1px solid rgb(0,0,0)";
        _sourceCanvas.id = "sourceCanvas";

        _drawCanvas = document.createElement("canvas");
        _drawCanvas.width = img.width;
        _drawCanvas.height = img.height;
  
        _sourceCanvas.style.zIndex = -1;
        _drawCanvas.style.position = "absolute";
        _drawCanvas.style.top = 0;
        _drawCanvas.style.left = 0;
	_drawCanvas.style.border = "1px solid rgb(0,0,0)";
        _drawCanvas.id = "drawCanvas";
        _drawCanvas.cursor = "auto";

        _textCanvas = TextCanvas.create({
            width: img.width,
            height: img.height,
            fontFamily: "\u5B8B\u4F53",
            color: "#F00"
        });
        //_textCanvas.style.zIndex = 0;
        _textCanvas.style.position = "absolute";
        _textCanvas.id = "textCanvas";

        draw.appendChild(_drawCanvas);
        draw.appendChild(_sourceCanvas);
        draw.appendChild(_textCanvas);

        //获取上下文
        _sourceContext = _sourceCanvas.getContext("2d");
	_tempsourceContext = _sourceCanvas.getContext("2d");
        _drawContext = _drawCanvas.getContext("2d");
        _textContext = _textCanvas.getContext("2d");
	
	
        if (img.width <= divWidth && img.height <= divHeight) {
            //根据center_right的宽和高修改canvas_bak的位置
            canWidth = parseFloat((divWidth - img.width)) / 2 + "px";
            canHeight = parseFloat((divHeight - img.height)) / 2 + "px";
            //arrowyheight=parseFloat((divHeight - img.height)) / 2;
            $(_sourceCanvas).css({"margin-left": canWidth, "margin-top": canHeight});
            $(_drawCanvas).css({"margin-left": canWidth, "margin-top": canHeight});
            $(_textCanvas).css({"margin-left": canWidth, "margin-top": canHeight});
        }
	else if(img.width<= divWidth && img.height > divHeight){
	    canWidth = parseFloat((divWidth - img.width)) / 2 + "px";
            $(_sourceCanvas).css({"margin-left": canWidth});
            $(_drawCanvas).css({"margin-left": canWidth});
            $(_textCanvas).css({"margin-left": canWidth});
            //_sourceContext.drawImage(img, 0, 0,img.width,img.height);
	}else if(img.width>divWidth && img.height <= divHeight){
	     canHeight = parseFloat((divHeight - img.height)) / 2 + "px";
             //arrowyheight=parseFloat((divHeight - img.height)) / 2;
            $(_sourceCanvas).css({"margin-top": canHeight});
            $(_drawCanvas).css({"margin-top": canHeight});
            $(_textCanvas).css({"margin-top": canHeight});
            //_sourceContext.drawImage(img, 0, 0,img.width,img.height);
	}else if(img.width>divWidth && img.height > divHeight){
	     //_sourceContext.drawImage(img, 0, 0,img.width,img.height);
	}
        _sourceContext.drawImage(img, 0, 0);
	_tempsourceContext.drawImage(img, 0, 0);
	show();
	$("#shclFireballs").hide();
	$("#container").show();
    };
}




      


//=======================================鼠标相关操作===================================

mouseDown = function (e) {
    //如果原图存在的话
    if (_sourceCanvas != undefined) {
        var mouseX = e.clientX - $(_sourceCanvas).offset().left;
        var mouseY = e.clientY - $(_sourceCanvas).offset().top;
        if (_drawMode == "rect") {
            _syncSquareObj = new SyncSquare();
            _syncSquareObj.beginPos.x = mouseX;
            _syncSquareObj.beginPos.y = mouseY;
            _syncSquareObj.fill = _fill;
            _syncSquareObj.color = _color;
            _syncSquareObj.lineWidth = _lineWidth;
	     _paint = true;
	    _Isreset = true;
        } else if (_drawMode == "ellipse") {
            _syncCircleObj = new SyncCircle();
            _syncCircleObj.beginPos.x = mouseX;
            _syncCircleObj.beginPos.y = mouseY;
            _syncCircleObj.fill = _fill;
            _syncCircleObj.color = _color;
            _syncCircleObj.lineWidth = _lineWidth;
	     _paint = true;
	     _Isreset = true;
        }else if(_drawMode == "arrow"){
            _syncArrowObj = new SyncArrow();
            _syncArrowObj.beginPos.x = mouseX;
            _syncArrowObj.beginPos.y = mouseY;
            _syncArrowObj.color = _color;
            _syncArrowObj.brushWidth = _brushWidth;
	    _paint = true;
            _Isreset = true;

        }
        else if(_drawMode == "pencil"){
            _lineObj = new Line();
            _lineObj.x = mouseX;
            _lineObj.y = mouseY;
            _lineObj.context = _textContext;
            _lineObj.lineWidth = _lineWidth;
            _lineObj.color = _color;
            _lineObj.moveTo();
            _syncLineObj = new SyncLine();
            _syncLineObj.beginPos.x = mouseX;
            _syncLineObj.beginPos.y = mouseY;
            _syncLineObj.color = _color;
            _syncLineObj.lineWidth = _lineObj.lineWidth;
	    _paint = true;
	    _Isreset = true;

        }else if (_drawMode == "eraser"){
            _eraserObj = new Eraser();
            _eraserObj.x = mouseX;
            _eraserObj.y = mouseY;
            _eraserObj.context = _textContext;
            _eraserObj.lineWidth = _eraserWidth;
            _eraserObj.color = "white";
            _eraserObj.moveTo();
            _syncEraserObj = new SyncEraser();
            _syncEraserObj.beginPos.x = mouseX;
            _syncEraserObj.beginPos.y = mouseY;
            _syncEraserObj.color = "white";
            _syncEraserObj.lineWidth = _eraserWidth;
	    _paint = true;
	    _Isreset = true;

        }else if(_drawMode == "text"){
	     if(isReDrawFlag) {  //如果为真的话，那么就把内容画上去
                            var words = $(".text_box").val();
                            if (words != "") {
                                var array = words.split('\n');
                                _textContext.font = fontSize + "px Arial";
                                _textContext.fillStyle = fontcolor;
                                if (array.length > 0) {
                                    for (var i = 0; i < array.length; i++) {
                                        _textContext.fillText(array[i], mouseX, (mouseY + fontSize * (i + 1)));
                                    }
                                }
                                $(".text_box").val("");
                                isReDrawFlag = false;
                                $("#commitBtn").attr("disabled",false);
                                _syncTextObj = new SyncText();
				_syncTextObj.text = array;
				_syncTextObj.color = fontcolor;
                                _syncTextObj.fontSize = fontSize;
				_syncTextObj.beginPos.x = mouseX;
				_syncTextObj.beginPos.y = mouseY;
				map.put(map.getCount(),new createCanvasOperation(_drawMode,_syncTextObj));
				_Isreset = true;

                            }
                        }	
	}
        e=e||window.event;
        e.preventDefault();
    }
};

mouseMove = function (e) {
    if (_sourceCanvas != undefined && _paint) {
        var mouseX = e.clientX - $(_sourceCanvas).offset().left;
        var mouseY = e.clientY - $(_sourceCanvas).offset().top;
        if (_drawMode == "rect") {
            _syncSquareObj.endPos.x = mouseX;
            _syncSquareObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawRect(_drawContext, false, _syncSquareObj);
        }else if(_drawMode == "ellipse"){
            _syncCircleObj.endPos.x = mouseX;
            _syncCircleObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawEllipse(_drawContext, false, _syncCircleObj);
        }else if(_drawMode == "arrow"){
            _syncArrowObj.endPos.x = mouseX;
            _syncArrowObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawArrow(_drawContext, false,_syncArrowObj);
        }else if(_drawMode == "pencil"){
            _lineObj.lineTo(mouseX, mouseY);
            var pos = new Pos();
            pos.x = mouseX;
            pos.y = mouseY;
            _syncLineObj.endPosArr.push(pos);
        }else if (_drawMode == "eraser"){
            _eraserObj.lineTo(mouseX, mouseY);
            var pos = new Pos();
            pos.x = mouseX;
            pos.y = mouseY;
            _syncEraserObj.endPosArr.push(pos);
        }
    }
};

mouseUp = function (e) {
    if (_sourceCanvas != undefined && _paint) {
     var mouseY = e.clientY - $(_sourceCanvas).offset().top;
        var mouseX = e.clientX - $(_sourceCanvas).offset().left;
                if(parseInt(mouseX) < 0)

            {
                    mouseX = 0;
                                            }
                if(mouseX> _sourceCanvas.width)
                            {
                        mouseX= _sourceCanvas.width;
                                            }
                if (parseInt(mouseY) > parseInt(_sourceCanvas.height))
                        {
                                    mouseY = _sourceCanvas.height;
                              }
                      if (mouseY<0)
            {

                             mouseY=0;}
   
     if (_drawMode == "rect") {
            _syncSquareObj.endPos.x = mouseX;
            _syncSquareObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawRect(_textContext, true, _syncSquareObj);
        }else if(_drawMode == "ellipse"){
            _syncCircleObj.endPos.x = mouseX;
            _syncCircleObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawEllipse(_textContext, true, _syncCircleObj);
        }else if(_drawMode == "arrow"){
            _syncArrowObj.endPos.x = mouseX;
            _syncArrowObj.endPos.y = mouseY;
            _drawContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
            drawArrow(_textContext, true,_syncArrowObj);
        }else if(_drawMode == "pencil"){
            map.put(map.getCount(), new createCanvasOperation(_drawMode, _syncLineObj));
        }else if(_drawMode == "eraser"){
            map.put(map.getCount(), new createCanvasOperation(_drawMode, _syncEraserObj));
        }
        _paint = false;
    }
};

//==========================================================================
function SyncSquare() {
    this.beginPos = new Pos();
    this.endPos = new Pos();
    this.color = 0;
    this.lineWidth = 0;
    this.fill = false;
}

function SyncCircle() {
    this.beginPos = new Pos();
    this.endPos = new Pos();
    this.color = 0;
    this.lineWidth = 0;
    this.fill = false;
}

function SyncArrow(){
    this.beginPos = new Pos();
    this.endPos = new Pos();
    this.color = 0;
    this.brushWidth = 0;
}

function Line(){
    this.x = 0;
    this.y = 0;
    this.color = 0;
    this.lineWidth = 0;
    this.moveTo = function() {
        this.context.lineWidth = this.lineWidth;
        this.context.beginPath();
        this.context.strokeStyle= this.color;
        this.context.moveTo(this.x, this.y);
    };
    this.lineTo = function(dx, dy){
        this.context.lineWidth = this.lineWidth;
        this.context.strokeStyle= this.color;
        if(_drawMode == "eraser"){
            this.context.strokeStyle= "white";
        }
        this.context.lineTo(dx, dy);
        this.context.stroke();
    }
}

function SyncLine(){
    this.beginPos = new Pos();
    this.endPosArr = new Array();
    this.color = 0;
    this.lineWidth = 0;
}

function SyncText(){
    this.beginPos = new Pos();
    this.text = "";
    this.color = "";
    this.fontSize = "";
}

function SyncEraser(){
    this.beginPos = new Pos();
    this.endPosArr = new Array();
    this.color = 0;
    this.lineWidth = 0;
}

function Eraser(){
    this.line = Line;
    this.line();
    this.lineWidth = _eraserWidth;
    this.color = "white";
}

function Pos() {
    this.x = 0;
    this.y = 0;
}


/*********************************************************绘图操作**********************************************************/
/**
 * @param tempContext 要绘制的画布
 * @param isSave 是否保存
 * @param reDraw 是否重绘
 * @param obj 如果是重绘的话需要传入此值
 */
function drawRect(tempContext, isSave, obj) {
    tempContext.lineWidth = obj.lineWidth;
    tempContext.beginPath();
    if (obj.fill) {
        tempContext.fillStyle = obj.color;
        tempContext.fillRect(obj.beginPos.x, obj.beginPos.y, obj.endPos.x - obj.beginPos.x, obj.endPos.y - obj.beginPos.y);
    } else {
        tempContext.strokeStyle = obj.color;
        tempContext.strokeRect(obj.beginPos.x, obj.beginPos.y, obj.endPos.x - obj.beginPos.x, obj.endPos.y - obj.beginPos.y);
    }

    if (isSave) {
        map.put(map.getCount(), new createCanvasOperation(_drawMode, obj));
    }
}

function drawEllipse(contextTemp, isSave, obj) {
    contextTemp.lineWidth = obj.lineWidth;
    contextTemp.beginPath();
    var k = ((obj.endPos.x - obj.beginPos.x) / 0.75) / 2,
        w = (obj.endPos.x - obj.beginPos.x) / 2,
        h = (obj.endPos.y - obj.beginPos.y) / 2,
        x = (obj.endPos.x + obj.beginPos.x) / 2,
        y = (obj.endPos.y + obj.beginPos.y) / 2;
    contextTemp.beginPath();
    contextTemp.moveTo(x, y - h);
    contextTemp.bezierCurveTo(x + k, y - h, x + k, y + h, x, y + h);
    contextTemp.bezierCurveTo(x - k, y + h, x - k, y - h, x, y - h);
    contextTemp.closePath();
    if (obj.fill) {
        contextTemp.fillStyle = obj.color;
        contextTemp.fill();
    } else {
        contextTemp.strokeStyle = obj.color;
        contextTemp.stroke();
    }
    if (isSave) {
        map.put(map.getCount(), new createCanvasOperation(_drawMode, obj));
    }
}

function drawArrow(contextTemp,isSave,obj){
    paraDef(obj.brushWidth, 25);
    Plot.arrowCoord(obj.beginPos, obj.endPos);
    Plot.sideCoord();
    Plot.drawArrow(contextTemp, obj.color);
    if (isSave) {
        map.put(map.getCount(), new createCanvasOperation(_drawMode, obj));
    }
}

//涂鸦(回滚)
function drawPencilAndEraser(obj,type) {
    _textContext.beginPath();
    if(type == "pencil"){
        _lineObj = new Line();
        _lineObj.x = obj.beginPos.x;
        _lineObj.y = obj.beginPos.y;
        _lineObj.color = obj.color;
        _lineObj.lineWidth = obj.lineWidth;
        _lineObj.context = _textContext;
        _lineObj.moveTo();
        for(var i = 0; i < obj.endPosArr.length; i++) {
            _lineObj.lineTo(obj.endPosArr[i].x, obj.endPosArr[i].y);
        }
    }else{
        _eraserObj = new Eraser();
        _eraserObj.x = obj.beginPos.x;
        _eraserObj.y = obj.beginPos.y;
        _eraserObj.color = obj.color;
        _eraserObj.lineWidth = obj.lineWidth;
        _eraserObj.context = _textContext;
        _eraserObj.moveTo();
        for(var i = 0; i < obj.endPosArr.length; i++) {
            _eraserObj.lineTo(obj.endPosArr[i].x, obj.endPosArr[i].y);
        }
    }

    _textContext.closePath();
}




//初始化检测当前截图软件是否是print键启动的
function isCheck_PirntDir(){
    var python = spawn('python', ['nfs_python/nfs_check_print.py']);
    python.stdout.on('data', function (data) {
        if(data!=null && data.toString().trim() != "" ){
            loagImage(data.toString());
        }else{
	    show();
	}
    });

    python.stderr.on('data', function (data) {
        show();
    });
}


/**
 *  自定义对象，用来记录回滚操作时所需要的基础信息
 *  drawType 操作类型
 */
function createCanvasOperation(drawType, drawObj) {
    this.drawType = drawType;
    this.drawObj = drawObj;
}

  function undo(){
	if(map.getCount() == 0){
		return false;	
	}

	 map.remove(map.getCount() - 1);
		if(_textContext != undefined){
			 _textContext.clearRect(0, 0, sourceCanvasSize.width, sourceCanvasSize.height);
		}               
		
                $.map(map.getEntrys(), function (n) {
                    //重画矩形
                    if (n.value.drawType == 'rect') {
                        drawRect(_textContext, false, n.value.drawObj);
                    } else if (n.value.drawType == 'text') {
			if(_textContext != undefined){
				 var _t =  n.value.drawObj;
				  _textContext.font = _t.fontSize + "px Arial";
		                  _textContext.fillStyle = _t.color;
				  var array = _t.text;
		                  if (array.length > 0) {
		                        for (var i = 0; i < array.length; i++) {
		                                _textContext.fillText(array[i], _t.beginPos.x, (_t.beginPos.y + _t.fontSize * (i + 1)));
		                        }
		                  }
			}
                        //_textCanvas.drawText(n.value.drawObj.text);
			 
                    }else if(n.value.drawType == 'ellipse'){
                        drawEllipse(_textContext,false,n.value.drawObj);
                    }else if (n.value.drawType == 'arrow'){
                        drawArrow(_textContext,false,n.value.drawObj);
                    }else if(n.value.drawType == 'pencil' || n.value.drawType == "eraser"){
                        drawPencilAndEraser(n.value.drawObj, n.value.drawType);
                    }
                });	
    }	
//-------------------------------------------------------------------------------------------------------------------------
