package mjf

import scala.concurrent.Future


trait Api {
  def getGraph(name: String): Future[Model.Graph]

  def getMosaic(keywords: List[String]): Future[String]
}
