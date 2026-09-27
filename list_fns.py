import ast, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
tree = ast.parse(open('backend/physics_twin.py', encoding='utf-8').read())
for n in ast.walk(tree):
    if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
        print(f"L{n.lineno:4}: {type(n).__name__:15} {n.name}")
