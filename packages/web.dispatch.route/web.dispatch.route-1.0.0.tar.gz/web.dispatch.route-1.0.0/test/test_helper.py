# encoding: utf-8

from web.dispatch.route.helper import route
from web.dispatch.route.router import Router


def test_helper_free_root_route():
	class HelperFree(object):
		def root(self):
			return "I'm the baby!"
		
		root.__route__ = "/"
	
	router = Router.from_object(HelperFree)
	
	assert len(router.routes) == 1
	assert None in router.routes
	assert router.routes[None] == HelperFree.root
	assert router.routes[None](HelperFree()) == "I'm the baby!"


def test_helper_immediate_bind():
	class HelperBound(object):
		__router__ = Router()
		
		@route('/', __router__)
		def root(self):
			return "I'm the baby!"
	
	router = HelperBound.__router__
	
	assert len(router.routes) == 1
	assert None in router.routes
	assert router.routes[None](HelperBound()) == "I'm the baby!"
