
var update_frame = (data) => (ev) => {
    var frameno = ev.points[0].x;
    var url = sprintf("img/%s/5fps/%05d.jpg", data.name, frameno*data.downsampled);
    document.getElementById("frame").src = url;
}


function draw_line(data) {

    var lines = data.data.map((d,i) => ({
        x: data.x,
        y: d,
        type: 'scatter',
        name: data.labels[i],
        line: {shape: 'spline'}
    })
                             );

    var layout = {
        // title: "Probablity of object appearance"
        legend: {
            yanchor: 'top',
            xanchor: 'right'
        }
    };

    Plotly.newPlot('linePlot', lines, layout);
    var lineDiv = document.getElementById("linePlot");
    lineDiv.on("plotly_hover", update_frame(data));
}


function draw_pie(data) {
    var pies = [{
        values: data.freq,
        labels: data.labels,
        type: 'pie'
    }];

    Plotly.newPlot('piePlot', pies);
}


module.exports = {draw_line, draw_pie}
