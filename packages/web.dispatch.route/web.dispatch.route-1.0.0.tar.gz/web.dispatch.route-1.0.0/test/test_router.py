# encoding: utf-8

import pytest

from web.dispatch.route.router import __DYNAMIC__, Router

from sample import Root


@pytest.fixture
def router():
	return Router.from_object(Root)


def test_dynamic_repr():
	assert repr(__DYNAMIC__) == '<dynamic element>'


def test_router_singleton():
	assert Router.from_object(Root) is Router.from_object(Root)


def test_invalid_route():
	router = Router()
	
	with pytest.raises(ValueError):
		router.parse("{bad:/}")


class TestRouterSample(object):
	def test_single_static(self, router):
		assert len(router.routes) == 1  # There's only a single top-level element.
		assert 'user' in router.routes  # It's "user".
		assert len(router.routes['user']) == 2  # Which has a terminus and dynamic continuation.
		assert router.routes['user'][None] == Root.root  # The terminus is the "root" method.
		assert router.routes['user'][None](Root()) == "I'm all people."  # It really is.
	
	def test_dynamic_username(self, router):
		assert __DYNAMIC__ in router.routes['user']
		
		dynamic = router.routes['user'][__DYNAMIC__]
		assert len(dynamic) == 1
		
		assert list(dynamic.keys())[0].match("GothAlice")  # The regular expression matches.
		
		assert len(list(dynamic.values())[0]) == 2
		
		assert list(dynamic.values())[0][None] == Root.user
		assert list(dynamic.values())[0][None](Root(), "GothAlice") == "Hi, I'm GothAlice"
	
	def test_dynamic_username_action(self, router):
		assert __DYNAMIC__ in router.routes['user']
		
		dynamic = router.routes['user'][__DYNAMIC__]
		assert len(dynamic) == 1
		
		assert list(dynamic.keys())[0].match("GothAlice")  # The regular expression matches.
		
		assert len(list(dynamic.values())[0]) == 2
		
		assert list(dynamic.values())[0][None] == Root.user
		assert list(dynamic.values())[0][None](Root(), "GothAlice") == "Hi, I'm GothAlice"
