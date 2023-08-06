# !/usr/bin/env python3.4
# encoding: utf-8

"""Some random package."""


def fibonacci_recursive(n, fibo_seq=[0, 1]):
    """(recursive) Returns the sum of the first n Fibonacci numbers."""
    if len(fibo_seq) == n:
        print(sum(fibo_seq))
        return(sum(fibo_seq))
        # return(fibo_seq)
    fn = fibo_seq[-1] + fibo_seq[-2]
    fibo_seq.append(fn)
    return(fibonacci_recursive(n, fibo_seq))


def inf_gen(x):
    """
    Infinite generator, starting with given value x.

    Usage:
    y = inf_gen(5)
        for x in y:
            print(x)
    """
    add = 1
    while True:
        yield x + add
        add = add * 2


def own_xrange(start, stop, step):
    """Return iterator range."""
    current = start - step
    while current < stop:
        yield current + step
        current += step
