from jnius import autoclass

Stack = autoclass('java.util.Stack')
stack = Stack()
stack.push('Hello')
stack.push('World')

print(stack.pop()) # --> 'world'
print(stack.pop()) # --> 'hello'
