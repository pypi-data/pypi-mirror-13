
class group:
    def __init__(self, name):
        self.members = {}

    def __call__(self, f):
        if f not in self.members.values():
            self.members.update({f.__name__: f})

        def wrapper(*args,**kwargs):
            return f(*args,**kwargs)

        return wrapper

if __name__ == '__main__':
    test_group = group('test')
    test_group2 = group('test2')

    @test_group
    def plus1(a):
        return a+1

    @test_group
    def minus1(a):
        return a-1


    @test_group2
    def multiply(a):
        return a << 1

    print(test_group.members)
    print(test_group2.members)