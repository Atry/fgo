package mjf

import org.scalajs.dom.{document, ext, Event}
import org.scalajs.dom.raw.{HTMLInputElement, Node}

import scala.scalajs.js
import scala.scalajs.js.JSConverters._
import scala.scalajs.js.JSApp
import autowire._
import com.thoughtworks.binding.dom.Runtime.TagsAndTags2

import scalatags.JsDom

import scalajs.concurrent.JSExecutionContext.Implicits.runNow
import upickle.default._
import upickle.Js
import scala.concurrent.Future
import scala.language.postfixOps
import com.thoughtworks.binding.Binding
import com.thoughtworks.binding.Binding.{Var, Vars}
import com.thoughtworks.binding.dom
import plottable.Plottable._


object ClientAPI extends autowire.Client[Js.Value, Reader, Writer] {
  override def doCall(req: Request): Future[Js.Value] = {
    ext.Ajax.post(
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


object View {

  import UIModel._

  implicit def toSvgTags(t: TagsAndTags2.type) = JsDom.svgTags

  object Graph {
    def build(id: String)(graph: Model.Graph) = {
      val labels = graph.predictions.keys map (_.split(",").head)
      val xDouble = graph.x map (_.toDouble)
      val dataset = graph.predictions.values.map(_ zip xDouble).toList

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
      )
      }

      plots.renderTo(id)
    }
  }

  @dom
  def root(model: RootModel): Binding[Node] = {
    <div class="container-fluid">
      <svg id="graph"></svg>
      <video></video>
      <div id="mosaic"></div>
      <ul id="keywords" class="list-unstyled">
        {for (kw <- model.keywords) yield {
        <li>
          <a class={s"btn btn-default ${if (kw.selected.bind) "active" else ""}"}
             onclick={evt: Event => kw.selected := !kw.selected.get}>
            {kw.value} fasd
          </a>
        </li>
      }}
      </ul>
    </div>
  }

}


object UIModel {

  case class Keyword(value: String, selected: Var[Boolean])

  case class RootModel(graph: Var[Model.Graph], keywords: Vars[Keyword])

}


object Handler {

  import UIModel._

  val keywords = Vars.empty[Keyword]
  val graph = Var(Model.Graph())
  val model = RootModel(graph, keywords)

  def fetchGraph(id: String) = {
    ext.Ajax.get(s"/assets/$id.json").map(_.responseText)
      .map(read[Model.Graph]) map (g => {
      updateGraph(g)
      updateKeywords(g)
    })
  }

  def updateGraph(graph: Model.Graph) = {
    View.Graph.build("svg#graph")(graph)
  }

  def updateKeywords(graph: Model.Graph) = {
    keywords.get.clear()
    keywords.get ++= graph.predictions.keys.map(kw =>
      Keyword(kw.split(",").head, selected = Var(false)))
  }

}


object App extends JSApp {

  def main(): Unit = {

    dom.render(document.body, View.root(Handler.model))

    Handler.fetchGraph("14MLA")
  }

}