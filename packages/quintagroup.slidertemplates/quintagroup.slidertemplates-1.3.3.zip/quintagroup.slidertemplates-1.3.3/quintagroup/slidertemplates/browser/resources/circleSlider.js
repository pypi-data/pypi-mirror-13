$.fn.contCarousel = function () {

  	var base = $(this);
  	base.find(".contentslider-controls").css({'display':'block'});
	base.find(".slider-wrapper-outer").css({'top':0,'display':'block'});
	$("<div class=\"bx-buttons ng-collection-buttons\"><button class=\"bx-prev\">prev</button><button class=\"bx-next\">next</button></div>").insertBefore(base.find(".slider-wrapper"));

	var slideWrap = base.find('.slider-wrapper');
	var pagerWrap = base.find('.bx-pager');
	var nextLink = base.find('.bx-next');
	var prevLink = base.find('.bx-prev');

	var is_animate = false;

	function widthCalculate () {

		var slideWidth = base.find(".slider-wrapper-outer").width();
		var pagerWidth = slideWidth/2;
		var scrollSlider = -slideWidth;
		var scrollPager = -pagerWidth*2;
		var columnGap =  parseInt($('.pager-item').css('margin-right'));
		base.find(".block-visual").css({'width':slideWidth,'height':slideWidth});
		base.find(".pager-item > .block-visual ").css({'width':pagerWidth-columnGap/2,'height':pagerWidth-columnGap/2});
		base.find(".slider-wrapper-outer").css({'height':slideWidth });
		base.find(".bx-buttons").css({'top':slideWidth-45});
		pagerWrap.css({'height':pagerWidth});
		pagerWrap.css({'left':-pagerWidth-columnGap/2})
	}

	nextLink.click(function(){

		var slideWidth = base.find(".slider-wrapper-outer").width();
		var pagerWidth = slideWidth/2;
		var columnGap =  parseInt($('.pager-item').css('margin-right'));
		var scrollSlider = -slideWidth-columnGap;
		var scrollPager = (-pagerWidth-columnGap/2)*2;

	   	if(!slideWrap.is(':animated')) {
		    slideWrap.animate({'top': scrollSlider},500 , function(){
		     slideWrap
		      .find('.item:first')
		      .appendTo(slideWrap)
		      .parent()
		      .css({'top': 0});
		      });
		    setTimeout(function(){
			   	pagerWrap.animate({'left': scrollPager}, 500, function(){
			     pagerWrap
			      .find('.pager-item:first')
			      .appendTo(pagerWrap)
			      .parent()
			      .css({'left': -pagerWidth-columnGap/2});
			      });
		   		}, 500);
		   	}
		});

	prevLink.click(function(){

		var slideWidth = base.find(".slider-wrapper-outer").width();
		var pagerWidth = slideWidth/2;
		var scrollSlider = -slideWidth;
		var columnGap =  parseInt($('.pager-item').css('margin-right'));
		var scrollPager = (-pagerWidth-columnGap/2)*2;

	   if(!slideWrap.is(':animated')) {
	   	pagerWrap
	   	 .css({'left': scrollSlider-columnGap})
	     .find('.pager-item:last')
	     .prependTo(pagerWrap)
	     .parent()
	     .animate({'left':-pagerWidth-columnGap/2}, 500);
	   	setTimeout(function(){
			slideWrap
		     .css({'top': scrollSlider})
		     .find('.item:last')
		     .prependTo(slideWrap)
		     .parent()
		     .animate({'top': 0}, 500);
	     	}, 500);
	   	}
	});

	function clickOnPager () {

		base.find('.pager-item').click(function(){

			var slideWidth = base.find(".slider-wrapper-outer").width();
			var pagerWidth = slideWidth/2;
			var columnGap =  parseInt($('.pager-item').css('margin-right'));
			var scrollSlider = -slideWidth-columnGap;
			var scrollPager = (-pagerWidth-columnGap/2)*2;

			if($(this).index()==1) {

			   	if(!slideWrap.is(':animated')) {
				    slideWrap.animate({'top': scrollSlider}, 500, function(){
				     slideWrap
				      .find('.item:first')
				      .appendTo(slideWrap)
				      .parent()
				      .css({'top': 0});
				      });
				    setTimeout(function(){
					   	pagerWrap.animate({'left': scrollPager}, 500, function(){
					     pagerWrap
					      .find('.pager-item:first')
					      .appendTo(pagerWrap)
					      .parent()
					      .css({'left': -pagerWidth-columnGap/2});
					      });
				   		}, 500);
				   	}
			} else {

				if(!slideWrap.is(':animated')) {
				slideWrap.animate({'top': scrollSlider}, 500, function(){
				    slideWrap
				      .find('.item:first')
				      .appendTo(slideWrap)
				      .parent()
				      .css({'top': 0});
				      });
				pagerWrap.animate({'left': scrollPager}, 500, function(){
			     	pagerWrap
			      	  .find('.pager-item:first')
			          .appendTo(pagerWrap)
			          .parent()
			          .css({'left': -pagerWidth-columnGap/2});
			      	});

				}
				slideWrap.animate({'top': scrollSlider}, 500, function(){
				    slideWrap
				      .find('.item:first')
				      .appendTo(slideWrap)
				      .parent()
				      .css({'top': 0});
				      });
				setTimeout(function(){
				pagerWrap.animate({'left': scrollPager}, 500, function(){
				     	pagerWrap
				      	  .find('.pager-item:first')
				          .appendTo(pagerWrap)
				          .parent()
				          .css({'left': -pagerWidth-columnGap/2});
				      	});
				}, 400);
			}
		});
	}

	widthCalculate();
	clickOnPager();

	$(window).resize(function() {
	    widthCalculate();
	    }
	  );

	}