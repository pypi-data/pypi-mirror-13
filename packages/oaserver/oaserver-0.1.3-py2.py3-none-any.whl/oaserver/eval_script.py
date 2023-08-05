"""
Evaluate a main function provided in a text file
return the result of the function
"""


def eval_script(pycode, args=None):
    """ Evaluate pycode, run expected function main in it.

    Args:
        - pycode(str): python script as txt
        - args(tuple of any): arguments to pass to main

    Return:
        the result of 'main' function inside pycode

    Raise:
        KeyError if no object called 'main'
        is found in the code.
    """
    if args is None:
        args = {}

    ast = compile(pycode, "<rem str>", 'exec')
    loc = {}
    eval(ast, loc)

    try:
        main = loc['main']
    except KeyError:
        raise UserWarning("no 'main' function defined in script")

    try:
        return main(**args)
    except TypeError:
        raise UserWarning("'main' object is not callable or args do not match")
