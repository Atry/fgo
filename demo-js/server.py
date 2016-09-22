import os.path

import tornado.ioloop
import tornado.web


static_path = os.path.join(os.path.dirname(__file__), "static")


def make_app():
    return tornado.web.Application([
        (r"/(.*)", tornado.web.StaticFileHandler, dict(path=static_path, default_filename="index.html"))
    ],
    static_path=static_path,
    static_handler_args=dict(default_filename="index.html"))

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
