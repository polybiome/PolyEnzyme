var images = new Array()
function preload() {
	for (i = 0; i < preload.arguments.length; i++) {
		images[i] = new Image()
		images[i].src = preload.arguments[i]
	}
}
preload(
	"img/animationInterrogation.gif",
	"img/bacteriaFunny.gif",
	"img/bacteriaFunnyMini.gif"
)
$(document).ready(function(){

		if ($(window).width() < 767){
			var pillSize = 35;
			$('.navbar').css({
		     'transform' : 'translate(0px, '+ 0 +'px)'
			});
		}else{
			var pillSize = 18;
		};

var togglePill = 0
var viewportHeight = $('.mainViewport').height() + 300;
	if ($(window).width() > 767){
		$('.pill').css('background-size', ''+pillSize+'%');	

		
		var sec2Trigger = $('.section2').offset().top - ($(window).height());
		$('.navbar').css({
				  'transform' : 'translate(0px, '+ 0 +'px)'
				});

		$('.textAbobePills').css({
				  'opacity' : '100'
				});

		$('.textAbobePills hr').css({
				  'width' : '150%','margin-left' : '-25%'
				});
	};
		$(window).scroll(function(){

			var disTop = $(this).scrollTop();
	if ($(window).width() > 767){
			if (disTop <= viewportHeight) {
			}
			$('.logo').css({
				  'transform' : 'translate(0px, '+ -disTop/2 +'px)'
			});
			$('.pill').css({
				  'transform' : 'translate(0px, '+ disTop*1.5  +'px)'
			});

			if (disTop >= 200){
				$(".navbar-fixed-top").addClass('navbarEffect');
			} else{
				$(".navbar-fixed-top").removeClass('navbarEffect');
			};
			if (disTop >= 100){
				$('.textAbobePills hr').css({
				  'width' : '0%','margin-left' : '50%'
				});
			}else{
				$('.textAbobePills hr').css({
				  'width' : '150%','margin-left' : '-25%'
				});
			};
			if(disTop == 0){
				$('.textViewport').css({
					  'opacity' : '1'
				});
			}else{
				$('.textViewport').css({
					  'opacity' : ''+ Math.max(0,(viewportHeight-disTop-600)/viewportHeight)+''
				});
			};
			if(disTop > $('.section1').offset().top - ($(window).height() / 1.2)){
				$('.whatItIs').css({
				  'opacity' : '1'
				});
				$('.title1').css({
				  'transform' : 'translate(0px, 0px)'
				});
				setTimeout(function(){$('.section1').css('background-image', 'url(img/animationInterrogation.gif)');}, 500);
				
			};
			disPill = $('.pill').offset().top
			if(disTop > sec2Trigger){
				$('.scienceGirlExplains').css({
				  'opacity' : '1'
				});
				$('.title3').css({
				  'transform' : 'translate(0px,0px)'
				});
				$('.pill').css({
				   'transform' : 'translate(0px, '+ disPill +'px)'
				});
				$('.logo').css({
				  'transform' : 'translate(0px, 0px)'
				});
			};
			if(disTop > $('.section2').offset().top){
				$('.pill').css('background-image', 'url(img/meat1.png)');
				
				$('.pill').css('background-size', '30%');
			}else{
				$('.pill').css('background-image', 'url(img/logoPill.png)');
				$('.pill').css('background-size', ''+pillSize+'%');	
			};
			if(disTop > $('.section2').offset().top - 0.2*($(window).height())){
				$('.scienceGirl').css({
					'transform' : 'translate(0px,0px)'
				});
			};
			sec3Target = $('.section3').offset().top - ($(window).height()*0.1)

			if(disTop > sec3Target){
				$('.pill').css({
					'transform' : 'translate(0%, '+sec3Target+'px)'
				});			
			};

			if(disTop > $('.manyMeats').offset().top - ($(window).height() / 1.2)) {
				$('.title2').css({
					'transform' : 'translate(20%,0%)'
				});

				$('.scienceGuyExplains').css({
				  'opacity' : '1'
				});
				
			    $('.manyMeats img').each(function(i){
				      setTimeout(function(){
				        $('.manyMeats img').eq(i).addClass('is-showing');
				      }, (1000 * (Math.exp(i * 0.14))) - 1000);
				    });
		 	};

		 	sec4Target = $('.section4').offset().top - ($(window).height() / 1.2)
		 	if(disTop > sec4Target){
				$('.scienceGuyExplains2').css({
					'transform' : 'translate(0px,0px)','opacity' : '1'
				});			
			};
			sec5Target = $('.section5').offset().top - ($(window).height() / 1.2)
		 	if(disTop > sec5Target){
				$('.scienceGuyExplains3').css({
					'opacity' : '1'
				});
				$('.title5').css({
					'transform' : 'translate(0px,0px)'
				});
				if ($(window).width() < 767){
					setTimeout(function(){$('.section5').css('background-image', 'url(img/bacteriaFunnyMini.gif)');}, 1000);
				}else{
					setTimeout(function(){$('.section5').css('background-image', 'url(img/bacteriaFunny.gif)');}, 1000);
				};	
			};
			if(disTop > sec5Target + ($(window).height() / 1.1)){
				$('.scienceGuy').css({
					'transform' : 'translate(-700px,0px)'
				});
			}else{
				$('.scienceGuy').css({
					'transform' : 'translate(0px,0px)'
				});			
			};

			if(disTop > $('.section6').offset().top - ($(window).height() / 1.2)) {
				$('.title6').css({
					'transform' : 'translate(30%,0%)'
				});
				$('.text6').css({
					'opacity' : '1'
				});
			};

			secFinalTarget = $('.secFinal').offset().top - ($(window).height() / 1.2)
			if(disTop > $('.secFinal').offset().top - (0.1*$(window).height())){
				togglePill = 1;
				if ($(window).width() < 767){
					$('.pill2').css({
						'background-position' : '40% center','background-attachment' : 'scroll'
					});
				}else{
					$('.pill2').css({
						'background-position' : 'center','background-attachment' : 'scroll'
					});
				};	
				$('.finalText1').css({
					'opacity' : '1'
				});
				$('.finalText2').css({
					'transform' : 'translate(0px,0px)'
				});			
			};
			if(togglePill&&disTop<secFinalTarget + (0.5*$(window).height())){
				togglePill = 0;
				if ($(window).width() < 767){
					$('.pill2').css({
						'background-position' : '100% center','background-attachment' : 'fixed'
					});
				}else{
					$('.pill2').css({
						'background-position' : '90% center','background-attachment' : 'fixed'
					});
				};	
			};
	}else{
		if (disTop >= 200){
			$(".navbar-fixed-top").addClass('navbarEffect');
		} else{
			$(".navbar-fixed-top").removeClass('navbarEffect');
		};
		if(disTop > $('.section1').offset().top - ($(window).height() / 1.2)){
				setTimeout(function(){$('.section1').css('background-image', 'url(img/animationInterrogation.gif)');}, 500);
			};
		sec5Target = $('.section5').offset().top - ($(window).height() / 1.2)
		if(disTop > sec5Target){
			if ($(window).width() < 767){
				setTimeout(function(){$('.section5').css('background-image', 'url(img/bacteriaFunnyMini.gif)');}, 1000);
			}else{
				setTimeout(function(){$('.section5').css('background-image', 'url(img/bacteriaFunny.gif)');}, 1000);
			};	
		};	
		}
	});
});


smoothScroll.init({
	speed: 1000,
	easing: 'easeInOutQuad',
	updateURL: false,
	offset: 30,
});