import string
import types
import cProfile
import pstats
import tempfile
import json
import inspect

import tornado.web

class ProfileMeta(type):
    def __new__(mcs, cls_name, bases, attrs):
        supported_methods = map(string.lower, 
            tornado.web.RequestHandler.SUPPORTED_METHODS)
        for attr in attrs:
            if attr in supported_methods and \
                isinstance(attrs[attr], types.FunctionType):
                attrs[attr] = ProfileMeta.profile(attrs[attr])
        return super(ProfileMeta, mcs).__new__(mcs, cls_name, bases, attrs)

    @staticmethod
    def condition(requesthandler):
        return True if requesthandler.get_argument("profile", None) else False

    @classmethod
    def set_condition(cls, f):
        assert callable(f) and len(inspect.getargspec(f).args) == 1, \
                'f must be a callable object and takes one postion argument'
        cls.condition = staticmethod(f)

    @staticmethod
    def profile(f):
        def _inner(self, *args, **kwargs):
            if not ProfileMeta.condition(self):
                return f(self, *args, **kwargs)

            sortby = self.get_argument('sortby', None)
            if (not sortby) or (sortby not in pstats.Stats.sort_arg_dict_default):
                sortby = 'cumulative'

            try:
                amount_number = (int(self.get_argument("amount_number")), )
            except (tornado.web.MissingArgumentError, ValueError, TypeError):
                amount_number = tuple()
            amount = amount_number + tuple(self.get_arguments("amount", []))

            temp = tempfile.NamedTemporaryFile()
            temp_stats = tempfile.NamedTemporaryFile()
            try:
                cProfile.runctx("f(self, *args, **kwargs)", globals(), locals(), temp.name)
                self._write_buffer = []

                so = pstats.Stats(temp.name, stream=temp_stats).sort_stats(sortby).print_stats(*amount)
                temp_stats.seek(0)
                self.write(ProfileMeta.to_json(temp_stats.read(), so, amount))
            finally:
                temp.close()
                temp_stats.close()
        return _inner

    @staticmethod
    def to_json(content, so, amount):
        d = {}
        d['origin'] = content
        d['detail'] = []

        _, func_list = so.get_print_list(amount)
        if func_list:
            for func in func_list:
                cc, nc, tottime, cumtime, callers = so.stats[func]
                d['detail'].append({"filename:lineno(function)": pstats.func_std_string(func),
                    "ncalls": str(nc) if cc == nc else "%s/%s" % (nc, cc),
                    "tottime": tottime, "cumtime": cumtime,
                    "callers": map(pstats.func_std_string, callers.keys())
                })

        return json.dumps(d)

