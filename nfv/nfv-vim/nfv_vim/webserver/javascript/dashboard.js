/*
 * Copyright (c) 2017 Wind River Systems, Inc.
*
* SPDX-License-Identifier: Apache-2.0
*
 */

var uuid = 0;
var hosts_chart_overview = {};
var instances_chart_overview = {};

var colorOkay = 'rgb(44,103,0)';
var colorWarn = 'rgb(248,148,6)';
var colorDanger = 'rgb(150,0,10)';

var colorBlack = 'rgb(0,0,0)';
var colorBlue = 'rgb(51,102,153)';
var colorGreen = 'rgb(44,103,0)';
var colorOrange = 'rgb(255,128,0)';
var colorYellow = 'rgb(181,167,40)';
var colorRed = 'rgb(150,0,10)';

var current_page_content_function = null;

var in_viewport_function = function (element) {
    var distance = element.getBoundingClientRect();
    return (distance.top >= 0 &&
            distance.bottom <=
            (window.innerHeight || document.documentElement.clientHeight));
};

var update_page_content_function = function(new_html) {

//    var st = new Date().getTime();

    $(new_html).find('.html_refresh').each(function () {
        var $new = $(this);
        var $old = $('#' + $new.attr('id'));

        if($new.html() !== $old.html()) {
            $old.replaceWith($new);
            $new.css("background-color", '#CEE3F6');

            // Reset background color
            setTimeout(function () {
                $new.css("background-color", "");
            }, 4000);
        }
    });

    $(new_html).find('.html_refresh_no_highlight').each(function () {
        var $new = $(this);
        var $old = $('#' + $new.attr('id'));

        if($new.html() !== $old.html()) {
            $old.replaceWith($new);
        }
    });

//    var et = new Date().getTime();
//    console.log(et - st);
};

var message_success_function = function(message) {
    $('.messages').html("<div class='alert alert-success alert-dismissable fade in " +
        "message'> <a class='close' data-dismiss='alert' href='#'>×</a>" +
        "<p><strong>Success: </strong>" + message + "</p></div>");
    $(".message").delay(2000).fadeOut("slow", function () { $(this).remove(); });
};

var message_error_function = function(message) {
    $('.messages').html("<div class='alert alert-danger alert-dismissable fade in " +
    "message'> <a class='close' data-dismiss='alert' href='#'>×</a>" +
    "<p><strong>Error: </strong>" + message + "</p></div>");
    $(".message").delay(5000).fadeOut("slow", function () { $(this).remove(); });
};


var get_system_content = function() {
    $.ajax({
        url: '/vim/systems',
        type: 'GET',
        jsonpCallback: 'systemCallback',
        dataType: 'jsonp',
        success: function (data) {
            if(1 <= data.systems.length) {
                $('#system-name').text(data.systems[0].name);
            }
        }
    });
};

