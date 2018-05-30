/*
 * Copyright (c) 2017 Wind River Systems, Inc.
*
* SPDX-License-Identifier: Apache-2.0
*
 */

Handlebars.getTemplate = function (name) {
    if (Handlebars.templates === undefined || Handlebars.templates[name] === undefined) {
        $.ajax({
            url: '/templates/' + name + '.handlebars',
            datatype: 'text/javascript',
            success: function (response, status, jqXHR) {
                if (Handlebars.templates === undefined) {
                    Handlebars.templates = {};
                }
                Handlebars.templates[name] = Handlebars.compile(response);
            },
            async: false
        });
    }
    return Handlebars.templates[name];
};

Handlebars.registerHelper('ifCompare', function (v1, operator, v2, options) {

    switch (operator) {
        case '==':
            return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===':
            return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '<':
            return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=':
            return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>':
            return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=':
            return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&':
            return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
        default:
            return options.inverse(this);
    }
});

Handlebars.registerHelper('convertSecsToDate', function (secs) {

    var d = new Date(0, 0, 0);
    d.setSeconds(+secs);
    var date_string = '';

    if (0 < d.getHours()) {
        if (1 == d.getHours()) {
            date_string += d.getHours() + ' hour '
        } else {
            date_string += d.getHours() + ' hours '
        }
    }

    if (0 < d.getMinutes()) {
        if (1 == d.getMinutes()) {
            date_string += d.getMinutes() + ' minute '
        } else {
            date_string += d.getMinutes() + ' minutes '
        }
    }

    if (0 < d.getSeconds()) {
        if (1 == d.getSeconds()) {
            date_string += d.getSeconds() + ' second '
        } else {
            date_string += d.getSeconds() + ' seconds '
        }
    }

    return date_string;
});


Handlebars.registerHelper("log", function(something) {
  console.log(something);
});