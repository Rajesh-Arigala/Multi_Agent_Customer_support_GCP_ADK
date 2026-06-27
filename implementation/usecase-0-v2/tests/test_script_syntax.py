import py_compile
from pathlib import Path


def test_project_scripts_compile(tmp_path):
    script_paths = [
        Path("scripts/build_vertex_embeddings.py"),
        Path("scripts/smoke_vertex_embeddings.py"),
        Path("scripts/smoke_hybrid_retrieval.py"),
        Path("scripts/smoke_agent_local.py"),
    ]

    for script_path in script_paths:
        cfile = tmp_path / f"{script_path.stem}.pyc"
        py_compile.compile(str(script_path), cfile=str(cfile), doraise=True)
