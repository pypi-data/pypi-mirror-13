import sys
import time

import tornado.web
import tornado.ioloop

from tprofile import ProfileMeta

def condition(self):
    if self.get_argument("profile", None) == "2":
        return True
    return False

ProfileMeta.set_condition(condition)

class BaseHandler(tornado.web.RequestHandler):
    """this is base class of all handlers"""
    __metaclass__ = ProfileMeta

    def prepare(self):
        self.write("this is prepare.\n")

class MainHandler(BaseHandler):
    def block(self, n):
        time.sleep(n)

    def get(self):
        self.block(1)
        self.write("this is get.\n")
        self.block(0.8)
        self._write_buffer.append("end.\n")

app = tornado.web.Application([
            (r"/test/profile", MainHandler),
        ])

def main():
    port = 9876
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()

