package mjf


object Model {
  case class Graph(predictions: Map[String, Seq[Double]], x: Seq[Int])
  case class Mosaic()
}