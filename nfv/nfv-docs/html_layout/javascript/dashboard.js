
var get_content = function(clicked_id, page_title) {

    $('.main_nav>li>a.active').removeClass("active");
    $('a#' + clicked_id).addClass("active");

    $('#page-header-title').text(page_title);

    $(window).scrollTop(0);

    var page_content = $('div#' + clicked_id).html();
    $('div#page-content').html(page_content);

    function process_button(button, text) {
        $('#' + $(button).attr('id') + '_btn').text(text)
        .toggleClass('btn-info')
        .toggleClass('btn-default');
    }

    $('.details')
      .on('hide.bs.collapse', function (e) {
            process_button(this, 'details');
      })
      .on('show.bs.collapse', function (e) {
            process_button(this, 'close');
      });

    $('.examples')
      .on('hide.bs.collapse', function (e) {
            process_button(this, 'examples');
      })
      .on('show.bs.collapse', function (e) {
            process_button(this, 'close');
      });
};

page_date_refresh = function () {
    var datetime = new Date();
    $('.page-header h2 .datetime').html(datetime.toLocaleString());
    setTimeout(page_date_refresh, 1000);
};

var on_page_load = function() {
  $(window).scrollTop(0);
};
