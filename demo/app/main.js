var plotly = require("./plotly.js")

// Maybe try Plottable.js

function main() {
  $.get("links.json", add_video_links);
  window.addEventListener("hashchange", load_video);
  load_video();
}


function load_video() {
  var id = window.location.hash.slice(1)
  $.get("data/"+id+".json", draw_graph);
  // $.get("img/"+id+"/selection/indices.json", draw_images(id));
}


function add_video_links(data) {
  var list = $("#video-links");
  list.empty();
  data.forEach(v => 
    list.append($(sprintf('<li class="nav-item"><a class="nav-link" href="#%s">%s</a></li>', v.json, v.name)))
  );
  window.location.hash = data[0].json;
}


function draw_graph(data) {
  plotly.draw_line(data);
  // draw_pie(data);
}


var draw_images = (id) => (frames) => {
  var list = $("#frames");
  list.empty();
  frames.forEach(v =>
	list.append($(sprintf('<div class="col-lg-3"><img src="img/%s/5fps/%05d.jpg" class="img-fluid img-rounded"></div>', id, v)))
  )
}


var update_frame = (data) => (ev) => {
  var frameno = ev.points[0].x;
  var url = sprintf("img/%s/5fps/%05d.jpg", data.name, frameno*data.downsampled);
  document.getElementById("frame").src = url;
}

main()
