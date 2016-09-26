package mjf

import upickle.default._
import upickle.Js
import spray.routing.{Directives, SimpleRoutingApp}
import akka.actor.ActorSystem
import scala.concurrent.Future

import scala.concurrent.ExecutionContext.Implicits.global
import spray.http.{HttpEntity, MediaTypes}
import MediaTypes._


object ServerApi extends Api {
  override def getGraph(name: String) = Future.successful(
    Model.Graph(Map(), Seq())
  )

  override def getMosaic(keywords: List[String]): Future[String] = {
    Future.successful("img.png")
  }
}


object AutowireServer extends autowire.Server[Js.Value, Reader, Writer] {
  def read[Result: Reader](p: Js.Value) = upickle.default.readJs[Result](p)

  def write[Result: Writer](r: Result) = upickle.default.writeJs(r)
}

object Server extends SimpleRoutingApp {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem()
    startServer("0.0.0.0", port = 8080) {
      get {
        pathSingleSlash {
          respondWithMediaType(`text/html`) {
            complete {
              mjf.html.index().toString

            }
          }
        } ~
          getFromResourceDirectory("")
      } ~
        path("assets" / Rest) { file =>
          getFromResource("public/" + file)
        } ~
        post {
          path("api" / Segments) { s =>
            extract(_.request.entity.asString) { e =>
              complete {
                AutowireServer.route[Api](ServerApi)(
                  autowire.Core.Request(
                    s,
                    upickle.json.read(e).asInstanceOf[Js.Obj].value.toMap
                  )
                ).map(upickle.json.write)
              }
            }
          }
        }
    }
  }

  def list(path: String) = {
    val chunks = path.split("/", -1)
    val prefix = "./" + chunks.dropRight(1).mkString("/")
    val files = Option(new java.io.File(prefix).list()).toSeq.flatten
    files.filter(_.startsWith(chunks.last))
  }
}
