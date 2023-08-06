import six
import yaml

from yaml.representer import Representer, SafeRepresenter

try:
    import simplejson as json

except ImportError:
    import json


def stitch(obj):
    if isinstance(obj, (list, tuple)):
        return Strands([stitch(item) for item in obj])

    if isinstance(obj, dict):
        return Threads(obj)

    return obj


def unstitch(obj):
    if isinstance(obj, dict):
        return dict((k, unstitch(v)) for k, v in six.iteritems(obj))

    if isinstance(obj, (list, tuple)):
        return type(obj)(unstitch(v) for v in obj)

    return obj


class Strands(list):

    def __init__(self, *args):
        list.__init__(self, *args)

    def __call__(self, strand):
        return self[strand]


class Threads(dict):

    def __init__(self, *args, **kwargs):
        if isinstance(args, dict):
            stitch(args)

        for thread, value in six.iteritems(kwargs):
            kwargs[thread] = stitch(value)

        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

    def __call__(self, thread, *args):

        if args:
            self.__dict__[thread] = stitch(*args)

        return self.__dict__[thread]

    def _thread(thread, value):
        self.__dict__[thread] = value
        return self.__dict__[thread]

    @staticmethod
    def json_load(fp, **kwargs):
        return stitch(json.load(fp, **kwargs))

    @staticmethod
    def json_loads(data, **kwargs):
        return stitch(json.loads(data, **kwargs))

    def json_dump(self, fp, **kwargs):
        return json.dump(self, fp, **kwargs)

    def json_dumps(self, **kwargs):
        return json.dumps(self, **kwargs)

    @staticmethod
    def yaml_load(fp, **kwargs):
        return stitch(yaml.load(fp, **kwargs))

    @staticmethod
    def yaml_load_all(fp, **kwargs):
        return stitch(yaml.load_all(fp, **kwargs))

    @staticmethod
    def yaml_safe_load(fp):
        return Threads.yaml_load(stream, yaml.SafeLoader)

    @staticmethod
    def yaml_safe_load_all(fp):
        return Threads.yaml_load_all(stream, yaml.SafeLoader)

    def yaml_dump(self, **kwargs):
        kwargs.setdefault('indent', 4)
        kwargs.setdefault('default_flow_style', False)

        return yaml.dump(self, **kwargs)

    def yamp_safe_dump(self, **kwargs):
        kwargs.setdefault('indent', 4)
        kwargs.setdefault('default_flow_style', False)

        return yaml.safe_dump(self, **kwargs)

    @staticmethod
    def dict_load(self, data):
        return stitch(data)

    def dict_dump(self):
        return unstitch(self)


def from_yaml(loader, node):
    data = Threads()
    yield data

    value = loader.construct_mapping(node)
    data.update(value)


def to_yaml(dumper, data):
    return dumper.represent_mapping(six.u('!threads.Threads'), data)


def to_yaml_safe(dumper, data):
    return dumper.represent_dict(data)


yaml.add_constructor(six.u('!threads'), from_yaml)
yaml.add_constructor(six.u('!threads.Threads'), from_yaml)

Representer.add_representer(Threads, to_yaml)
Representer.add_multi_representer(Threads, to_yaml)

SafeRepresenter.add_representer(Threads, to_yaml_safe)
SafeRepresenter.add_multi_representer(Threads, to_yaml_safe)

items = Threads(a=0, b=1, c=[0, 2], d=Threads(x=0, y=1, z=2))
print items.yaml_dump()