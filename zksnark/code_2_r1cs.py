import ast

def parse(code):
    return ast.parse(code).body

def extract_inputs_and_body(code):
    if len(code) != 1 or not isinstance(code[0], ast.FunctionDef):
        raise Exception("Expection ast body, please check the code")
    
    inputs = []
    for arg in code[0].args.args:
        if isinstance(arg, ast.arg):
            assert isinstance(arg.arg, str)
            inputs.append(arg.arg)
        elif isinstance(arg, ast.Name):
            inputs.append(arg.id)
        else:
            raise Exception("Invalid arg: %r" % ast.dump(arg))
    
    body = []
    returned = False
    for c in code[0].body:
        if not isinstance(c, (ast.Assign, ast.Return)):
            raise Exception("only variable assignment and return are supported")
        if returned:
            raise Exception("Cannot do stuff after a return statement")
        if isinstance(c, ast.Return):
            returned = True
        body.append(c)
    return inputs, body

def flatten_body(body):
    output = []
    for c in body:
        output.extend(flatten_stmt(c))
    return output

next_symbol = [0]
def mksymbol():
    next_symbol[0] += 1
    return 'sym_' + str(next_symbol[0])

def flatten_stmt(stmt):
    target = ''
    if isinstance(stmt, ast.Assign):
        assert len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name)
        target = stmt.targets[0].id
    elif isinstance(stmt, ast.Return):
        target = "~out"
    
    return flatten_expr(target, stmt.value)


def flatten_expr(target, expr):
    # x = y
    if isinstance(expr, ast.Name):
        return [['set', target, expr.id]]
    
    # x = 5
    elif isinstance(expr, ast.Num):
        return [['set', target, expr.n]]
    
    # x = y (op) z
    elif isinstance(expr, ast.BinOp):
        if isinstance(expr.op, ast.Add):
            op = '+'
        elif isinstance(expr.op, ast.Mult):
            op = '*'
        elif isinstance(expr.op, ast.Sub):
            op = '-'
        elif isinstance(expr.op, ast.Div):
            op = '/'
        elif isinstance(expr.op, ast.Pow):
            assert isinstance(expr.right, ast.Num)
            if expr.right.n == 0:
                return [['set', target, 1]]
            elif expr.right.n == 1:
                return flatten_expr(target, expr.left)
            else:
                if isinstance(expr.left, (ast.Name, ast.Num)):
                    nxt = base = expr.left.id if isinstance(expr.left, ast.Name) else expr.left.n
                    o = []
                else:
                    nxt = base = mksymbol()
                    o = flatten_expr(base, expr.left)
                for i in range(1, expr.right.n):
                    latest = nxt
                    nxt = target if i == expr.right.n - 1 else mksymbol()
                    o.append(['*', nxt, latest, base])
                return o
        else:
            raise Exception("bad operation: %s" % ast.dump(stmt.op))
        
        if isinstance(expr.left, (ast.Name, ast.Num)):
            var1 = expr.left.id if isinstance(expr.left, ast.Name) else expr.left.n
            sub1 = []
        else:
            var1 = mksymbol()
            sub1 = flatten_expr(var1, expr.left)
        
        if isinstance(expr.right, (ast.Name, ast.Num)):
            var2 = expr.right.id if isinstance(expr.right, ast.Name) else expr.right.n
            sub2 = flatten_expr(var2, expr.right)
        return sub1 + sub2 + [[op, target, var1, var2]]
    else:
        raise Exception("unexpected statement value: %r" % stmt.value)

code = """
def qeval(x):
    y = x**3
    return y + x + 5
"""
inputs, body = extract_inputs_and_body(parse(code))

print("Inputs", inputs)
print("body", body)
print(flatten_body(body))