var get_overview_content = function() {

    $('.main_nav>li>a.active').removeClass("active");
    $('a#overview_panel').addClass("active");
    $.ajax({
        url: '/vim/overview',
        type: 'GET',
        jsonpCallback: 'overviewCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Overview');

            if(current_page_content_function != get_overview_content) {
                var template = Handlebars.getTemplate('overview');
                $('div#page-content').html(template(data));

                current_page_content_function = get_overview_content;

                Chart.call(hosts_chart_overview, '#hosts_chart_overview', {
                    title: "Hosts Overview",
                    width: 900,
                    height: 300,
                    margin: {top: 30, right: 20, bottom: 30, left: 50},
                    x_axis_ticks: 20,
                    y_axis_ticks: 15,
                    series: [
                        {
                            name: 'Total Hosts',
                            renderer: 'line',
                            color: colorBlack,
                            label: 'Total Hosts',
                            data: []
                        },
                        {
                            name: 'Enabled Hosts ',
                            renderer: 'line',
                            color: colorGreen,
                            label: 'Enabled Hosts',
                            data: []
                        },
                        {
                            name: 'NFVI Enabled Hosts',
                            renderer: 'line',
                            color: colorBlue,
                            label: 'NFVI Enabled Hosts',
                            data: []
                        }
                    ]
                });

                hosts_chart_overview.initialize();

                Chart.call(instances_chart_overview, '#instances_chart_overview', {
                    title: "Instances Overview",
                    width: 900,
                    height: 400,
                    margin: {top: 30, right: 20, bottom: 30, left: 50},
                    x_axis_ticks: 20,
                    y_axis_ticks: 15,
                    series: [
                        {
                            name: 'Total Instances',
                            renderer: 'line',
                            color: colorBlack,
                            label: 'Total Instances',
                            data: []
                        },
                        {
                            name: 'Failed Instances',
                            renderer: 'line',
                            color: colorRed,
                            label: 'Failed Instances',
                            data: []
                        },
                        {
                            name: 'Enabled Instances',
                            renderer: 'line',
                            color: colorGreen,
                            label: 'Enabled Instances',
                            data: []
                        },
                        {
                            name: 'Migrating Instances',
                            renderer: 'line',
                            color: colorBlue,
                            label: 'Migrating Instances',
                            data: []
                        },
                        {
                            name: 'Rebuilding Instances',
                            renderer: 'line',
                            color: colorOrange,
                            label: 'Rebuilding Instances',
                            data: []
                        },
                        {
                            name: 'Rebooting Instances',
                            renderer: 'line',
                            color: colorYellow,
                            label: 'Rebooting Instances',
                            data: []
                        }
                    ]
                });

                instances_chart_overview.initialize();
            }

            var timestamp = new Date().getTime();

            var hosts_chart_data = [
                [{series_id: 0, id: uuid++, x: timestamp, y: data.total_hosts}],
                [{series_id: 1, id: uuid++, x: timestamp, y: data.enabled_hosts}],
                [{series_id: 2, id: uuid++, x: timestamp, y: data.nfvi_enabled_hosts}]
            ];

            hosts_chart_overview.update(hosts_chart_data);

            var instances_chart_data = [
                [{series_id: 0, id: uuid++, x: timestamp, y: data.total_instances}],
                [{series_id: 1, id: uuid++, x: timestamp, y: data.failed_instances}],
                [{series_id: 2, id: uuid++, x: timestamp, y: data.enabled_instances}],
                [{series_id: 3, id: uuid++, x: timestamp, y: data.migrating_instances}],
                [{series_id: 4, id: uuid++, x: timestamp, y: data.rebuilding_instances}],
                [{series_id: 5, id: uuid++, x: timestamp, y: data.rebooting_instances}]
            ];

            instances_chart_overview.update(instances_chart_data);
        }
    });
};

var get_hosts_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#hosts_panel').addClass("active");
    $.ajax({
        url: '/vim/hosts',
        type: 'GET',
        jsonpCallback: 'hostsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Hosts');

            var template = Handlebars.getTemplate('hosts');
            var new_html = template(data);
            var new_count = $(new_html).find('#hosts tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#hosts tr').length;

            if((current_page_content_function == get_hosts_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_hosts_content;
                $(html).html(new_html);

                var cookie = $.cookie('hosts');
                var items = cookie ? cookie.split(/,/) : new Array();
                $.each(items, function(index, value) {
                    var entry = $(html).find('#' + value);
                    var img = $(entry).prev().find("img");
                    img.attr('src', "/images/details_close.png");
                    $(entry).collapse('show');
                });
            }

            $('.image_toggle').on('hidden.bs.collapse', function () {
                var img = $(this).prev().find("img");
                img.attr('src', "/images/details_open.png");

                var cookie = $.cookie('hosts');
                var items = cookie ? cookie.split(/,/) : new Array();
                var idx = items.indexOf($(this).attr('id'));
                if(-1 != idx) {
                    items.splice(idx, 1);
                }
                $.cookie('hosts', items.join(','), {expires: 7});
            });

            $('.image_toggle').on('shown.bs.collapse', function () {
                var img = $(this).prev().find("img");
                img.attr('src', "/images/details_close.png");

                var cookie = $.cookie('hosts');
                var items = cookie ? cookie.split(/,/) : new Array();
                var idx = items.indexOf($(this).attr('id'));
                if(-1 == idx) {
                    items.push($(this).attr('id'));
                    $.cookie('hosts', items.join(','), {expires: 7});
                }
            });
        }
    });
};

var get_host_groups_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#host_groups_panel').addClass("active");
    current_page_content_function = get_host_groups_content;
    $.ajax({
        url: '/vim/host_groups',
        type: 'GET',
        jsonpCallback: 'hostGroupsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Host Groups');

            var template = Handlebars.getTemplate('host_groups');
            if(current_page_content_function == get_host_groups_content) {
                $('div#page-content').html(template(data));
            }
        }
    });
};

