# from dopus.core import ToolRunner, tool, Convo
# from dopus.util import suppress_output, log
# import inspect
# import json
# import argparse

# test_registry = {}

# @tool(
#     description="tell the user if the assertion about the given data is true or false",
#     parameters={
#         "result": {
#             "type": "boolean",
#             "description": "true if the assertion is true or false"
#         },
#         "message": {
#             "type": "string",
#             "description": "message explaining the result"
#         }
#     },
#     required=["result", "message"],
#     registry=test_registry
# )
# def SmartAssert(self, result, message):
#     return {
#         'assert': result,
#         'message': message
#     }

# class DopusTest:

#     def __init__(self):
#         parser = argparse.ArgumentParser(description='Run DopusTest')
#         parser.add_argument('--test', type=str, help='Specific test to run')
#         args = parser.parse_args()

#         self.test_cases = []
#         self.tests = []
#         self.passed_tests = 0
#         self.total_tests = 0
#         self.runner = ToolRunner(registry=test_registry)
#         self.runner.add_tool(SmartAssert)
#         self.suppress_output = False
#         self.test = args.test
#         self.setUp()
#         self._add_tests_in_class()
#         self.run()
#         self.run_multi()
#         self.tearDown()

#     def _add_tests_in_class(self):
#             for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
#                 if hasattr(method, "is_test"):
#                     if hasattr(method, "path"):
#                         self.load(getattr(method, "path"), method)
#                     else:
#                         self.tests.append(method)

#     def setUp(self):
#         pass

#     def tearDown(self):
#         pass

#     def on(self, test_case):
#         pass

#     def load(self, path, func):
#         with open(path, 'r') as file:
#             self.test_cases.append({'function': func, 'data': json.load(file)})

#     def run_test(self, test_func, test_name):
#         self.total_tests += 1
#         try:
#             if self.suppress_output:
#                 with suppress_output():
#                     test_func()
#             else:
#                 test_func()
#             log(f"✅ Test Passed - {test_name}")
#             self.passed_tests += 1
#         except AssertionError as e:
#             log(f"❌ Test Failed - {test_name}: {e}", color="red")

#     def run(self):
#         for test in self.tests:
#             if self.test and test.__name__ != self.test:
#                 continue
#             self.run_test(test, test.__name__)

#     def run_multi_test(self, name, test, func):
#         self.total_tests += 1
#         try:
#             if self.suppress_output:
#                 with suppress_output():
#                     func(name, test)
#             else:
#                 func(name, test)
#             log(f"✅ Test Passed - {name}")
#             self.passed_tests += 1
#         except AssertionError as e:
#             log(f"❌ Test Failed - {name}: {e}", color="red")

#     def run_multi(self):
#         for tests in self.test_cases:
#             for test_name, test_data in tests['data'].items():
#                 if self.test and test_name != self.test:
#                     continue
#                 self.run_multi_test(test_name, test_data, tests['function'])

#     def tearDown(self):
#         if self.total_tests > 0:
#             success_rate = (self.passed_tests / self.total_tests) * 100
#             log(f"Passed {success_rate:.2f}% tests [{self.passed_tests}/{self.total_tests}]", color="blue")
#         else:
#             log("No tests were run.")

#     def extract_tool_calls(self, actions):
#         tool_calls = []
#         for action in actions:
#             if 'tool_called' in action:
#                 tool_calls.append(action['tool_called'])
#         return tool_calls

#     def IsEqual(self, first, second):
#         if isinstance(first, list) and isinstance(second, list):
#             return len(first) == len(second) and all(f == s for f, s in zip(first, second))
#         elif isinstance(first, dict) and isinstance(second, dict):
#             return first == second
#         else:
#             return first == second

#     def AssertEqual(self, first, second):
#         if isinstance(first, list) and isinstance(second, list):
#             if len(first) != len(second) or any(f != s for f, s in zip(first, second)):
#                 raise AssertionError(f"Lists differ: {first} != {second}")
#         elif isinstance(first, dict) and isinstance(second, dict):
#             if first != second:
#                 raise AssertionError(f"Dictionaries differ: {first} != {second}")
#         else:
#             if first != second:
#                 raise AssertionError(f"{first} does not equal {second}")

#     def AssertTrue(self, expr, msg=None):
#         if not expr:
#             raise AssertionError(msg or f"{expr} is not True")

#     def AssertFalse(self, expr, msg=None):
#         if expr:
#             raise AssertionError(msg or f"{expr} is not False")

#     def AssertIn(self, member, container, msg=None):
#         if member not in container:
#             raise AssertionError(msg or f"{member} not found in {container}")

#     def AssertNotIn(self, member, container, msg=None):
#         if member in container:
#             raise AssertionError(msg or f"{member} unexpectedly found in {container}")

#     def _LLMAssert(self, assertion, data):
#         convo = Convo()
#         convo.append('user', f"Determine if this assertion about the data is true or false: {assertion}\nDATA: {data}")
#         res, actions = self.runner.execute(convo, default_inference_provider)
#         return res

#     def LLMAssertTrue(self, assertion, data):
#         res = self._LLMAssert(assertion, data)
#         if res['assert'] is False:
#             raise AssertionError(res["message"])
    
#     def LLMAssertFalse(self, assertion, data):
#         res = self._LLMAssert(assertion, data)
#         if res['assert'] is True:
#             raise AssertionError(res["message"])

# def test_multi(path):
#     def decorator(func):
#         func.is_test = True
#         func.path = path
#         return func
#     return decorator

# def test(func):
#     func.is_test = True
#     return func