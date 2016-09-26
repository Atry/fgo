package mjf


object Model {

  case class Graph(predictions: Map[String, Seq[Double]], x: Seq[Int])

  object Graph {
    def apply(): Graph = Graph(Map(), Seq())
  }

  case class Mosaic()

}