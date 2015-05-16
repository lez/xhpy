import sys
from .parser import parse
from importlib.machinery import SourceFileLoader, PathFinder

class XHPyLoader(SourceFileLoader):
  def __init__(self, path):
    self.path = path

  def get_filename(self, name):
    return self.path

  def get_data(self, path):
    if path.endswith('.py'):
      return parse(super().get_data(path).decode()).encode()
    return super().get_data(path)

  def path_stats(self, path):
    """not returning size, because the loader would identify the cache as stale"""
    stats = super().path_stats(path)
    return {'mtime': stats['mtime']}

class XHPyFinder(PathFinder):
  __xhpy_module_map = {}
  __xhpy_leaf = '__leaf'

  @classmethod
  def register_xhpy_module(cls, name):
    """
    Registers the given module and all its submodules as containing XHPy,
    so that they are passed through the XHPy preprocessor when imported.
    """
    cur = cls.__xhpy_module_map
    for t in name.split('.'):
      cur = cur.setdefault(t, {})
    cur[cls.__xhpy_leaf] = True

  @classmethod
  def is_xhpy_module(cls, name):
    cur = cls.__xhpy_module_map
    for t in name.split('.'):
      if t not in cur:
        return cls.__xhpy_leaf in cur
      cur = cur[t]
    return cls.__xhpy_leaf in cur

  def find_spec(self, name, path, target=None):
    ms = PathFinder.find_spec(name, path, target)
    if self.is_xhpy_module(name):
      ms.loader = XHPyLoader(ms.origin)
    return ms

def register_xhpy_module(name):
  XHPyFinder.register_xhpy_module(name)

sys.meta_path.insert(0, XHPyFinder())
register_xhpy_module('xhpy')
