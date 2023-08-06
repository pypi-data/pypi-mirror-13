# encoding: utf-8

from inspect import isclass
from functools import partial

from .router import Router

if __debug__:
	import warnings
	from collections import deque


log = __import__('logging').getLogger(__name__)


class RouteDispatch(object):
	def __call__(self, context, obj, path):
		if __debug__:
			if not isinstance(path, deque):
				warnings.warn(
						"Your code uses auto-casting of paths to a deque; "
						"this will explode gloriously if run in a production environment.",
						RuntimeWarning, stacklevel=1
					)
				
				if isinstance(path, str):
					path = deque(path.split('/')[1 if not path or path.startswith('/') else 0:])
				else:
					path = deque(path)
			
			log.debug("Preparing route dispatch.", extra=dict(
					dispatcher = repr(self),
					context = repr(context),
					obj = repr(obj),
					path = list(path)
				))
		
		router = Router.from_object(obj)
		processed, target, kwargs = router.route(path)
		
		if isclass(obj):
			obj = obj() if context is None else obj(context)
			yield None, obj, False  # Let everyone know we instantiated something.
			target = partial(target, obj, **kwargs)
		else:
			target = partial(target, **kwargs)
		
		yield processed, target, True
