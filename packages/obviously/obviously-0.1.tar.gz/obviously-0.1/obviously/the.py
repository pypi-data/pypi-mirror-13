from collections import namedtuple


class ObviousFailure(Exception): pass


class _the(object):

    def __init__(self):
        self.__wrappers = set()

    def __call__(self, target):
        new_wrapper = WrapsObject(target)
        self.__wrappers.add(new_wrapper)
        return new_wrapper

    def clear(self):
        self.__wrappers = set()

    def verify(self):
        for wrapper in self.__wrappers:
            if not wrapper.meets_requirements:
                raise ObviousFailure(
                    wrapper,
                )


class WrapsObject(object):

    def __repr__(self):
        return u"<WrapsObject: {}>".format(self.__target)

    def __init__(self, target):
        self.__target = target
        self.__accesses = []
        self.__requirements = []

    def should_receive(self, method_name):
        self.__requirements.append(ListensForMethod(self, method_name))
        return self

    def given_arguments(self, *args, **kwargs):
        self.__requirements[-1].expected_argumets = ListensForMethod.ExpectedArguments(args, kwargs)
        return self

    def and_return(self, return_value):
        self.__requirements[-1].return_value = return_value
        return self

    def __getattr__(self, key):
        self.__accesss.append(key)
        return getattr(self.__target)


class ListensForMethod(object):

    ExpectedArguments = namedtuple("ExpectedArguments", ["args", "kwargs"])

    class NoReturnValue(object): pass

    def __init__(self, watcher, method_name):
        self.__watcher = watcher
        self.__method_name = method_name
        self.expected_arguments = None
        self.return_value = ListensForMethod.NoReturnValue


