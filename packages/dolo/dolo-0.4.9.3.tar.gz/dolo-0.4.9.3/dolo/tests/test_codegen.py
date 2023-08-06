s = """
def fun(x,y,n=i):
    s = "{} {} {}".format(x,y,n=i)
    return s
"""


def test_direct():
    from dolo.compiler.codegen import to_source
    import ast

    expr = ast.parse(s)

    print(ast.dump(expr))

    res = to_source(expr)
    print(res)

test_direct()
