$(document).ready(function(){
            function update() {
                var year_slider = $('#year_slider').slider('value');
		pd = piedata[year_slider];
		if (pd == '#') return;
		$('#image').attr('src', pd);
                $('#year').text(year_slider);
                $('#movies').html(mdata[year_slider].sort().join('<br>'));
            }
    year = window.location.hash.substring(1);
    year = (year  && year > 1914 && year < 2013)? year : 1914;
           $( "#year_slider" ).slider({
                range: "min",
                value: year,
                min: 1914,
                max: 2012,
                slide: function() {
                    update();
                }
            });
    year = 
    
    update();


});
