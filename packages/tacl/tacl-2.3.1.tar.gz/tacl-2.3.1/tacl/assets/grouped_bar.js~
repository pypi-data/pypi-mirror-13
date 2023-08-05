function groupedBarChart() {
    var margin = {top: 20, right: 20, bottom: 100, left: 40},
        width = 960 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    var x0 = d3.scale.ordinal().rangeRoundBands([0, width], .1);

    var x1 = d3.scale.ordinal();

    var y = d3.scale.linear().range([height, 0]);

    var color = d3.scale.ordinal().range(["#D8B365", "#5AB4AC"]);

    var xAxis = d3.svg.axis().scale(x0).orient("bottom");

    var yAxis = d3.svg.axis().scale(y).orient("left")
        .tickFormat(d3.format(".2s"));

    function chart(selection) {
        selection.each(function(data) {
            var groupNames = d3.keys(data[0]).filter(function(key) {
                return key !== "";
            });

            data.forEach(function(d) {
                d.groups = groupNames.map(function(name) {
                    return {name: name, value: +d[name]};
                });
            });
        });
    }

    return chart;
}