var get_host_aggregates_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#host_aggregates_panel').addClass("active");
    current_page_content_function = get_host_aggregates_content;
    $.ajax({
        url: '/vim/host_aggregates',
        type: 'GET',
        jsonpCallback: 'hostAggregatesCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Host Aggregates');

            var template = Handlebars.getTemplate('host_aggregates');
            if(current_page_content_function == get_host_aggregates_content) {
                $('div#page-content').html(template(data));
            }
        }
    });
};

var get_hypervisors_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#hypervisors_panel').addClass("active");
    current_page_content_function = get_hypervisors_content;
    $.ajax({
        url: '/vim/hypervisors',
        type: 'GET',
        jsonpCallback: 'hypervisorsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Hypervisors');

            var template = Handlebars.getTemplate('hypervisors');
            var new_html = template(data);
            var new_count = $(new_html).find('#hypervisors tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#hypervisors tr').length;

            if((current_page_content_function == get_hypervisors_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_hypervisors_content;
                $(html).html(new_html);
            }
        }
    });
};

var get_instances_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#instances_panel').addClass("active");
    current_page_content_function = get_instances_content;
    $.ajax({
        url: '/vim/instances',
        type: 'GET',
        jsonpCallback: 'instancesCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Instances');

            var template = Handlebars.getTemplate('instances');
            var new_html = template(data);
            var new_count = $(new_html).find('#instances tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#instances tr').length;

            if((current_page_content_function == get_instances_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_instances_content;
                $(html).html(new_html);

                var cookie = $.cookie('instances');
                var items = cookie ? cookie.split(/,/) : new Array();
                $.each(items, function(index, value) {
                    var entry = $('div#page-content').find('#' + value);
                    var img = $(entry).prev().find("img");
                    img.attr('src', "/images/details_close.png");
                    $(entry).collapse('show');
                });
            }

            $('.image_toggle').on('hidden.bs.collapse', function () {
                var img = $(this).prev().find("img");
                img.attr('src', "/images/details_open.png");

                var cookie = $.cookie('instances');
                var items = cookie ? cookie.split(/,/) : new Array();
                var idx = items.indexOf($(this).attr('id'));
                if(-1 != idx) {
                    items.splice(idx, 1);
                }
                $.cookie('instances', items.join(','), {expires: 7});
            });

            $('.image_toggle').on('shown.bs.collapse', function () {
                var img = $(this).prev().find("img");
                img.attr('src', "/images/details_close.png");

                var cookie = $.cookie('instances');
                var items = cookie ? cookie.split(/,/) : new Array();
                var idx = items.indexOf($(this).attr('id'));
                if(-1 == idx) {
                    items.push($(this).attr('id'));
                    $.cookie('instances', items.join(','), {expires: 7});
                }
            });
        }
    });
};

var get_instance_types_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#instance_types_panel').addClass("active");
    current_page_content_function = get_instance_types_content;
    $.ajax({
        url: '/vim/instance_types',
        type: 'GET',
        jsonpCallback: 'instanceTypesCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Instance Types');

            var template = Handlebars.getTemplate('instance_types');
            if(current_page_content_function == get_instance_types_content) {
                $('div#page-content').html(template(data));
            }
        }
    });
};

var get_instance_groups_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#instance_groups_panel').addClass("active");
    current_page_content_function = get_instance_groups_content;
    $.ajax({
        url: '/vim/instance_groups',
        type: 'GET',
        jsonpCallback: 'instanceGroupsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Instance Groups');

            var template = Handlebars.getTemplate('instance_groups');
            if(current_page_content_function == get_instance_groups_content) {
                $('div#page-content').html(template(data));
            }
        }
    });
};

var get_images_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#images_panel').addClass("active");
    current_page_content_function = get_images_content;
    $.ajax({
        url: '/vim/images',
        type: 'GET',
        jsonpCallback: 'imagesCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Images');

            var template = Handlebars.getTemplate('images');
            var new_html = template(data);
            var new_count = $(new_html).find('#images tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#images tr').length;

            if((current_page_content_function == get_images_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_images_content;
                $(html).html(new_html);
            }
        }
    });
};

var get_volumes_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#volumes_panel').addClass("active");
    current_page_content_function = get_volumes_content;
    $.ajax({
        url: '/vim/volumes',
        type: 'GET',
        jsonpCallback: 'volumesCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Volumes');

            var template = Handlebars.getTemplate('volumes');
            var new_html = template(data);
            var new_count = $(new_html).find('#volumes tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#volumes tr').length;

            if((current_page_content_function == get_volumes_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_volumes_content;
                $(html).html(new_html);
            }
        }
    });
};

