/**
 *  jQuery ��չ����
 *
 *      $.Object.count( p )
 *          ��ȡһ������ĳ��ȣ���Ҫָ�������ģ�ͨ�� call/apply ����
 *          ʾ��: $.Object.count.call( obj, true );
 *          @param  {p}             �Ƿ����� null / undefined / ��ֵ
 *
 */
$.extend({
    //  ��ȡ����ĳ��ȣ���Ҫָ�������� this
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