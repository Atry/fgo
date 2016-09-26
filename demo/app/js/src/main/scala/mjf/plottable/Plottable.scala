package mjf.plottable

import scala.scalajs.js
import scala.scalajs.js.annotation.JSName


@js.native
object Plottable extends js.Object {

  @js.native
  trait Point extends js.Object {
    val x: Double
    val y: Double
  }

  @js.native
  class Dataset[T](data: js.Array[T]) extends js.Object {
    def onUpdate(): Unit = js.native
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
      def domain(a: js.Array[String]): Scale = js.native
    }

    @js.native
    class Category() extends Scale

    @js.native
    class Linear() extends Scale

    @js.native
    class Color() extends Scale {
      def scale(s: String): String = js.native
    }

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
    class Group[T] extends Component {
      def append(p: Plots.Plot[T]): Unit = js.native

      def append(p: Component): Unit = js.native
    }

  }

  @js.native
  object Plots extends js.Object {

    @js.native
    trait PlotEntity extends js.Object {
      val position: Point = js.native
      val datum: (Double, Double) = js.native
    }

    @js.native
    trait Plot[T] extends js.Object {
      def apply(): Line[T] = js.native

      def addDataset(data: Dataset[T]): Plot[T] = js.native

      def datasets(sets: js.Array[Dataset[T]]): Plot[T] = js.native

      def x(f: js.Function1[T, Double], scale: Scales.Scale): Plot[T] = js.native

      def y(f: js.Function1[T, Double], scale: Scales.Scale): Plot[T] = js.native

      def renderTo(s: String): Plot[T] = js.native

      def redraw(): Unit = js.native

      def attr(k: String, v: Int): Plot[T] = js.native

      def attr(k: String, v: String): Plot[T] = js.native

      def attr(k: String, f: js.Function1[T, String]): Plot[T] = js.native

      def entityNearest(query: Point): PlotEntity = js.native
    }

    @js.native
    class Line[T] extends Plot[T]

    @js.native
    class Area[T] extends Plot[T]

  }

}