/**
 *  jQuery 扩展方法
 *
 *      $.Object.count( p )
 *          获取一个对象的长度，需要指定上下文，通过 call/apply 调用
 *          示例: $.Object.count.call( obj, true );
 *          @param  {p}             是否跳过 null / undefined / 空值
 *
 */
$.extend({
    //  获取对象的长度，需要指定上下文 this
    Object:     {
        count: function( p ) {
            p = p || false;

            return $.map( this, function(o) {
                if( !p ) return o;

                return true;
            } ).length;
        }
    }
});