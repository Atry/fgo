(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var plotly = require("./plotly.js");

// Maybe try Plottable.js

function main() {
  $.get("links.json", add_video_links);
  window.addEventListener("hashchange", load_video);
  load_video();
}

function load_video() {
  var id = window.location.hash.slice(1);
  $.get("data/" + id + ".json", draw_graph);
  // $.get("img/"+id+"/selection/indices.json", draw_images(id));
}

function add_video_links(data) {
  var list = $("#video-links");
  list.empty();
  data.forEach(v => list.append($(sprintf('<li class="nav-item"><a class="nav-link" href="#%s">%s</a></li>', v.json, v.name))));
  window.location.hash = data[0].json;
}

function draw_graph(data) {
  plotly.draw_line(data);
  // draw_pie(data);
}

var draw_images = id => frames => {
  var list = $("#frames");
  list.empty();
  frames.forEach(v => list.append($(sprintf('<div class="col-lg-3"><img src="img/%s/5fps/%05d.jpg" class="img-fluid img-rounded"></div>', id, v))));
};

var update_frame = data => ev => {
  var frameno = ev.points[0].x;
  var url = sprintf("img/%s/5fps/%05d.jpg", data.name, frameno * data.downsampled);
  document.getElementById("frame").src = url;
};

main();

},{"./plotly.js":2}],2:[function(require,module,exports){

var update_frame = data => ev => {
    var frameno = ev.points[0].x;
    var url = sprintf("img/%s/5fps/%05d.jpg", data.name, frameno * data.downsampled);
    document.getElementById("frame").src = url;
};

function draw_line(data) {

    var lines = data.data.map((d, i) => ({
        x: data.x,
        y: d,
        type: 'scatter',
        name: data.labels[i],
        line: { shape: 'spline' }
    }));

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

module.exports = { draw_line, draw_pie };

},{}]},{},[1])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJhcHAvbWFpbi5qcyIsImFwcC9wbG90bHkuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQSxJQUFJLFNBQVMsUUFBUSxhQUFSLENBQWI7O0FBRUE7O0FBRUEsU0FBUyxJQUFULEdBQWdCO0FBQ2QsSUFBRSxHQUFGLENBQU0sWUFBTixFQUFvQixlQUFwQjtBQUNBLFNBQU8sZ0JBQVAsQ0FBd0IsWUFBeEIsRUFBc0MsVUFBdEM7QUFDQTtBQUNEOztBQUdELFNBQVMsVUFBVCxHQUFzQjtBQUNwQixNQUFJLEtBQUssT0FBTyxRQUFQLENBQWdCLElBQWhCLENBQXFCLEtBQXJCLENBQTJCLENBQTNCLENBQVQ7QUFDQSxJQUFFLEdBQUYsQ0FBTSxVQUFRLEVBQVIsR0FBVyxPQUFqQixFQUEwQixVQUExQjtBQUNBO0FBQ0Q7O0FBR0QsU0FBUyxlQUFULENBQXlCLElBQXpCLEVBQStCO0FBQzdCLE1BQUksT0FBTyxFQUFFLGNBQUYsQ0FBWDtBQUNBLE9BQUssS0FBTDtBQUNBLE9BQUssT0FBTCxDQUFhLEtBQ1gsS0FBSyxNQUFMLENBQVksRUFBRSxRQUFRLGlFQUFSLEVBQTJFLEVBQUUsSUFBN0UsRUFBbUYsRUFBRSxJQUFyRixDQUFGLENBQVosQ0FERjtBQUdBLFNBQU8sUUFBUCxDQUFnQixJQUFoQixHQUF1QixLQUFLLENBQUwsRUFBUSxJQUEvQjtBQUNEOztBQUdELFNBQVMsVUFBVCxDQUFvQixJQUFwQixFQUEwQjtBQUN4QixTQUFPLFNBQVAsQ0FBaUIsSUFBakI7QUFDQTtBQUNEOztBQUdELElBQUksY0FBZSxFQUFELElBQVMsTUFBRCxJQUFZO0FBQ3BDLE1BQUksT0FBTyxFQUFFLFNBQUYsQ0FBWDtBQUNBLE9BQUssS0FBTDtBQUNBLFNBQU8sT0FBUCxDQUFlLEtBQ2hCLEtBQUssTUFBTCxDQUFZLEVBQUUsUUFBUSw0RkFBUixFQUFzRyxFQUF0RyxFQUEwRyxDQUExRyxDQUFGLENBQVosQ0FEQztBQUdELENBTkQ7O0FBU0EsSUFBSSxlQUFnQixJQUFELElBQVcsRUFBRCxJQUFRO0FBQ25DLE1BQUksVUFBVSxHQUFHLE1BQUgsQ0FBVSxDQUFWLEVBQWEsQ0FBM0I7QUFDQSxNQUFJLE1BQU0sUUFBUSxzQkFBUixFQUFnQyxLQUFLLElBQXJDLEVBQTJDLFVBQVEsS0FBSyxXQUF4RCxDQUFWO0FBQ0EsV0FBUyxjQUFULENBQXdCLE9BQXhCLEVBQWlDLEdBQWpDLEdBQXVDLEdBQXZDO0FBQ0QsQ0FKRDs7QUFNQTs7OztBQ2hEQSxJQUFJLGVBQWdCLElBQUQsSUFBVyxFQUFELElBQVE7QUFDakMsUUFBSSxVQUFVLEdBQUcsTUFBSCxDQUFVLENBQVYsRUFBYSxDQUEzQjtBQUNBLFFBQUksTUFBTSxRQUFRLHNCQUFSLEVBQWdDLEtBQUssSUFBckMsRUFBMkMsVUFBUSxLQUFLLFdBQXhELENBQVY7QUFDQSxhQUFTLGNBQVQsQ0FBd0IsT0FBeEIsRUFBaUMsR0FBakMsR0FBdUMsR0FBdkM7QUFDSCxDQUpEOztBQU9BLFNBQVMsU0FBVCxDQUFtQixJQUFuQixFQUF5Qjs7QUFFckIsUUFBSSxRQUFRLEtBQUssSUFBTCxDQUFVLEdBQVYsQ0FBYyxDQUFDLENBQUQsRUFBRyxDQUFILE1BQVU7QUFDaEMsV0FBRyxLQUFLLENBRHdCO0FBRWhDLFdBQUcsQ0FGNkI7QUFHaEMsY0FBTSxTQUgwQjtBQUloQyxjQUFNLEtBQUssTUFBTCxDQUFZLENBQVosQ0FKMEI7QUFLaEMsY0FBTSxFQUFDLE9BQU8sUUFBUjtBQUwwQixLQUFWLENBQWQsQ0FBWjs7QUFTQSxRQUFJLFNBQVM7QUFDVDtBQUNBLGdCQUFRO0FBQ0oscUJBQVMsS0FETDtBQUVKLHFCQUFTO0FBRkw7QUFGQyxLQUFiOztBQVFBLFdBQU8sT0FBUCxDQUFlLFVBQWYsRUFBMkIsS0FBM0IsRUFBa0MsTUFBbEM7QUFDQSxRQUFJLFVBQVUsU0FBUyxjQUFULENBQXdCLFVBQXhCLENBQWQ7QUFDQSxZQUFRLEVBQVIsQ0FBVyxjQUFYLEVBQTJCLGFBQWEsSUFBYixDQUEzQjtBQUNIOztBQUdELFNBQVMsUUFBVCxDQUFrQixJQUFsQixFQUF3QjtBQUNwQixRQUFJLE9BQU8sQ0FBQztBQUNSLGdCQUFRLEtBQUssSUFETDtBQUVSLGdCQUFRLEtBQUssTUFGTDtBQUdSLGNBQU07QUFIRSxLQUFELENBQVg7O0FBTUEsV0FBTyxPQUFQLENBQWUsU0FBZixFQUEwQixJQUExQjtBQUNIOztBQUdELE9BQU8sT0FBUCxHQUFpQixFQUFDLFNBQUQsRUFBWSxRQUFaLEVBQWpCIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsInZhciBwbG90bHkgPSByZXF1aXJlKFwiLi9wbG90bHkuanNcIilcblxuLy8gTWF5YmUgdHJ5IFBsb3R0YWJsZS5qc1xuXG5mdW5jdGlvbiBtYWluKCkge1xuICAkLmdldChcImxpbmtzLmpzb25cIiwgYWRkX3ZpZGVvX2xpbmtzKTtcbiAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoXCJoYXNoY2hhbmdlXCIsIGxvYWRfdmlkZW8pO1xuICBsb2FkX3ZpZGVvKCk7XG59XG5cblxuZnVuY3Rpb24gbG9hZF92aWRlbygpIHtcbiAgdmFyIGlkID0gd2luZG93LmxvY2F0aW9uLmhhc2guc2xpY2UoMSlcbiAgJC5nZXQoXCJkYXRhL1wiK2lkK1wiLmpzb25cIiwgZHJhd19ncmFwaCk7XG4gIC8vICQuZ2V0KFwiaW1nL1wiK2lkK1wiL3NlbGVjdGlvbi9pbmRpY2VzLmpzb25cIiwgZHJhd19pbWFnZXMoaWQpKTtcbn1cblxuXG5mdW5jdGlvbiBhZGRfdmlkZW9fbGlua3MoZGF0YSkge1xuICB2YXIgbGlzdCA9ICQoXCIjdmlkZW8tbGlua3NcIik7XG4gIGxpc3QuZW1wdHkoKTtcbiAgZGF0YS5mb3JFYWNoKHYgPT5cbiAgICBsaXN0LmFwcGVuZCgkKHNwcmludGYoJzxsaSBjbGFzcz1cIm5hdi1pdGVtXCI+PGEgY2xhc3M9XCJuYXYtbGlua1wiIGhyZWY9XCIjJXNcIj4lczwvYT48L2xpPicsIHYuanNvbiwgdi5uYW1lKSkpXG4gICk7XG4gIHdpbmRvdy5sb2NhdGlvbi5oYXNoID0gZGF0YVswXS5qc29uO1xufVxuXG5cbmZ1bmN0aW9uIGRyYXdfZ3JhcGgoZGF0YSkge1xuICBwbG90bHkuZHJhd19saW5lKGRhdGEpO1xuICAvLyBkcmF3X3BpZShkYXRhKTtcbn1cblxuXG52YXIgZHJhd19pbWFnZXMgPSAoaWQpID0+IChmcmFtZXMpID0+IHtcbiAgdmFyIGxpc3QgPSAkKFwiI2ZyYW1lc1wiKTtcbiAgbGlzdC5lbXB0eSgpO1xuICBmcmFtZXMuZm9yRWFjaCh2ID0+XG5cdGxpc3QuYXBwZW5kKCQoc3ByaW50ZignPGRpdiBjbGFzcz1cImNvbC1sZy0zXCI+PGltZyBzcmM9XCJpbWcvJXMvNWZwcy8lMDVkLmpwZ1wiIGNsYXNzPVwiaW1nLWZsdWlkIGltZy1yb3VuZGVkXCI+PC9kaXY+JywgaWQsIHYpKSlcbiAgKVxufVxuXG5cbnZhciB1cGRhdGVfZnJhbWUgPSAoZGF0YSkgPT4gKGV2KSA9PiB7XG4gIHZhciBmcmFtZW5vID0gZXYucG9pbnRzWzBdLng7XG4gIHZhciB1cmwgPSBzcHJpbnRmKFwiaW1nLyVzLzVmcHMvJTA1ZC5qcGdcIiwgZGF0YS5uYW1lLCBmcmFtZW5vKmRhdGEuZG93bnNhbXBsZWQpO1xuICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChcImZyYW1lXCIpLnNyYyA9IHVybDtcbn1cblxubWFpbigpXG4iLCJcbnZhciB1cGRhdGVfZnJhbWUgPSAoZGF0YSkgPT4gKGV2KSA9PiB7XG4gICAgdmFyIGZyYW1lbm8gPSBldi5wb2ludHNbMF0ueDtcbiAgICB2YXIgdXJsID0gc3ByaW50ZihcImltZy8lcy81ZnBzLyUwNWQuanBnXCIsIGRhdGEubmFtZSwgZnJhbWVubypkYXRhLmRvd25zYW1wbGVkKTtcbiAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChcImZyYW1lXCIpLnNyYyA9IHVybDtcbn1cblxuXG5mdW5jdGlvbiBkcmF3X2xpbmUoZGF0YSkge1xuXG4gICAgdmFyIGxpbmVzID0gZGF0YS5kYXRhLm1hcCgoZCxpKSA9PiAoe1xuICAgICAgICB4OiBkYXRhLngsXG4gICAgICAgIHk6IGQsXG4gICAgICAgIHR5cGU6ICdzY2F0dGVyJyxcbiAgICAgICAgbmFtZTogZGF0YS5sYWJlbHNbaV0sXG4gICAgICAgIGxpbmU6IHtzaGFwZTogJ3NwbGluZSd9XG4gICAgfSlcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKTtcblxuICAgIHZhciBsYXlvdXQgPSB7XG4gICAgICAgIC8vIHRpdGxlOiBcIlByb2JhYmxpdHkgb2Ygb2JqZWN0IGFwcGVhcmFuY2VcIlxuICAgICAgICBsZWdlbmQ6IHtcbiAgICAgICAgICAgIHlhbmNob3I6ICd0b3AnLFxuICAgICAgICAgICAgeGFuY2hvcjogJ3JpZ2h0J1xuICAgICAgICB9XG4gICAgfTtcblxuICAgIFBsb3RseS5uZXdQbG90KCdsaW5lUGxvdCcsIGxpbmVzLCBsYXlvdXQpO1xuICAgIHZhciBsaW5lRGl2ID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoXCJsaW5lUGxvdFwiKTtcbiAgICBsaW5lRGl2Lm9uKFwicGxvdGx5X2hvdmVyXCIsIHVwZGF0ZV9mcmFtZShkYXRhKSk7XG59XG5cblxuZnVuY3Rpb24gZHJhd19waWUoZGF0YSkge1xuICAgIHZhciBwaWVzID0gW3tcbiAgICAgICAgdmFsdWVzOiBkYXRhLmZyZXEsXG4gICAgICAgIGxhYmVsczogZGF0YS5sYWJlbHMsXG4gICAgICAgIHR5cGU6ICdwaWUnXG4gICAgfV07XG5cbiAgICBQbG90bHkubmV3UGxvdCgncGllUGxvdCcsIHBpZXMpO1xufVxuXG5cbm1vZHVsZS5leHBvcnRzID0ge2RyYXdfbGluZSwgZHJhd19waWV9XG4iXX0=
