package mjf.plottable

import scala.scalajs.js
import scala.scalajs.js.annotation.JSName

object Point {
  def apply(x: Double, y: Double): Plottable.Point =
    js.Dynamic.literal(x = x, y = y).asInstanceOf[Plottable.Point]
}

object RectPoint {
  def apply(x: Int, y: Int, v: Int): Plottable.RectPoint =
    js.Dynamic.literal(x = x, y = y, v = v).asInstanceOf[Plottable.RectPoint]
}


@js.native
object Plottable extends js.Object {

  @js.native
  trait Point extends js.Object {
    val x: Double = js.native
    val y: Double = js.native
  }


  @js.native
  trait RectPoint extends js.Object {
    val x: Int = js.native
    val y: Int = js.native
    val v: Int = js.native
  }

  @js.native
  class Dataset[T](data: js.Array[T]) extends js.Object {
    def onUpdate(): Unit = js.native

    def data(data: js.Array[T]): Unit = js.native
  }

  @js.native
  object Interactions extends js.Object {

    @js.native
    trait Interaction extends js.Object {
      def attachTo(c: Components.Component): Unit = js.native
    }

    @js.native
    class PanZoom(xScale: Scales.Scale) extends Interaction

    @js.native
    class Pointer() extends Interaction {
      def onPointerEnter(cb: js.Function1[Point, Unit]): Unit = js.native

      def onPointerMove(cb: js.Function1[Point, Unit]): Unit = js.native
    }

  }


  @js.native
  object Scales extends js.Object {

    @js.native
    trait Scale extends js.Object {
      def domain(a: js.Array[_]): Scale = js.native

      def range(r: js.Array[_]): Scale = js.native
    }

    @js.native
    class Category() extends Scale

    @js.native
    class Linear() extends Scale

    @js.native
    class Color() extends Scale {
      def scale(s: String): String = js.native
    }

    @js.native
    class InterpolatedColor() extends Scale

  }

  @js.native
  object Components extends js.Object {

    @js.native
    trait Component extends js.Object {
      def renderTo(id: String): Unit = js.native
    }

    @js.native
    class Legend(s: Scales.Scale) extends Component {
      def xAlignment(s: String): Unit = js.native

      def yAlignment(s: String): Unit = js.native

    }

    @js.native
    class GuideLineLayer(orientation: GuideLineLayer.Orientation) extends Component {
      def scale(s: Scales.Scale): GuideLineLayer = js.native

      def value(x: Double): GuideLineLayer = js.native
    }

    @js.native
    object GuideLineLayer extends js.Object {

      @js.native
      trait Orientation extends js.Object

      val ORIENTATION_VERTICAL: Orientation = js.native
    }

    @js.native
    class Group extends Component {
      def append(p: Plots.Plot[_]): Unit = js.native

      def append(p: Component): Unit = js.native
    }

  }

  @js.native
  object Plots extends js.Object {

    @js.native
    trait PlotEntity[T] extends js.Object {
      val position: Point = js.native
      val datum: T = js.native
    }

    @js.native
    trait Plot[T] extends js.Object {
      def apply(): Line[T] = js.native

      def addDataset(data: Dataset[T]): Plot[T] = js.native

      def datasets: js.Array[Dataset[T]] = js.native

      def datasets(sets: js.Array[Dataset[T]]): Plot[T] = js.native

      def x(f: js.Function1[T, Double], scale: Scales.Scale): Plot[T] = js.native

      def y(f: js.Function1[T, Double], scale: Scales.Scale): Plot[T] = js.native

      def renderTo(s: String): Plot[T] = js.native

      def redraw(): Unit = js.native

      def attr(k: String, v: Int): Plot[T] = js.native

      def attr(k: String, v: String): Plot[T] = js.native

      def attr(k: String, f: js.Function1[T, String]): Plot[T] = js.native

      def attr(k: String, f: js.Function1[T, Double], s: Scales.Scale): Plot[T] = js.native

      def entityNearest(query: Point): PlotEntity[T] = js.native
    }

    @js.native
    class Line[T] extends Plot[T]

    @js.native
    class Area[T] extends Plot[T]

    @js.native
    class Rectangle[T] extends Plot[T]

  }

}