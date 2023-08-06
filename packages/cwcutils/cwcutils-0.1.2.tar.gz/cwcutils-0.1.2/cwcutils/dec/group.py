from collections import Iterable

class group:
    def __init__(self, name):
        self.name = name
        self.members = set()

    def __call__(self, f):
        if f not in self.members:
            self.members.add(f)

        def new_f(*args,**kwargs):
            g = f(*args,**kwargs)
            # g.__name__ = f.__name__
            # g.__doc__ = f.__doc__
            # g.__dict__.update(f.__dict__)
            return g

        new_f.__name__ = f.__name__
        new_f.__doc__ = f.__doc__
        new_f.__dict__.update(f.__dict__)
        return new_f

    def name_of_members(self):
        return [f.__name__ for f in self.members]

    def remove(self, members):
        if not isinstance(members,Iterable):
            members = [members]

        member_to_remove_names = [f.__name__ for f in members]
        new_members = set(f for f in self.members if f.__name__ not in member_to_remove_names)
        self.members = new_members


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
    def multiply2(a):
        return a << 1

    print(test_group.members)
    print(test_group2.members)

    # assert multiply2 in test_group2.members # this does not work, because there will be 2 instances of multiply2
    # alternatively, assert their existence using their names

    assert multiply2.__name__ in test_group2.name_of_members()
    assert plus1.__name__ in test_group.name_of_members()
    assert minus1.__name__ in test_group.name_of_members()

    test_group.remove(plus1) # arg is not iterable
    assert plus1.__name__ not in test_group.members

    test_group.__call__(plus1)
    test_group.remove({plus1,minus1}) # arg is iterable
    assert plus1.__name__ not in test_group.members
    assert minus1.__name__ not in test_group.members


    test_group.__call__(plus1)
    f = test_group.members.pop()
    print(f(1))

