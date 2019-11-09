"use strict";
//TODO: When drag browser out screen or scroll page.

//global value
var SPAN,
    isWord = /^[\w]+$/,
    isChromeWord = /^[\w0-9`~!@#$%^&\*\(\)<>:"{}|,./;''\[\]\\\+=]+$/,
    isSpace = /^\s+$/,
    rSplit = /([\s]+)|([\w0-9`~!@#$%^&\*\(\)<>:"{}|,./;''\[\]\\\+=]+)|([^\w0-9`~!@#$%^&\*\(\)<>:"{}|,./;''\[\]\\\+=\n\r]+)|([\n\r]+)/g;

//init global value
SPAN = document.createElement("span");
SPAN.style.font = "18px";
SPAN.innerHTML = "";
SPAN.style.position = "absolute";
SPAN.style.left = "-5000px";
SPAN.style.border = 0;
SPAN.style.padding = 0;
SPAN.style.margin = 0;

var oldLeft = 0;  //记录滚动条水平方向旧状态
var oldTop = 0 ; //记录滚动条垂直方向旧状态
var isLeftFlag= 0; //没移动 1, -1
var isTopFlag = 0 ;// 没移动

function htmlEncode(str) {
    var s = "";
    if (str.length == 0) return "";
    s = str.replace(/&/g, "&amp;");
    s = s.replace(/</g, "&lt;");
    s = s.replace(/>/g, "&gt;");
    //s = s.replace(/ /g, "&nbsp;");
    s = s.replace(/\'/g, "&#39;");
    s = s.replace(/\"/g, "&quot;");
    s = s.replace(/\n/g, "<br>");
    return s;
}

function html_decode(str) {
    var s = "";
    if (str.length == 0) return "";
    s = str.replace(/&amp;/g, "&");
    s = s.replace(/&lt;/g, "<");
    s = s.replace(/&gt;/g, ">");
    //s = s.replace(/&nbsp;/g, " ");
    s = s.replace(/&#39;/g, "\'");
    s = s.replace(/&quot;/g, "\"");
    s = s.replace(/<br>/g, "\n");
    return s;
}


var Text = {
    create: function(t) {
        var text = {};
        text.top = t.top || "36px";
        text.left = t.left || "24px";
        text.color = t.color || "#333";
        text.font = t.font || "12px arial";
        text.lineHeight = t.font.match(/[\d]{1,}px/)[0];
        text.content = t.content || "";
        text.width = t.width || "36px";
        text.height = t.height || "24px";
        text.maxWidth = t.maxWidth || "600px";
        text.maxHeight = t.maxHeight || "400px";
        text.parent = t.parent;
        return text;
    }
};

var TextInput = {
    create: function() {
        var textInput = document.createElement("textarea");

        textInput.init = function(t, p) {
            //this.text = t;
            this.id = "__textInput";
            this.style.resize = "none";
            this.style.outline = "none";
            this.style.border = "dashed 1px #000";
            this.style.padding = 0;
            this.style.margin = 0;
            this.style.position = "absolute";
            this.style.backgroundColor = "transparent";
            this.style.overflow = "hidden";
            this.style.color = t.color;
            this.style.font = t.font;
            this.style.top = (parseInt(t.top) - 1) + "px";
            this.style.left = (parseInt(t.left) - 1) + "px";
            this.style.width = t.width;
            this.style.height = t.height;
            this.style.maxWidth = t.maxWidth;
            this.style.maxHeight = t.maxHeight;
            this.style.lineHeight = t.lineHeight;
            this.value = t.content.replace(/\r/g, "");
            this.buffer = t.content.replace(/\r/g, "");
            this.parent = p || t.parent;
        };

        textInput.toText = function() {
            return Text.create({
                top: (parseInt(this.style.top) + 1) + "px",
                left: (parseInt(this.style.left) + 1) + "px",
                color: this.style.color,
                font: this.style.font,
                content: this.buffer,
                width: (this.offsetWidth - 2) + "px",
                height: (this.offsetHeight - 2) + "px",
                maxWidth: this.style.maxWidth,
                maxHeight: this.style.maxHeight,
                parent: this.parent
            });
        };

        textInput.parseValue = function() {
            var strArr = this.value.split(/\n|\r/);
            var i, rows = strArr.length, maxLine = 0, len;
            for ( i = 0; i < rows; i++ ) {
                len = this.getStrWidth(strArr[i]);
                if (len > maxLine) {
                    maxLine = len;
                }
            }
            //this.maxLine = maxLine;
            return [rows, maxLine];
        };

        textInput.getStrWidth = function(str) {
            var span = SPAN.cloneNode();
            span.style.font = this.style.font;
            span.innerHTML = str;
            document.body.appendChild(span);
            var width = span.offsetWidth;
            document.body.removeChild(span);

            return width;
        };

        textInput.transValue = function() {
            var span = SPAN.cloneNode(),
                nextSpan = SPAN.cloneNode(),
                buffer = "",
                maxWidth = parseInt(this.style.maxWidth);
            span.style.font = this.style.font;
            nextSpan.style.font = this.style.font;
            document.body.appendChild(span);
            document.body.appendChild(nextSpan);
            console.log("bufer1 : " + this.value);
            //var value = this.value.split(/\b/);
            var value = this.value.match(rSplit);
            if ( !value ) return;
            console.log(value);
            var totalLen = value.length;
            for ( var i = 0; i < totalLen; i++ ) {
                span.innerHTML += htmlEncode(value[i]);
                // /^\w+$/.test
                while ( span.offsetWidth > maxWidth ) {
                    var tVal = html_decode(span.innerHTML),
                        tmpLen =  tVal.length;
                    span.innerHTML = "";
                    for ( var j = 0; j < tmpLen; j++ ) {
                        span.innerHTML += htmlEncode(tVal[j]);
                        nextSpan.innerHTML = htmlEncode(tVal[j + 1]);
                        if ( span.offsetWidth + nextSpan.offsetWidth > maxWidth ) {
                            buffer += html_decode(span.innerHTML);
                            buffer += "\r";
                            span.innerHTML = htmlEncode(tVal.substr(j + 1));
                            break;
                        }
                    }
                }
                if ( i + 1 < totalLen ) {
                    /*if ( isSpace.test(value[i + 1]) ) {
                        buffer += html_decode(span.innerHTML);
                        span.innerHTML = "";
                        buffer += "\r";
                        continue;
                    }*/
                    nextSpan.innerHTML = htmlEncode(value[i + 1]);
                    if ( /\n/.test(html_decode(span.innerHTML)) ) {
                        var lastLF = html_decode(span.innerHTML).lastIndexOf('\n');
                        buffer += html_decode(span.innerHTML).substr(0, lastLF + 1);
                        span.innerHTML = htmlEncode(html_decode(span.innerHTML).substr(lastLF + 1));
                        if (span.innerHTML == "") continue;
                    }
                    if ( span.offsetWidth + nextSpan.offsetWidth > maxWidth ) {
                        if ( isChromeWord.test(value[i + 1]) ) {
                            buffer += html_decode(span.innerHTML);
                            span.innerHTML = "";
                            buffer += "\r";
                        }
                    }
                }
            }
            buffer += html_decode(span.innerHTML);
            this.value = buffer;
            this.buffer = buffer;
            document.body.removeChild(span);
            document.body.removeChild(nextSpan);
        };

        textInput.show = function() {
            document.body.appendChild(this);
            this.addEventListener("input", function(e) {
                var maxWidth = parseInt(this.style.maxWidth);
                /**fix:bug 001*/
                /*if ( e.keyCode == 32 || e.keyCode == 13 || e.keyCode == 16 || (e.keyCode > 47 && e.keyCode < 58)
                    || e.keyCode == 188 || e.keyCode == 190 || e.keyCode == 186  ) {
                    this.transValue();
                }*/
                var r = this.parseValue();
                if ( r[1] >  maxWidth ) {
                    this.style.width = this.style.maxWidth;
                    /**bug:001 IME preview show */
                        //this.buffer = this.value.substr(0, this.value.length - 1) + "\n" + this.value.substr(-1, 1);
                    r[0] = r[0] +   r[1] / maxWidth + 1;
                } else {
                    this.style.width = (r[1] +  parseInt(this.style.lineHeight)) + "px";
                }
                this.style.height = (r[0] * parseInt(this.style.lineHeight)) + "px";
            });

            this.addEventListener("blur", function() {
                this.transValue();
                var maxWidth = parseInt(this.style.maxWidth);
                var r = this.parseValue();
               /* if ( r[1] >  maxWidth ) {
                    this.style.width = this.style.maxWidth;
                    r[0] = r[0] +   r[1] / maxWidth + 1;
                } else {
                    this.style.width = (r[1] +  parseInt(this.style.lineHeight)) + "px";
                }*/
                this.style.height = ((r[0] + 1) * parseInt(this.style.lineHeight)) + "px";
                this.parent.drawText(this.toText());
                document.body.removeChild(this);
		_syncTextObj = new SyncText();
		_syncTextObj.text = this.toText();
		map.put(map.getCount(),new createCanvasOperation(_drawMode,_syncTextObj));
                delete this;
            });
            this.addEventListener("focus", function() {
                this.removeEventListener("mouseout", this.mouseOut);
                this.parent.removeEventListener("mouseup", this.parent.leftMouseDown);
                this.parent.removeEventListener("mousemove", this.parent.mouseMove);
                //textInput.listenInput();
            });
        };

        textInput.listenInput = function() {
            this.focus();
        };

        textInput.preShow = function() {
            this.addEventListener("mouseout", this.mouseOut);
            this.show();
        };

        textInput.mouseOut = function() {
            this.transValue();
            var text = this.toText();
            document.body.removeChild(this);
            delete this;
            this.parent.drawText(text);
        };

        return textInput;
    }
};

var TextCanvas = {
    opts: {
        fontSize: "18px",
        fontFamily: "arial",//"\u5B8B\u4F53";
        width: 300,
        height : 200,
        color : "#000"
    },
    create: function(p) {
        p = p || {};
        var canvas = p.canvas || document.createElement("canvas");
        //var div = canvas.parent || document.createElement("div");
        canvas.fontSize = p.fontSize || TextCanvas.opts.fontSize;
        canvas.fontFamily = p.fontFamily || TextCanvas.opts.fontFamily;
        canvas.width = p.width || TextCanvas.opts.width;
        canvas.height = p.height || TextCanvas.opts.height;
        canvas.color = p.color || TextCanvas.opts.color;
        canvas.style.border = "solid 1px #000";
        //canvas.content = p.content || "";
        canvas.top = p.top;
        canvas.left = p.left;
        canvas.graphics2D = canvas.getContext("2d");
        /**/
        canvas.parent = p.parent;
        canvas.texts = [];
        canvas.selectText = undefined;

        /*div.style.width = canvas.width;

        div.style.height = canvas.width;
        div.style.position = "relative";
        div.style.overflow = "hidden";*/

        canvas.toTextInput = function(t) {
            var textInput = TextInput.create();
            textInput.init(t);
            return textInput;
        };

        canvas.clear = function(text) {
            canvas.graphics2D.globalCompositeOperation = "destination-out";
            //canvas.graphics2D.clearRect(...);
            canvas.graphics2D.fillRect(parseInt(text.left) - this.getBoundingClientRect().left,
                                        parseInt(text.top) - this.getBoundingClientRect().top,
                                        parseInt(text.width), parseInt(text.height));
        };

        canvas.clearAll = function() {
            for ( var i = 0; i < canvas.texts.length; i++) {
                this.clear(i);
            }
        };

        canvas.drawText = function(t) {
            if ( !t.content ) {
                window.setTimeout(function(){
                    if (!canvas.listeningTextInup) return;
                    canvas.addEventListener("mouseup", canvas.leftMouseDown)}
                    , 200);
                return;
            }
            canvas.texts.push(t);
            canvas.graphics2D.textBaseline = "top";
            canvas.graphics2D.textAlign = "left";

            canvas.graphics2D.fillStyle = t.color;
            canvas.graphics2D.font =  t.font;
            canvas.graphics2D.globalCompositeOperation = "source-over";
            var cArr = t.content.split(/\n|\r/),
                left = parseInt(t.left) - this.getBoundingClientRect().left,
                top = parseInt(t.top) - this.getBoundingClientRect().top;
            console.log(cArr);
            for ( var i = 0; i < cArr.length; i++ ) {
                canvas.graphics2D.fillText(cArr[i], left, top);
                top = top + parseInt(this.fontSize);
            }

            window.setTimeout(function(){
                if (!canvas.listeningTextInup) return;
                canvas.addEventListener("mouseup", canvas.leftMouseDown);
                canvas.addEventListener("mousemove", canvas.mouseMove);
            }, 200);
        };

        canvas.overText = function(x, y) {
           // var text, x1, y1;
            //for ( var i = 0; i < canvas.texts.length; i++ ) {
            //    text = canvas.texts[i];
				//判断左侧有没有被遮挡住
				
			
             //   x1 = x - (parseInt(text.left));
           //     y1 = y - parseInt(text.top);
            //    if ( x1 > 0 && x1 < parseInt(text.width) && y1 > 0 && y1 < parseInt(text.height) ) {
		//			console.log("===========================action==========================");
		//			
		//			return [text, i];
               // }
            //}

            //return 0;
        };

        /**event function*/
        canvas.leftMouseDown = function(e) {
            if ( e.button == 0 /* && e.buttons == 1 */ ) {
		
		var __width = "";
		var __height = "";
				
		__width = (this.width - (this.width - $(this).parent().width())+$(this).parent().scrollLeft() - 19 - e.clientX + this.getBoundingClientRect().left) + "px";
		__height = (this.height - (this.height - $(this).parent().height())+$(this).parent().scrollTop() - 22 - e.clientY + this.getBoundingClientRect().top) + "px";		
                var t = Text.create({
                    top: e.clientY + "px",
                    left: e.clientX + "px",
                    color: _color,
                    font: fontSize + "px" + " " + this.fontFamily,
                    width: parseInt(fontSize + "px") * 3 + "px",
                    height: parseInt(fontSize + "px") * 2 + "px",
                    maxWidth: __width,
                    maxHeight: __height
                });
                var textInput = TextInput.create();
                textInput.init(t, this);
                textInput.show();
                textInput.listenInput();
            }
            //canvas.removeEventListener("mouseup", canvas.leftMouseDown);
        };

        canvas.mouseMove = function(e) {
            var x = e.clientX, y = e.clientY;
            var o = canvas.overText(x, y);
            if ( o ) {
                var text = o[0];
                canvas.clear(text);
                canvas.texts.splice(o[1], 1);
                var textInput = canvas.toTextInput(text);
                textInput.preShow();
                canvas.removeEventListener("mouseup", canvas.leftMouseDown);
            }
        };


        /**add event*/
        canvas.listenTextInput = function() {
            if (canvas.listeningTextInup) return;
            canvas.listeningTextInup = true;
            canvas.style.cursor = "crosshair";
            canvas.addEventListener("mouseup", canvas.leftMouseDown);
            canvas.addEventListener("mousemove", canvas.mouseMove);
        };
        
        
        canvas.removeTextInputEvent = function() {
            canvas.listeningTextInup = false;
            canvas.style.cursor = "auto";
            canvas.removeEventListener("mouseup", canvas.leftMouseDown);
            canvas.removeEventListener("mousemove", canvas.mouseMove);
        };
        canvas.undo = function() {
            var size = canvas.texts.length;
            if( size ){
                canvas.clear(canvas.texts[size - 1]);
                canvas.texts.pop(1);
                return 1;
            }
            return 0;
        }

        return canvas;
    }
}