var get_volume_snapshots_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#volume_snapshots_panel').addClass("active");
    current_page_content_function = get_volume_snapshots_content;
    $.ajax({
        url: '/vim/volume_snapshots',
        type: 'GET',
        jsonpCallback: 'volumeSnapshotsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Volume Snapshots');

            var template = Handlebars.getTemplate('volume_snapshots');
            var new_html = template(data);
            var new_count = $(new_html).find('#volume_snapshots tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#volume_snapshots tr').length;

            if((current_page_content_function == get_volume_snapshots_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_volume_snapshots_content;
                $(html).html(new_html);
            }
        }
    });
};

var get_networks_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#networks_panel').addClass("active");
    current_page_content_function = get_networks_content;
    $.ajax({
        url: '/vim/networks',
        type: 'GET',
        jsonpCallback: 'networksCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Networks');
            var template = Handlebars.getTemplate('networks');
            var new_html = template(data);
            var new_count = $(new_html).find('#networks tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#networks tr').length;

            if((current_page_content_function == get_networks_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_networks_content;
                $(html).html(new_html);
            }
        }
    });
};

var get_subnets_content = function() {
    $('.main_nav>li>a.active').removeClass("active");
    $('a#subnets_panel').addClass("active");
    current_page_content_function = get_subnets_content;
    $.ajax({
        url: '/vim/subnets',
        type: 'GET',
        jsonpCallback: 'subnetsCallback',
        dataType: 'jsonp',
        success: function (data) {
            $('#page-header-title').text('Subnets');
            var template = Handlebars.getTemplate('subnets');
            var new_html = template(data);
            var new_count = $(new_html).find('#subnets tr').length;
            var html = $('div#page-content');
            var html_count = $(html).find('#subnets tr').length;

            if((current_page_content_function == get_subnets_content) &&
               (new_count == html_count)) {
                update_page_content_function(new_html);

            } else {
                current_page_content_function = get_subnets_content;
                $(html).html(new_html);
            }
        }
    });
};

page_date_refresh = function () {
    var datetime = new Date();
    $('.datetime').html(datetime.toLocaleString());
    setTimeout(page_date_refresh, 1000);
};

page_system_banner_refresh = function () {
    $.ajax({
        url: '/vim/alarms',
        type: 'GET',
        jsonpCallback: 'systemBannerCallback',
        dataType: 'jsonp',
        success: function (data) {
            var template = Handlebars.getTemplate('system_banner');
            var new_html = template(data);
            var new_html_count = $(new_html).find('li').length;
            var html = $('#system-banner');
            var html_count = $(html).find('li').length;
            if(new_html_count != html_count) {
                $(html).html(new_html);

            } else {
                $(new_html).find('.html_refresh').each(function () {
                    var $new = $(this);
                    var $old = $('#' + $new.attr('id'));

                    if ($new.html() !== $old.html()) {
                        $old.replaceWith($new);
                    }
                });
            }
        }
    });

    setTimeout(page_system_banner_refresh, 15000);
};

page_drop_down_banner_refresh = function () {
    $.ajax({
        url: '/vim/overview',
        type: 'GET',
        jsonpCallback: 'dropDownBannerCallback',
        dataType: 'jsonp',
        success: function (data) {
            var template = Handlebars.getTemplate('drop_down_banner');
            var new_html = template(data);
            var new_html_count = $(new_html).find('li').length;
            var html = $('div.drop-down-banner');
            var html_count = $(html).find('li').length;
            if(new_html_count != html_count) {
                $(html).html(new_html);

                $('.page-header').click(function() {
                    $('.page-header-caret').toggleClass('open');
                });

                $('.page-header-caret').click(function() {
                    $(this).toggleClass('open');
                });

            } else {
                $(new_html).find('.html_refresh').each(function () {
                    var $new = $(this);
                    var $old = $('#' + $new.attr('id'));

                    if ($new.html() !== $old.html()) {
                        $old.replaceWith($new);
                        $new.css("background-color", '#253CF6');

                        // Reset background color
                        setTimeout(function () {
                            $new.css("background-color", "");
                        }, 15000);
                    }
                });
            }
        }
    });
            
    setTimeout(page_drop_down_banner_refresh, 1000);
};

page_content_refresh = function () {
    get_system_content();
    if(current_page_content_function != null) {
        current_page_content_function();
    }
    setTimeout(page_content_refresh, 5000);
};

var on_page_load = function() {
    page_date_refresh();
    page_system_banner_refresh();
    page_drop_down_banner_refresh();
    page_content_refresh();
    $.removeCookie("hosts");
    $.removeCookie("instances");
};
