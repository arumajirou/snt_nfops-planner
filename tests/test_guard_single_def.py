from pathlib import Path, PurePath
import re
def test_single_definition_of_pk_heuristic():
    p = Path("src/phase2/dq_runner.py")
    txt = p.read_text(encoding="utf-8")
    assert len(list(re.finditer(r"^def _suggest_primary_keys\\(", txt, re.M))) == 1
