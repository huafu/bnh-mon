window.bnh = {};

$(document).ready(function () {
    var BATT_MAX, BATT_MIN, BATT_ICONS, GRAPH_RANGE, START,
        colors, main, progress, refresh, $items, graph_series, alarms, statuses;
    BATT_MIN = 40;
    BATT_MAX = 54;
    GRAPH_RANGE = [30, 'minute'];
    BATT_ICONS = [
        'battery-empty', 'battery-quarter', 'battery-half', 'battery-three-quarters', 'battery-full'
    ];

    window.bnh.$items = $items = {
        in_out: $('#in_out'),
        batt: $('#battery'),
        load: $('#load'),
        batt_status: $('#batt_status'),
        grid_status: $('#grid_status'),
        time: $('#time'),
        summary: $('#summary')
    };

    window.bnh.alarms = alarms = {
        low_batt: {
            delay: 10 * 1000,
            timer: null,
            sound: new Audio('/assets/sounds/low-batt.wav')
        },
        power_down: {
            delay: 30 * 1000,
            timer: null,
            sound: new Audio('/assets/sounds/power-down.wav')
        }
    };

    window.bnh.statuses = statuses = {
        on_battery: {ranges: [], last: undefined},
        power_down: {ranges: [], last: undefined}
    };

    window.bnh.graph_series = graph_series = {
        in: {data: [], lines: {fill: false}},
        out: {data: [], lines: {fill: false}},
        batt: {data: []},
        load: {data: []}
    };

    window.bnh.colors = colors = {
        in: '#276000',
        out: '#A20B02',
        load: '#FB6600',
        batt: '#09629E'
    };

    window.bnh.progress = progress = function (elem, val, label, type) {
        if (label == null) {
            label = val + '%';
        }
        $(elem).find('.progress-bar')
            .attr('aria-valuenow', val)
            .width(val + '%')
            .text(label)
            .tbsTypeClass(type, 'progress-bar');
    };

    function pick_for_percent(array, percent) {
        return array[Math.round(percent * (array.length - 1) / 100)];
    }

    $.fn.tbsTypeClass = function (type, prefix) {
        var $this = $(this), i, t, types = ['default', 'success', 'info', 'warning', 'danger'];
        prefix = prefix ? prefix + '-' : '';
        for (i in types) {
            t = types[i];
            $this[type === t ? 'addClass' : 'removeClass'](prefix + t);
        }
        return $this;
    };

    window.bnh.main = main = function () {
        $.getJSON('/latests/ep3000-status.json?t=' + Date.now()).then(function (json) {
            if (!START)START = Date.now();
            for (var k in refresh) {
                try {
                    refresh[k](json);
                } catch (e) {
                    console.log(e);
                    setTimeout(function () {
                        throw e;
                    }, 1);
                }
            }

            setTimeout(main, 1000);
        });
    };

    function to_js_timestamp(unix) {
        return Math.round(unix * 1000);
    }

    function alarm_ticker() {
        if (!this.ticker) this.ticker = alarm_ticker;
        this.timer = setTimeout(this.ticker.bind(this), this.delay || 30000);
        this.sound.play();
    }

    function alarm(obj, status) {
        if (status && !obj.timer) {
            alarm_ticker.bind(obj)();
        } else if (!status && obj.timer) {
            clearTimeout(obj.timer);
            obj.timer = null;
        }
    }

    function batt_type(percent) {
        switch (true) {
            case (percent === 100):
                return 'success';
            case (percent < 5):
                return 'danger';
            case (percent < 20):
                return 'warning';
            case (percent < 60):
                return 'info';
            default:
                return null;
        }
    }

    function status(obj, status, now) {
        if (!now) now = Date.now();
        status = Boolean(status);
        if (obj.last === undefined) {
            obj.last = status;
            obj.since = now
        } else if (obj.last !== status) {
            obj.last = status;
            obj.ranges.push([obj.since, now - obj.since, !status]);
            obj.since = now;
        }
    }

    function status_totals(obj, since) {
        var totals = {on: 0, off: 0}, i, r;
        if (!since) since = 0;
        for (i in obj.ranges) {
            r = obj.ranges[i];
            if (r[0] < since) continue;
            totals[r[2] ? 'on' : 'off'] += r[1];
        }
        totals[obj.last ? 'on' : 'off'] += Math.max(since, Date.now()) - obj.since;
        totals.on = moment.duration(totals.on);
        totals.off = moment.duration(totals.off);
        return totals;
    }


    function load_type(percent) {
        switch (true) {
            case (percent > 90):
                return 'danger';
            case (percent > 40):
                return 'warning';
            case (percent > 20):
                return null;
            case (percent > 10):
                return 'info';
            default:
                return 'success';
        }
    }

    function percentize(value, min, max) {
        return Math.min(100, Math.max(0, Math.round((value - min) * 100 / (max - min))));
    }


    function graph(graph_name, unix_ts, values, range, options) {
        var opt, new_item, series, i, j, s, v, delete_count, ymin, ymax,
            $graph = $items[graph_name].find('.graph'),
            start = moment(),
            //last_update = $graph.data('lastUpdate'),
            now = Date.now(),
            plot = $graph.data('plotObject'),
            autoMinMax = $graph.data('autoMinMax'),
            series_names = Object.keys(values);

        if (!range) range = GRAPH_RANGE;
        start = start.subtract.apply(start, range).valueOf();

        series = [];
        for (i in series_names) {
            if (!plot) {
                graph_series[series_names[i]] = $.extend(
                    true,
                    {color: colors[series_names[i]], lines: {fill: true}},
                    graph_series[series_names[i]]
                );
            }
            series.push(s = graph_series[series_names[i]]);
            v = values[series_names[i]];
            new_item = [to_js_timestamp(unix_ts), v === 0 ? undefined : v];
            if (!s.data.length || s.data[s.data.length - 1][0] !== new_item[0]) {
                s.data.push(new_item);
            }
            delete_count = 0;
            while (s.data[delete_count][0] < start - 60 * 1000 && delete_count + 1 < s.data.length) {
                delete_count++;
            }
            s.data.splice(0, delete_count);
            if (autoMinMax) {
                for (j in s.data) {
                    v = s.data[j][1];
                    if (v === undefined) continue;
                    ymin = ymin ? Math.min(ymin, v) : v;
                    ymax = ymax ? Math.max(ymax, v) : v;
                }
            }
        }
        if (ymin !== undefined) {
            v = (ymax - ymin) / 20;
            ymin -= v;
            ymax += v;
        }

        if (!plot) {
            plot = $.plot(
                $graph,
                series,
                $.extend(
                    true, {
                        xaxis: {
                            mode: "time",
                            timezone: "browser",
                            min: start,
                            max: Date.now()
                        },
                        yaxis: {
                            min: ymin,
                            max: ymax
                        }
                    }, options || {}
                )
            );
            $graph.data('plotObject', plot);
        } else {
            opt = plot.getAxes().xaxis.options;
            opt.min = start;
            opt.max = now;
            if (ymin !== undefined) {
                opt = plot.getAxes().yaxis.options;
                opt.min = ymin;
                opt.max = ymax;
            }
            plot.setupGrid();
        }

        plot.setData(series);
        plot.draw();
        $graph.data('lastUpdate', Date.now());
    }

    window.bnh.refresh = refresh = {
        time: function (json) {
            $items.time.text(moment().format('llll'));
        },

        summary: function (json) {
            var totals, $s = $items.summary, on_batt,
                now = Date.now(),
                start_of_day = moment().startOf('day').valueOf();
            status(statuses.power_down, json.payload.input_voltage == 0, to_js_timestamp(json.timestamp));
            status(statuses.on_battery, on_batt = (json.payload.output_load > 0), to_js_timestamp(json.timestamp));
            totals = {
                today: status_totals(statuses.on_battery, start_of_day),
                all: status_totals(statuses.on_battery)
            };
            $s.find('.on_grid_since').text(on_batt ? '-' : moment(statuses.on_battery.since).fromNow(true));
            $s.find('.on_batt_since').text(on_batt ? moment(statuses.on_battery.since).fromNow(true) : '-');

            $s.find('.total_grid_today').html(
                totals.today.off.format('d [days] H:m:s') +
                ' (<code>' + percentize(totals.today.off, 0, now - start_of_day) + '%</code>)'
            );
            $s.find('.total_batt_today').html(
                totals.today.on.format('d [days] H:m:s') +
                ' (<code>' + percentize(totals.today.on, 0, now - start_of_day) + '%</code>)'
            );

            $s.find('.since').text(moment(START).fromNow(true));
            $s.find('.total_grid').html(
                totals.all.off.format('d [days] H:m:s') +
                ' (<code>' + percentize(totals.all.off, 0, now - START) + '%</code>)'
            );
            $s.find('.total_batt').html(
                totals.all.on.format('d [days] H:m:s') +
                ' (<code>' + percentize(totals.all.on, 0, now - START) + '%</code>)'
            );
            $s.find('.batt').tbsTypeClass(on_batt ? 'info' : null, 'bg');
            $s.find('.grid').tbsTypeClass(on_batt ? null : 'info', 'bg');
        },

        battery: function (json) {
            var batt, batt_percent, on_solar;
            batt = json.payload.battery_voltage;
            batt_percent = percentize(batt, BATT_MIN, BATT_MAX);
            on_solar = json.payload.output_load > 0;
            progress($items.batt.find('.progress'), batt_percent, null, batt_type(batt_percent));
            $items.batt.find('.badge').text(batt + ' V');
            $items.batt.tbsTypeClass(on_solar ? 'success' : 'warning', 'panel');
            $items.batt.find('.title').text('Battery (' + (on_solar ? 'off grid' : 'on grid') + ')');

            graph('batt', json.timestamp, {batt: batt}, null, {
                yaxis: {
                    axisLabel: "Volts",
                    tickDecimals: 1,
                    min: BATT_MIN - 4
                }
            });
        },

        load: function (json) {
            var load_percent = json.payload.output_load, load;
            load = load_percent * 6 / 100;
            progress($items.load.find('.progress'), load_percent, null, load_type(load_percent));
            $items.load.find('.badge').text(load_percent === 0 ? 'grid' : (load + ' kW'));

            graph('load', json.timestamp, {load: load}, null, {
                yaxis: {
                    axisLabel: "Kilo Watts",
                    tickDecimals: 1
                }
            });
        },

        in_out: function (json) {
            var in_volts = json.payload.input_voltage,
                out_volts = json.payload.output_voltage;
            $items.in_out.tbsTypeClass(in_volts == 0 ? 'danger' : 'default', 'panel');
            $items.in_out.find('.badge.input .text').text(in_volts + ' V');
            $items.in_out.find('.badge.output .text').text(out_volts + ' V');
            $items.in_out.find('.badge.input').css('background-color', colors.in);
            $items.in_out.find('.badge.output').css('background-color', colors.out);
            graph('in_out', json.timestamp, {out: out_volts, in: in_volts}, null, {
                yaxis: {
                    axisLabel: "Volts",
                    tickDecimals: 1,
                    min: 195
                }
            });
        },

        statuses: function (json) {
            var batt_percent = percentize(json.payload.battery_voltage, BATT_MIN, BATT_MAX),
                power_down = json.payload.input_voltage == 0;
            $items.batt_status.find('i.fa')
                .removeClass()
                .addClass('fa fa-fw fa-' + pick_for_percent(BATT_ICONS, batt_percent))
                .tbsTypeClass(batt_type(batt_percent), 'text');
            $items.grid_status.find('i.fa')
                .removeClass()
                .addClass('fa fa-fw fa-' + (power_down ? 'exclamation-triangle' : 'building'))
                .addClass(power_down ? 'text-danger' : 'text-success');
            $items.grid_status.find('.text').text(
                power_down && statuses.power_down.since
                    ? moment(statuses.power_down.since).fromNow()
                    : ''
            );

            alarm(alarms.low_batt, json.payload.battery_voltage <= 44);
            alarm(alarms.power_down, power_down);
        }
    };

    main();
});
