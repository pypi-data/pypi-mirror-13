    // http://stackoverflow.com/questions/4198041/jquery-smooth-scroll-to-an-anchor/12714767#12714767
    $(".scroll").click(function(event){
        event.preventDefault();
        window.history.replaceState(null, this.title, url=this.hash);
        var dest=$('#entries_scroller').scrollTop()+($(this.hash).offset().top)-60;
        $('#entries_scroller').animate({scrollTop:dest}, 300,'swing');
     });

    $(".top_of_page").click(function(event){
        $('#pages_scroller').animate({scrollTop:100}, 300,'swing');
    })

    var set_height = function(){
        $("#entries_scroller").css("height", $(window).height()-99);
        $("#pages_scroller").css("height", $(window).height()-57);
        $("#page_wrapper").css("height", $(window).height()+50);
    }

    $("#edit_button").click(function() {
        $("body").toggleClass("editing");
        $("#edit_button").toggleClass("active");

        if ($("body").hasClass("editing")) {
            $('.controllable .editable').fadeIn();
        }
        else {
            $('.controllable .editable').fadeOut();
        }
    });

    $("#calendar_button").click(function() {
        $("#calendar_button").toggleClass("active");
        if ($("#calendar_button").hasClass("active")) {
            //var midnight_today = new Date();
            var parts = "{{day.date}}".split('-');
            var calendar_date = new Date(parts[0], parts[1]-1, parts[2]);
            // 5 hours compensates for the offset from GMT
            // midnight_today.setHours(5, 0, 0, 0);
            $('.datepicker').show();
            $('.datepicker').datetimepicker({
                autoclose: true,
                initialDate: calendar_date,
                format: 'yyyy-mm-dd',
                minView: 2
            });
        }
        else {
            $('.datepicker').hide();
        }
    });

    $('.datepicker').on('changeDate', function(ev){
        var month = ev.date.getMonth() + 1;
        var day = ev.date.getDate() + 1;
        var year = ev.date.getFullYear();
        if (day < 10) {
            day = "0" + day;
        }
        if (month < 10) {
            month = "0" + month;
        }
        var date = year + "-" + month + "-" + day;
        window.location = "/admin/journal/nearest/" + date;
    });

    $( window ).resize( set_height );

    reveal_confirm_widget = function() {
        var container = $(this).parent().children()[1];
        console.log(container);
        $(container).toggle("slide");
    }

    hide_confirm_widget = function() {
        var container = $(this).parent();
        console.log(container);
        $(container).toggle("slide");
    }

    set_image_widths = function() {
        // set image widths
        var widths = $(".page_attachment a + div img").map(function(){
            return $(this).width();
        }).get();

        $(".image_container").each(function(index, value){
            $(value).css("width", widths[index]);
        });
    }

    $( document ).ready( function() {
        set_height();
        $('#pages_scroller').scrollTop(100);
        $(".delete_button").click(reveal_confirm_widget);
        $(".cancel_button").click(hide_confirm_widget);
        $('.controllable .editable').hide();
        $('.controllable .viewable').hide();

        /*$("img.lazy").lazy({
            appendScroll: $("div.image_container")
        });*/
    } );

    $(window).bind("load", function() {
        set_image_widths();
    });

    $("#entries, .image_container").hover(
        function() {
            if (!$("body").hasClass("editing")) {
                $(this).find('.controllable .viewable').fadeIn();
            }
        },
        function() {
            if (!$("body").hasClass("editing")) {
                $(this).find('.controllable .viewable').fadeOut();
            }
        }
    );

    $(".viewable a").click(function(){
        window.history.replaceState(null, this.title, url="#"+$(this).attr("anchorid"));
    });

