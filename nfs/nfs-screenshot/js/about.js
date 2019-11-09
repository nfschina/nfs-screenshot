$(function(){
	$( "#dialog" ).dialog({
	title : "关于我们",
	autoOpen: false,
	width: 400,
	buttons: [
		{
			text: "Ok",
			click: function() {
				$( this ).dialog( "close" );
			}
		}
	]
});

// Link to open the dialog
$( "#about" ).click(function( event ) {
	$( "#dialog" ).dialog( "open" );
	event.preventDefault();
});
});
