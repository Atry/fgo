package mjf

import org.scalajs.dom

import scala.scalajs.js
import scala.scalajs.js.JSConverters._
import scala.scalajs.js.JSApp
import scalatags.JsDom.all._
import scalatags.JsDom.svgTags._
import autowire._
import js.Dynamic.{global, newInstance}

//import scalatags.JsDom.svgAttrs._
import upickle.default._
import upickle.Js
import scala.concurrent.Future
import scalajs.concurrent.JSExecutionContext.Implicits.runNow
import scala.language.postfixOps
import scala.scalajs.js.annotation.JSName


import plottable.Plottable._


object ClientAPI extends autowire.Client[Js.Value, Reader, Writer] {
  override def doCall(req: Request): Future[Js.Value] = {
    dom.ext.Ajax.post(
      url = "/api/" + req.path.mkString("/"),
      data = upickle.json.write(Js.Obj(req.args.toSeq: _*))
    ).map(_.responseText)
      .map(upickle.json.read)
  }

  def read[Result: Reader](p: Js.Value) = readJs[Result](p)

  def write[Result: Writer](r: Result) = writeJs(r)
}

object TestAPI extends Api {
  override def getGraph(name: String) = Future.successful(
    Model.Graph(predictions = Map(
      "guitar" -> Seq(0.2, 0.3, 1.0, 0.6, 0.54),
      "stage" -> Seq(0.1, 0.1, 0.4, 0.6, 1.0),
      "singer" -> Seq(1.0, 0.1, 0.1, 0.1, 0.3)),
      x = Seq(1, 2, 3, 4, 5))
  )
}


object GraphView {
  def build(id: String, graph: Model.Graph) = {
    val labels = graph.predictions.keys
    val xDouble = graph.x map (_.toDouble)
    val dataset = graph.predictions.values.map(_ zip xDouble).toList

//    val datasets = dataset.map(a => new Dataset(a.toJSArray)).toJSArray


    val colorScale = new Scales.Color()
    val xScale = new Scales.Linear()
    val yScale = new Scales.Linear()

    val legend = new Components.Legend(colorScale)
    colorScale.domain(labels.toJSArray)
    legend.xAlignment("right")
    legend.yAlignment("top")
    legend.renderTo(id)

    val plots = new Components.Group[(Double, Double)]()

    val panZoom = new Interactions.PanZoom(xScale)
    panZoom.attachTo(plots)

    dataset.zip(labels).foreach { case (set, label) => plots.append(
      new Plots.Line[(Double, Double)]()
        .addDataset(new Dataset(set.toJSArray))
        .x((d: (Double, Double)) => d._2, xScale)
        .y((d: (Double, Double)) => d._1, yScale)
        .attr("stroke", colorScale.scale(label))
    )}

    plots.renderTo(id)

//    new Plots.Line[(Double, Double)]()
//      .datasets(datasets)
//      .x((d: (Double, Double)) => d._2, xScale)
//      .y((d: (Double, Double)) => d._1, yScale)
//      .renderTo(id)

  }

  def root = svg(id := "graph", width := "100%", height := "100%")
}


object App extends JSApp {

  def toolbar = {
    div(cls := "navbar navbar-default",
      a(cls := "navbar-brand", "Montreux Jazz"),
      ul(cls := "nav navbar-nav"))
  }

  def main(): Unit = {
    import dom.ext._

    val root = div(
      div(cls := "container-fluid",
        GraphView.root()
      )
    )

    dom.document.body.appendChild(root.render)

    dom.ext.Ajax.get("/assets/14MLA.json").map(_.responseText)
      .map(read[Model.Graph]) map { graph =>
      GraphView.build("svg#graph", graph)
    }
  }

}