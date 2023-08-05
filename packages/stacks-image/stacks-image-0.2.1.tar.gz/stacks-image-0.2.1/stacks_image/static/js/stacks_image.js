var StacksImage = function(){
    var fullScreenViewer = $('.stacks-image-full-screen-viewer');
    if(fullScreenViewer.length == 0){
        $('body').append('<div class="stacks-image-full-screen-viewer hide">' +
            '<div class="stacks-image-full-screen-viewer-background"></div>' +
            '<img class="stacks-image-full-screen-image" src="" alt=""/>' +
        '</div>');
    }
    this.lazyLoadImages = function(el){
        if(el){

            el.find('.lazy').lazyload({
                placeholder: "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==",
                //skip_invisible : false,
                effect: "fadeIn",
                threshold: "4000"
            });

        } else {
            $(".lazy").lazyload({
                placeholder: "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==",
                //skip_invisible : false,
                effect: "fadeIn"
            });

            $('html,body').animate({
                scrollTop: $(window).scrollTop() - 1
            }, 1);
        }
    }
};

StacksImage.prototype.init = function(){
    var showFullScreenImage = function(url){
        var fullScreenViewer = $('.stacks-image-full-screen-viewer');
        var fullScreenImage = fullScreenViewer.children('.stacks-image-full-screen-image');
        fullScreenImage.attr('src', url);
        fullScreenViewer.removeClass('hide');
        fullScreenViewer.addClass('show');
    };

    $('.stacks-image-full-screen-viewer').on('click', function(){
        $(this).removeClass('show');
        $(this).addClass('hide');
    });

    $('.image-gallery-thumbnail').on('click', function(){
        var imageContainer = $(this).children('.image-container');
        if(imageContainer.length > 0){
            var thumbnail = imageContainer.children('.thumbnail');
            if (thumbnail.length > 0) {
                var fullScreenSource = thumbnail.data('large-image');
                showFullScreenImage(fullScreenSource);
            }
        }
    });

    $('.carousel').not('.js-nested-article-group .carousel').owlCarousel({
        navigation: true,
        pagination: true,
        singleItem: true,
        slideSpeed: 500,
        //lazyLoad: false
        lazyLoad: true
    });
    this.lazyLoadImages();
};


module.exports = StacksImage;
