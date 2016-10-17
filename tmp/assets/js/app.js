$(document).ready(function () {
    var BATT_MAX, BATT_MIN, BATT_ICONS,
        colors, main, progress, refresh, $items, graph_data;
    BATT_MIN = 40;
    BATT_MAX = 54;
    BATT_ICONS = [
        'battery-empty', 'battery-quarter', 'battery-half', 'battery-three-quarters', 'battery-full'
    ];

    $items = {
        in: $('#in'),
        out: $('#out'),
        batt: $('#battery'),
        load: $('#load'),
        batt_status: $('#batt_status'),
        grid_status: $('#grid_status')
    };

    graph_data = {
        in: [],
        out: [],
        batt: [],
        load: []
    };

    colors = {
        in: '#276000',
        out: '#A20B02',
        load: '#FB6600',
        batt: '#09629E'
    };

    progress = function (elem, val, label, type) {
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

    main = function () {
        $.getJSON('/latests/ep3000-status.json?t=' + Date.now()).then(function (json) {

            refresh.statuses(json);

            refresh.battery(json);
            refresh.load(json);
            refresh.in(json);
            refresh.out(json);

            setTimeout(main, 1000);
        });
    };

    function to_js_timestamp(unix) {
        return Math.round(unix * 1000);
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


    function graph(name, unix_ts, value, range, options) {
        var data = graph_data[name],
            $graph = $items[name].find('.graph'),
            start = moment(),
            delete_count = 0;
        start = start.subtract.apply(start, range).valueOf();

        data.push([to_js_timestamp(unix_ts), value === 0 ? undefined : value]);
        if (data.length >= 2) {
            // GC
            while (data[delete_count][0] < start && delete_count + 1 < data.length) delete_count++;
            data.splice(0, delete_count);
            $.plot(
                $graph,
                [{data: data, color: colors[name]}],
                $.extend(
                    true, {
                        xaxis: {
                            mode: "time",
                            timezone: "browser",
                            min: start,
                            max: Date.now()
                        }
                    }, options || {}
                )
            );
        }
    }

    refresh = {
        battery: function (json) {
            var batt, batt_percent, on_solar;
            batt = json.payload.battery_voltage;
            batt_percent = percentize(batt, BATT_MIN, BATT_MAX);
            on_solar = json.payload.output_load > 0;
            progress($items.batt.find('.progress'), batt_percent, null, batt_type(batt_percent));
            $items.batt.find('.badge').text(batt + ' V');
            $items.batt.tbsTypeClass(on_solar ? 'success' : 'warning', 'panel');
            $items.batt.find('.title').text('Battery (' + (on_solar ? 'off grid' : 'on grid') + ')');

            graph('batt', json.timestamp, batt, [1, 'hour'], {
                yaxis: {
                    axisLabel: "Volts",
                    tickDecimals: 1
                }
            });
        },

        load: function (json) {
            var load_percent = json.payload.output_load, load;
            load = load_percent * 6 / 100;
            progress($items.load.find('.progress'), load_percent, null, load_type(load_percent));
            $items.load.find('.badge').text(load_percent === 0 ? 'grid' : (load + ' kW'));

            graph('load', json.timestamp, load, [1, 'hour'], {
                yaxis: {
                    axisLabel: "Kilo Watts",
                    tickDecimals: 1
                }
            });
        },

        in: function (json) {
            var volts = json.payload.input_voltage;
            $items.in.tbsTypeClass(volts == 0 ? 'danger' : 'default', 'panel');
            $items.in.find('.badge').text(volts + ' V');
            graph('in', json.timestamp, volts, [1, 'hour'], {
                yaxis: {
                    axisLabel: "Volts",
                    tickDecimals: 1
                }
            });
        },

        out: function (json) {
            var volts = json.payload.output_voltage;
            $items.out.find('.badge').text(volts + ' V');
            graph('out', json.timestamp, volts, [1, 'hour'], {
                yaxis: {
                    axisLabel: "Volts",
                    tickDecimals: 1
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
        }
    };

    main();
});
