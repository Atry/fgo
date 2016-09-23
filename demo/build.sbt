import spray.revolver.RevolverPlugin.Revolver


scalaVersion in Global := "2.11.7"
version in Global := "0.1"

lazy val client = (project in file("app/js"))
  .settings(
    libraryDependencies ++= Seq(
      "org.scala-js" %%% "scalajs-dom" % "0.8.2",
      "com.lihaoyi" %%% "upickle" % "0.3.6",
      "com.lihaoyi" %%% "autowire" % "0.2.4",
      "com.lihaoyi" %%% "scalatags" % "0.5.2",
      "com.thoughtworks.binding" %%% "dom" % "9.0.2"
    ),
    jsDependencies ++= Seq(
      "org.webjars" % "d3js" % "3.5.16" / "3.5.16/d3.min.js",
      "org.webjars.bower" % "plottable" % "2.0.0" / "plottable.js" dependsOn "3.5.16/d3.min.js"
    ),
    persistLauncher in Compile := true,
    skip in packageJSDependencies := false,
    addCompilerPlugin("org.scalamacros" % "paradise" % "2.1.0" cross CrossVersion.full)
  )
  .enablePlugins(ScalaJSPlugin, ScalaJSWeb)
  .dependsOn(appJS)


lazy val server = (project in file("app/jvm"))
  .settings(
    Revolver.settings: _*
  )
  .settings(
    scalaJSProjects := Seq(client),
    pipelineStages in Assets := Seq(scalaJSPipeline),
    compile in Compile <<= (compile in Compile) dependsOn scalaJSPipeline,
    WebKeys.packagePrefix in Assets := "public/",
    managedClasspath in Runtime += (packageBin in Assets).value,
    libraryDependencies ++= Seq(
      "io.spray" %% "spray-can" % "1.3.1",
      "io.spray" %% "spray-routing" % "1.3.1",
      "com.typesafe.akka" %% "akka-actor" % "2.3.2",
      "org.webjars" % "bootstrap" % "3.2.0",
      "org.webjars.bower" % "plottable" % "2.0.0",
      "com.lihaoyi" %% "scalatags" % "0.5.2",
      "com.lihaoyi" %%% "upickle" % "0.3.6",
      "com.lihaoyi" %%% "autowire" % "0.2.4",
      "com.vmunier" %% "scalajs-scripts" % "1.0.0"
    ) //    compile in Compile <<= (compile in Compile) dependsOn scalaJSPipeline
  )
  .enablePlugins(SbtWeb, SbtTwirl)
  .dependsOn(appJVM)


lazy val app = (crossProject.crossType(CrossType.Pure) in file("app/shared"))
  .jsConfigure(_ enablePlugins ScalaJSWeb)


lazy val appJS = app.js
lazy val appJVM = app.jvm

onLoad in Global := (Command.process("project server", _: State)) compose (onLoad in Global).value