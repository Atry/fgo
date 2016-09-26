package mjf

import org.scalajs.dom.{Event, document, ext}
import org.scalajs.dom.raw.{HTMLInputElement, HTMLVideoElement, Node}

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

//object TestAPI extends Api {
//  override def getGraph(name: String) = Future.successful(
//    Model.Graph(predictions = Map(
//      "guitar" -> Seq(0.2, 0.3, 1.0, 0.6, 0.54),
//      "stage" -> Seq(0.1, 0.1, 0.4, 0.6, 1.0),
//      "singer" -> Seq(1.0, 0.1, 0.1, 0.1, 0.3)),
//      x = Seq(1, 2, 3, 4, 5))
//  )
//}


object View {

  import UIModel._

  implicit def toSvgTags(t: TagsAndTags2.type) = JsDom.svgTags

  object Graph {
    def build(id: String, videoID: String)(graph: Model.Graph) = {
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

      val group = new Components.Group[(Double, Double)]()

      val panZoom = new Interactions.PanZoom(xScale)
      panZoom.attachTo(group)

      val plots = dataset.zip(labels).map { case (set, label) =>
        new Plots.Line[(Double, Double)]()
          .addDataset(new Dataset(set.toJSArray))
          .x((d: (Double, Double)) => d._2, xScale)
          .y((d: (Double, Double)) => d._1, yScale)
          .attr("stroke", colorScale.scale(label))
      }
      plots.foreach(pl => group.append(pl))


      val guideline = new Components.GuideLineLayer(
        Components.GuideLineLayer.ORIENTATION_VERTICAL
      ).scale(xScale)
      group.append(guideline)


      val video = document.getElementById(videoID).asInstanceOf[HTMLVideoElement]
      js.timers.setInterval(10) {
        if (!video.paused) {
          val t = video.currentTime
          val fps = 50
          val frame = t * fps
          guideline.value(frame)
        }
      }

      val pointer = new Interactions.Pointer()
      pointer.onPointerMove((p: Point) => {
        val frame = plots(0).entityNearest(p).datum._2
        //        selectedPoint1.datasets()[0].data([nearestEntityByX.datum]);
        guideline.value(frame)
        val fps = 50.0
        val t = frame / fps
        video.currentTime = t
        ()
      })
      pointer.attachTo(group)

      group.renderTo(id)
    }
  }

  @dom
  def video(name: String): Binding[Node] =
    <video controls={true} id="video" style="width:640px;height:360px;">
      <source src={s"http://localhost:8000/$name.mp4"} type="video/mp4"></source>
    </video>

  @dom
  def root(model: RootModel): Binding[Node] = {
    <div class="container-fluid">
      <svg id="graph"></svg>{video(model.name.bind).bind}<div id="mosaic"></div>
      <ul id="keywords" class="list-unstyled">
        {for (kw <- model.keywords) yield {
        <li>
          <a class={s"btn btn-default ${if (kw.selected.bind) "active" else ""}"}
             onclick={evt: Event => kw.selected := !kw.selected.get}>
            {kw.value}
          </a>
        </li>
      }}
      </ul>
      <button onclick={_: Event => Handler.updateMosaic()}>Refresh mosaic</button>
      <img src={model.mosaicFilename.bind}></img>
    </div>
  }

}


object UIModel {

  case class Keyword(value: String, selected: Var[Boolean])

  case class RootModel(name: Var[String], graph: Var[Model.Graph], keywords: Vars[Keyword], mosaicFilename: Var[String])

}


object Handler {

  import UIModel._

  val keywords = Vars.empty[Keyword]
  val graph = Var(Model.Graph())
  val name = Var("14MLA")
  val mosaicFilename = Var("")
  val model = RootModel(name, graph, keywords, mosaicFilename)

  def fetchGraph(id: String) = {
    ext.Ajax.get(s"/assets/$id.json").map(_.responseText)
      .map(read[Model.Graph]) map (g => {
      model.graph := g
      updateGraph()
      //      name := id
    })
  }

  def updateGraph() = {
    View.Graph.build("svg#graph", "video")(model.graph.get)
    keywords.get.clear()
    keywords.get ++= model.graph.get.predictions.keys.map(kw =>
      Keyword(kw.split(",").head, selected = Var(false)))
  }


  def updateMosaic() = {
    val selected = keywords.get.filter(_.selected.get).map(_.value).toList
    ClientAPI[Api].getMosaic(selected).call() map { imageFilename =>
      model.mosaicFilename := imageFilename
    }
  }
}


object App extends JSApp {

  def main(): Unit = {

    dom.render(document.body, View.root(Handler.model))

    Handler.fetchGraph("14MLA")
  }

}