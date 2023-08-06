from re      import compile
from inspect import getargspec

class TypeArgsError(TypeError):
    pass

class has(object):
    '''
    Specify that an argument has an attribute, rather than that it is of a type.
    '''
    def __init__(self, attribute):
        self.attribute = attribute

    def __repr__(self):
        return 'has({})'.format(self.attribute)

class re(object):
    '''
    Specify that an argument satisifies a regular expression, rather than that
    it is of a type.
    '''
    def __init__(self, pattern):
        self.pattern  = pattern
        self.compiled = compile(pattern)

    def __repr__(self):
        return 're({})'.format(pattern)

def typeargs(*types):
    def match(arg, type_):
        '''
        Helper for deciding if an argument passed to the function meets the
        expectations of the signature in typeargs.
        '''
        if isinstance(type_, type):
            return isinstance(arg, type_)
        elif isinstance(type_, has):
            try:
                return hasattr(arg, type_.attribute)
            except:
                return False
        elif isinstance(type_, re):
            try:
                return type_.compiled.match(arg).group(0) == arg
            except:
                return False
        return arg == type_

    def actualDecorator(function):
        from functools import wraps

        typeForName = zip(function.__code__.co_varnames, types)
        @wraps(function)
        def wrapper(*args, **kwargs):
            for arg in args:
                for argName, type_ in typeForName:
                    if argName not in kwargs and match(arg, type_):
                        kwargs[argName] = arg
                        break
                else:
                    raise TypeArgsError('{} takes the arguments {}. Could not '
                                        'place {}. Had already assigned {}.'
                                        .format(function.func_name, typeForName,
                                                repr(arg), kwargs))
            unmatchedPairs = []
            defaults = getargspec(function).defaults
            if defaults:
                for arg, type_ in typeForName[:-len(defaults)]:
                    if arg not in kwargs:
                        unmatchedPairs.append((arg, type_))
            if unmatchedPairs:
                raise TypeArgsError('{} has the following arguments which have '
                                    'no defaults and nothing passed in for '
                                    'them {}. Had already assigned {}.'
                                    .format(function.func_name, unmatchedPairs,
                                            kwargs))
            return function(**kwargs)
        return wrapper
    return actualDecorator