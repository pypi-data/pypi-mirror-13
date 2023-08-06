from .timeit import timeit
from .group import group
from .coroutine import coroutine
from .synchronized import synchronized

# Decorators are simply callables that return a replacement,
# optionally the same function, a wrapper, or something completely different.
#
# As such, you could create a conditional decorator:
#
# class conditional_decorator(object):
#     def __init__(self, dec, condition):
#         self.decorator = dec
#         self.condition = condition
#
#     def __call__(self, func):
#         if not self.condition:
#             # Return the function unchanged, not decorated.
#             return func
#         return self.decorator(func)
# Now you can use it like this:
#
# @conditional_decorator(timeit, doing_performance_analysis)
# def foo():
#     time.sleep(2)
#