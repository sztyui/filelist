def lower_it(func):
	def func_wrapper(*args, **kwargs):
		if 'system' in kwargs:
			kwargs['system'] = kwargs['system'].lower()
		return func(*args, **kwargs)
	func_wrapper.__name__ = func.__name__
	return func_wrapper