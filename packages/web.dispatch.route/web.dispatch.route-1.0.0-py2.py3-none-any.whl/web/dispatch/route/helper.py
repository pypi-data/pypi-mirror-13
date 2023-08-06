# encoding: utf-8

COUNT = 0

def route(route, router=None):
	def inner(func):
		global COUNT
		
		if router:
			# Immediate routing declaration; mostly for testing.
			router.register(route, func)
		else:
			# Deferred routing declaration.
			func.__route__ = route
		func.__index__ = COUNT
		
		COUNT += 1
		
		return func
	
	return inner
