from tornado.web import RequestHandler
from hybrid.util import imports
from hybrid.metaclass import CatchExceptionMeta

class BaseHandler(RequestHandler):
    __metaclass__ = CatchExceptionMeta
    def getviewfunc(self, view, module):
        if not view and not module:
            from ..views import json_view
            return json_view
        elif not view:
            raise RuntimeError("missing view function name")

        if not module:
            from .. import views
            m = views
        else:
            m = imports(module)
        if not m or not hasattr(m, view):
            self.send_error(500, 'can\'t find %s:%s'%(module,view))
            return 
        return getattr(m, view)

    def render_func(self, data, view=None, module=None, *a, **kw):
        self.write(self.getviewfunc(view, module)(data, *a, **kw))
        self.finish()

