$(document).ready(function()
{


	// INDEX TICKER
	var scroll_images = function() {
			var last = 4;
			// Animate photo list
			var photo = $($(".small_photo")[last]);
			photo.css({ marginTop: "-160px" });
			photo.prependTo("#small_photos_container");
			photo.animate({ marginTop: "0" }, 1000);
			
			// get attributes and create new hgroup
			var src = $($(".small_photo")[last]).attr("src").replace("thumbs", "filtered");
			var attrs = $($(".small_photo")[last]).attr("title").split(";");
			var hgroup = $("<hgroup class='photo_caption'><h3><a href='/view/" + attrs[0] + "/'>" + attrs[1] + "</a></h3><h5><a href='/profile/" + attrs[2] + "/'>" + attrs[3] + "</a></h5></hgroup>");
			hgroup.css({ marginTop: "0" });
			
			// Abimate big photo and hgroup
			$("#index_box > hgroup").animate({ marginTop: "0" }, 500, function() {
				$("#big_photo").fadeOut(function() {
					$(this).attr({"src" : src});
					$("#big_photo").fadeIn();
					$("#index_box > hgroup").replaceWith(hgroup)
					$("#index_box > hgroup").animate({ marginTop: "-61px" });
				});
			});
	}
	var index_box = $("div#index_box");
	if (index_box.length) {
		// Swap photos every 5s
		setInterval(function() {
			scroll_images();
		}, 5000)
	}
	
	$(".small_photo").click(function(event){
		event.preventDefault();
		scroll_images();
	});
	
	
	// AJAX PAGINATION!
	$('.pagination a').live('click', function(event){
		event.preventDefault();
		var href = $(this).attr("href");
		history.pushState(href, document.title, href);
		// ADD SPINNER
		/*
		$(document.createElement("img"))
		.attr({ src: '/uploads/graphics/spinner.gif', id: "spinner"})
		.prependTo($("#pagination_photos"))
		*/
		// AJAX MAGIC AND SWAP IMAGES
		$("#pagination_photos").animate({opacity:0}, "fast", function() 
		{ 
			$(this).remove(); 
			$.get(href, function(data){
				var new_list = $($(data).get(0));
				new_list.appendTo($("#content"));
				new_list.animate({opacity:1}, "slow", function() {
					$("#spinner").remove();
				});

			});
		});
	});

	

	// OPENID: SHOW FORM ON CLICK
	$("#openid_form").hide();
	$(".openid").click(function(event) {
		$("#openid_form").fadeToggle('fast');
	});
	
	// STYLE FILE INPUT FIELD
	var filefield = $("input#id_image");
	if (filefield.length) {
	
		
		$(document.createElement("p"))
		.html("<label for='id_image'>IMAGE:</label><input id='fake_image_input' type='text' style='width:65%;' value='No file selected' /><a href='#' style='margin-right: 0;' class='button'>Choose File</a>")
		.css({marginTop: "-88px"})
		.insertAfter($("input#id_image").parent())
		
		$("input#id_image").parent().css({opacity: 0});
		$("input#id_image").change(function() {
			var value = $(this).val().replace(/^.*(\\|\/|\:)/, '');
			$("#fake_image_input").val(value);
		});
		
	}


	// FILTER: FADE IMAGES WITH AJAX
	$(".filter").click(function(event) {
		// CANCEL CLICK
		event.preventDefault();
	
		// ADD SPINNER
		$(document.createElement("img"))
		.attr({ src: '/uploads/graphics/spinner.gif', id: "spinner"})
		.prependTo($("#main_photo_frame"))
		
		// AJAX MAGIC AND SWAP IMAGES
		$("#main_photo").animate({opacity:0}, 1000);
		var href = $(this).attr('href');
		$.get(href, function(data){
			d = new Date();
			$("#main_photo").attr("src", data + "?" + d.getTime());
			$("#main_photo").animate({opacity:1}, 1000, function() {
				$("#spinner").remove();
			});

		});
	});
	
	// FILTER, DISPLAY TOOLTIP
	$(".filter img").hover(
		function() {
			$(this).fadeTo("slow", 0.1);
		},
		function() {
			$(this).fadeTo("slow", 1);
		}
	);
		

	$(".details_button").live('click', function(event) {
		var href = $(this).attr('href');
		event.preventDefault();
		if ($("#details_content").length == 0) {
		
			
			// AJAX MAGIC AND SWAP CONTENT
			$("#main_photo").fadeOut(function() {
				$(".details_button").addClass("details_button_active");
				$.get(href, function(data){
					$(data).hide().prependTo("#photo_canvas").fadeIn("fast");
					if ($("#details_content").attr("title") == "has_map")
						$.getScript("http://maps.google.com/maps/api/js?sensor=false&callback=load_map");
				});
			});

		}
		else {
			$("#details_content").fadeOut(function(){
				$(this).remove();
				$("#main_photo").fadeIn('fast');
				$(".details_button_active").removeClass("details_button_active");
			});
		}
	});
	
	$(".edit_button").toggle( 
	function(event) {
		$(this).addClass("edit_button_active");
		event.preventDefault();
		$(".photo").animate({ left: '-=80'}, 1000, function() {
		});
		$(".filters").animate({ marginLeft: '60'}, 1000, function() {
		});
	}, 
	function(event) {
		$(this).removeClass("edit_button_active");
		event.preventDefault();
		$(".photo").animate({ left: '+=80'}, 1000, function() {
		});
		$(".filters").animate({ marginLeft: '-180'}, 1000, function() {
		});
	});
	
	$(".share_button").toggle( 
	function(event) {
		$(this).removeClass("share_button_active");
		event.preventDefault();
		$("#like_holder").slideUp();
	}, 
	function(event) {
		$(this).addClass("share_button_active");
		event.preventDefault();
		$("#like_holder").slideDown();
	});
	
	
});

function load_map(latlong) {
		var latlong = $("#map_canvas").attr("title").split(",");
		var myLatlng = new google.maps.LatLng(latlong[0], latlong[1]);
		var myOptions = {
			zoom: 8,
			center: myLatlng,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
		
		var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
		var marker = new google.maps.Marker({
			position: myLatlng, 
			map: map, 
			title:"Photo location",
			animation: google.maps.Animation.DROP
	}); 
};
