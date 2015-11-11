<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> bfdbab2... Set selected mode button background and fix path building
$(document).ready(function(){
		// MENU
		$('#i-menu').click(function(){
			$('#settings').hide();
      $('#menu').toggle();
<<<<<<< HEAD
    });

		// SETTINGS
		$('#i-settings').click(function(){
			$('#menu').hide();
      $('#settings').toggle();
    });

		// TOGGLE MENU/SETTINGS
    $('.list-menu a').click(function(){
        $('.list-menu').hide();
    });

		// MODE (TEXT)
		$('#m-item1, #i-text').click(function(){
      $('#mode-text').toggle(true);
			$("#video-streaming").css("margin-bottom", "60px");
    });

		// KEY
		$('#m-item2, #i-key').click(function(){
      $('#mode-text').hide();
			$("#video-streaming").css("margin-bottom", "10px");
    });

		// P2P
		$('#m-item3, #i-p2p').click(function(){
      $('#mode-text').hide();
			$("#video-streaming").css("margin-bottom", "10px");
    });

		// CAMERA
		$('#m-item4').click(function(){
			$('#video-streaming').toggle();
    });

		$('.icon').click(function(){
			$('.icon').removeClass('active');
			$(this).addClass('active');
		});
});

//
// (function (window, $) {
// 	'use strict';
//
// 	// Cache document for fast access.
// 	var document = window.document;
//
// })(window, jQuery);
=======
(function (window, $) {
	'use strict';

	// Cache document for fast access.
	var document = window.document;

	// MENU
	$('#i-menu').click(function(){
		$('#settings').hide();
        $('#menu').toggle();
=======
>>>>>>> bfdbab2... Set selected mode button background and fix path building
    });

		// SETTINGS
		$('#i-settings').click(function(){
			$('#menu').hide();
      $('#settings').toggle();
    });

		// TOGGLE MENU/SETTINGS
    $('.list-menu a').click(function(){
        $('.list-menu').hide();
    });

		// MODE (TEXT)
		$('#m-item1, #i-text').click(function(){
      $('#mode-text').toggle(true);
			$("#video-streaming").css("margin-bottom", "60px");
    });

		// KEY
		$('#m-item2, #i-key').click(function(){
      $('#mode-text').hide();
			$("#video-streaming").css("margin-bottom", "10px");
    });

		// P2P
		$('#m-item3, #i-p2p').click(function(){
      $('#mode-text').hide();
			$("#video-streaming").css("margin-bottom", "10px");
    });

		// CAMERA
		$('#m-item4').click(function(){
			$('#video-streaming').toggle();
    });
<<<<<<< HEAD
	
})(window, jQuery);
>>>>>>> 7207f9e... Mega commit
=======

		$('.icon').click(function(){
			$('.icon').removeClass('active');
			$(this).addClass('active');
		});
});

//
// (function (window, $) {
// 	'use strict';
//
// 	// Cache document for fast access.
// 	var document = window.document;
//
// })(window, jQuery);
>>>>>>> bfdbab2... Set selected mode button background and fix path building
