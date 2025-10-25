from pathlib import Path
import ast

def test_single_definition_of_pk_heuristic():
    src = Path("src/phase2/dq_runner.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_suggest_primary_keys"]
    assert len(defs) == 1
