var image_dir = 'images';
$(document).ready(function(){ 
  var i = 0;
  for (i=1914;i <= 2012; ++i) {
     $('#everything_nodetail').append('<img class="hover" attr-year="'+i+'" src="' + image_dir + '/nogrey.colour.nolight.nosat.' + i + '.png" />');
  }
  for (i=1914;i <= 2012; ++i) {
     $('#everything_detail').append('<img class="hover" attr-year="'+i+'" src="' + image_dir + '/nogrey.colour.light.sat.' + i + '.png" />');
  }

    var detail = function() {
	$('#everything_detail').show();
	$('#everything_nodetail').css('display', 'none');
	$('#show_detail').hide();
	$('#show_nondetail').show();
	return false;
    };
    var nondetail = function() {
	$('#everything_detail').css('display', 'none');
	$('#everything_nodetail').show();
	$('#show_detail').show();
	$('#show_nondetail').hide();
	return false;
    };
    $('#show_detail').bind('click', detail);
    $('#show_nondetail').bind('click', nondetail);

    // make sure the html we added above has been commited to the DOM
    $('#everything_detail').offset();
    $('#everything_nondetail').offset();

    if (window.location.hash == '#nondetail') {
	setTimeout(1, nondetail());
    } else {
	setTimeout(1, detail());
    }


    $('.hover').bind('mouseover', function() {
	$(this).addClass('hovering');
	return false;
    });
    $('.hover').bind('mouseout', function() {
	$(this).removeClass('hovering');
	return false;
    });
    $('.hover').bind('click', function() {
	window.location='index.html#' + $(this).attr('attr-year');
	return false;
    });

});
