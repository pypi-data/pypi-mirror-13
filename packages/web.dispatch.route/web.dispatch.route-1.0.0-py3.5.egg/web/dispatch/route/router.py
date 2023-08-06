# encoding: utf-8

import re

from collections import OrderedDict as odict

re_type = type(re.compile(""))


class DynamicElement(object):
	def __repr__(self):
		return "<dynamic element>"

__DYNAMIC__ = DynamicElement()


def route_iterator(obj):
	ordered = []
	
	for name in dir(obj):
		if name.startswith('_'): continue
		
		value = getattr(obj, name)
		if not hasattr(value, '__route__'): continue
		
		if hasattr(value, '__index__'):
			ordered.append((value.__index__, name, value))
		else:
			yield name, value
	
	for item in sorted(ordered):
		yield item[1:]


class Router(object):
	def __init__(self):
		self.routes = odict()
	
	@classmethod
	def from_object(cls, obj, cache=True):
		if cache and hasattr(obj, '__router__'):
			return obj.__router__
		
		self = cls()
		
		for name, value in route_iterator(obj):
			self.register(value.__route__, value)
		
		if cache:
			obj.__router__ = self
		
		return self
	
	def register(self, route, obj):
		parsed = self.parse(route)
		routes = self.routes
		
		for element in parsed:
			if isinstance(element, re_type):
				routes.setdefault(__DYNAMIC__, odict())
				routes[__DYNAMIC__].setdefault(element, odict())
				routes = routes[__DYNAMIC__][element]
				continue
			
			routes.setdefault(element, odict())
			routes = routes[element]
		
		routes[None] = obj
	
	def parse(self, route):
		parts = route.lstrip('/')
		
		if not parts:
			return []
		
		parts = parts.split('/')
		
		for i, part in enumerate(parts):
			if '{' not in part:
				continue
			
			elif '}' not in part:
				raise ValueError("Route match must not contain forward slashes.")
			
			sub = list()
			
			while part:
				prefix, _, match = part.partition('{')
				name, _, part = match.partition('}')
				sub.append(prefix)
				
				name, _, regex = name.partition(':')
				sub.append('(?P<%s>%s)' % (name, regex or r'[^/]+'))
			
			parts[i] = re.compile(''.join(sub))
		
		return parts
	
	def route(self, path):
		processed = list()
		routes = self.routes
		arguments = dict()
		
		for i, part in enumerate(path):
			processed.append(part)
			
			if part in routes:  # Exact match, convienent!
				routes = routes[part]
				continue
			
			if __DYNAMIC__ not in routes:
				raise LookupError("No static route element capable of handling: " + part)
			
			for route in routes[__DYNAMIC__]:
				matched = route.match(part)
				if not matched: continue
				arguments.update(matched.groupdict())
				routes = routes[__DYNAMIC__][route]
				break
			else:
				raise LookupError("No dynamic route element capable of handling: " + part)
		
		return tuple(processed), routes[None], arguments
