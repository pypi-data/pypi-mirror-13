# encoding: utf-8

import warnings
import pytest

from collections import deque
from web.dispatch.route.dispatch import RouteDispatch

from sample import Root


@pytest.fixture
def dispatch():
	return RouteDispatch()



def test_instantiated():
	class InstantiatedRoot(object):
		def hello(self, name):
			return "Hello " + name
		hello.__route__ = "/hello/{name}"
	
	root = InstantiatedRoot()
	result = list(RouteDispatch()(None, root, deque(['hello', 'world'])))
	assert len(result) == 1
	assert result[0][0] == ('hello', 'world')
	assert result[0][1]() == "Hello world"
	assert result[0][2] is True


if __debug__:
	class TestFallbackBehaviour(object):
		def test_string_value(self, dispatch):
			with warnings.catch_warnings(record=True) as w:
				warnings.simplefilter("always")
				
				result = list(dispatch(None, Root, '/user'))
				
				assert len(w) == 1
				assert issubclass(w[-1].category, RuntimeWarning)
				assert 'production' in str(w[-1].message)
				
				assert len(result) == 2
		
		def test_list_value(self, dispatch):
			with warnings.catch_warnings(record=True) as w:
				warnings.simplefilter("always")
				
				result = list(dispatch(None, Root, ['user', 'GothAlice']))
				
				assert len(w) == 1
				assert issubclass(w[-1].category, RuntimeWarning)
				assert 'production' in str(w[-1].message)
				
				assert len(result) == 2


class TestDispatchSample(object):
	def test_single_static(self, dispatch):
		result = list(dispatch(None, Root, deque(['user'])))
		
		assert len(result) == 2
		assert result[0][0] is None
		assert isinstance(result[0][1], Root)
		assert result[0][2] is False
		
		assert result[1][0] == ('user', )
		assert result[1][1]() == "I'm all people."
		assert result[1][2] == True
	
	def test_dynamic_username(self, dispatch):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice'])))
		
		assert len(result) == 2
		assert result[0][0] is None
		assert isinstance(result[0][1], Root)
		assert result[0][2] is False
		
		assert result[1][0] == ('user', 'GothAlice')
		assert result[1][1]() == "Hi, I'm GothAlice"
		assert result[1][2] == True
	
	def test_dynamic_username_action(self, dispatch):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice', 'action'])))
		
		assert len(result) == 2
		assert result[0][0] is None
		assert isinstance(result[0][1], Root)
		assert result[0][2] is False
		
		assert result[1][0] == ('user', 'GothAlice', 'action')
		assert result[1][1]() == "I'm also GothAlice"
		assert result[1][2] == True


class TestDispatchFailures(object):
	def test_static_failure(self, dispatch):
		with pytest.raises(LookupError):
			print(list(dispatch(None, Root, deque(['die']))))
	
	def test_dynamic_failure(self, dispatch):
		with pytest.raises(LookupError):
			print(list(dispatch(None, Root, deque(['user', '27']))))
