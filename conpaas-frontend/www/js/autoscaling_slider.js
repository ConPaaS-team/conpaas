/* Copyright (C) 2010-2013 by Contrail Consortium. */

$(function() {
var select = $( "#strategy" );
try{
var slider = $( "<div id='slider'></div>" ).insertAfter( select ).slider({
min: 1,
max: 5,
range: "min",
value: select[ 0 ].selectedIndex + 1,
slide: function( event, ui ) {
select[ 0 ].selectedIndex = ui.value - 1;
}
});

$( "#strategy" ).change(function() {
slider.slider( "value", this.selectedIndex + 1 );
});
}
catch(err)
{}

});