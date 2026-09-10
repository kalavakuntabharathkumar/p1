import ast, re

def scan_python(filename: str, code: str) -> list[dict]:
    out=[]
    try: tree=ast.parse(code, filename=filename)
    except SyntaxError as e:
        return [{"tool":"heuristic","rule_id":"PY_SYNTAX","severity":"MEDIUM","confidence":"HIGH","filename":filename,"line":e.lineno or 0,"message":"Python syntax error"}]
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"execute","executemany"} and node.args:
            arg=node.args[0]
            risky=isinstance(arg,ast.JoinedStr) or (isinstance(arg,ast.BinOp) and isinstance(arg.op,(ast.Add,ast.Mod)))
            if risky:
                out.append({"tool":"heuristic","rule_id":"SQLI001","severity":"HIGH","confidence":"MEDIUM","filename":filename,"line":node.lineno,"message":"Possible SQL injection: dynamically constructed SQL passed to execute()"})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval","exec"}:
            out.append({"tool":"heuristic","rule_id":"EXEC001","severity":"HIGH","confidence":"HIGH","filename":filename,"line":node.lineno,"message":f"Use of {node.func.id}() on potentially untrusted data"})
    for i,line in enumerate(code.splitlines(),1):
        if re.search(r"(?i)(api[_-]?key|secret|password)\s*=\s*[\"\'][^\"\']{8,}[\"\']", line):
            out.append({"tool":"heuristic","rule_id":"SECRET001","severity":"HIGH","confidence":"MEDIUM","filename":filename,"line":i,"message":"Possible hard-coded secret"})
    return out
