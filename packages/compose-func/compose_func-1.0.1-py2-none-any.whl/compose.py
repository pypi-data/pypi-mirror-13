from functools import reduce

def compose(*fs):
    """
    Create a function composition.

    :type *fs: ``iterable`` of 1-argument ``callable``s
    :param *fs: Iterable of 1-argument functions to compose, functions will be
        applied from last to first, in other words ``compose(f, g)(x) ==
        f(g(x))``.
    :return: I{callable} taking 1 argument.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), fs, lambda x: x)
