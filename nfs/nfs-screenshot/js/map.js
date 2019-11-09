/**
 * @version 1.0
 * @author cuisuqiang@163.com
 * 用于实现页面 Map 对象，Key只能是String，对象随意
 */
var Map = function(){
    this._entrys = new Array();

    this.put = function(key, value){
        if (key == null || key == undefined) {
            return;
        }
        var index = this._getIndex(key);
        if (index == -1) {
            var entry = new Object();
            entry.key = key;
            entry.value = value;
            this._entrys[this._entrys.length] = entry;
        }else{
            this._entrys[index].value = value;
        }
    };
    this.get = function(key){
        var index = this._getIndex(key);
        return (index != -1) ? this._entrys[index].value : null;
    };
    this.remove = function(key){
        var index = this._getIndex(key);
        if (index != -1) {
            this._entrys.splice(index, 1);
        }
    };
    this.clear = function(){
        this._entrys.length = 0;;
    };
    this.contains = function(key){
        var index = this._getIndex(key);
        return (index != -1) ? true : false;
    };
    this.getCount = function(){
        return this._entrys.length;
    };
    this.getEntrys =  function(){
        return this._entrys;
    };
    this._getIndex = function(key){
        if (key == null || key == undefined) {
            return -1;
        }
        var _length = this._entrys.length;
        for (var i = 0; i < _length; i++) {
            var entry = this._entrys[i];
            if (entry == null || entry == undefined) {
                continue;
            }
            if (entry.key === key) {//equal
                return i;
            }
        }
        return -1;
    };
}