"""
Extension stuff
"""
from memoizer import memoize
from pkg_resources import iter_entry_points

class ResourceNotFound(RuntimeError):
    """
    Resource was not found
    """

class ResourceNotUnique(RuntimeError):
    """
    More than one resource found for condition
    """

@memoize
def Load(namespace, resource):
    try:
        return next(iter_entry_points(namespace, resource)).load()
    except StopIteration:
        raise ResourceNotFound('Resource "%s" not found in namespace "%s"' % (namespace, resource))

def LoadClasses(namespace, condition):
    try:
        return [c for c in [ep.load() for ep in iter_entry_points(namespace)] if c.check(condition)]
    except StopIteration:
        raise ResourceNotFound('No class matching condition found in namespace "%s"' % namespace)

def LoadClass(namespace, condition):
    try:
        result = [c for c in [ep.load() for ep in iter_entry_points(namespace)] if c.check(condition)]
        if len(result) > 1:
            raise ResourceNotUnique('More than one class matches in namespace "%s"' % namespace)
    except StopIteration:
        raise ResourceNotFound('No class matching condition found in namespace "%s"' % namespace)
