package mjf


object Model {

  case class Graph(predictions: Map[String, Seq[Double]], x: Seq[Int])

  object Graph {
    def apply(): Graph = Graph(Map(), Seq())
  }

  case class Mosaic()

  case class Maps(height: Int, width: Int, fps: Double, maps: Seq[Seq[Int]])
  object Maps {
    def apply(): Maps = Maps(0,0,0,Seq())
  }
}