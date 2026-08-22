import os
import sys
import unittest
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
sys.path.insert(0, str(PYTHON_PACKAGES))
sys.path.insert(0, str(ROOT))

def run_all_tests():
    print("=" * 70)
    print("MAICA-MTTS Synbrace Test Suite (Python 3.12 / Ren'Py 8.5.0)")
    print("=" * 70)

    test_dir = ROOT / "tests"
    test_files = sorted(test_dir.glob("test_*.py"))
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    failures_list = []

    for test_file in test_files:
        module_name = f"tests.{test_file.stem}"
        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            print(f"[ERROR importing {test_file.name}]: {e}")
            total_failed += 1
            failures_list.append((test_file.name, str(e)))
            continue

        test_functions = [
            getattr(mod, name)
            for name in dir(mod)
            if name.startswith("test_") and callable(getattr(mod, name))
        ]

        print(f"\nRunning {test_file.name} ({len(test_functions)} tests)...")

        for fn in test_functions:
            total_tests += 1
            test_name = f"{test_file.stem}::{fn.__name__}"
            try:
                # Handle test functions that accept tmp_path or fixture args
                import inspect
                sig = inspect.signature(fn)
                if len(sig.parameters) == 0:
                    fn()
                else:
                    import tempfile
                    with tempfile.TemporaryDirectory() as tmpdir:
                        kwargs = {}
                        if "tmp_path" in sig.parameters:
                            kwargs["tmp_path"] = Path(tmpdir)
                        if "monkeypatch" in sig.parameters:
                            class MonkeyPatcher:
                                def setattr(self, target, name_or_value, value=None):
                                    if value is None and isinstance(target, str):
                                        mod_name, attr = target.rsplit(".", 1)
                                        mod = sys.modules[mod_name]
                                        setattr(mod, attr, name_or_value)
                                    else:
                                        setattr(target, name_or_value, value)
                            kwargs["monkeypatch"] = MonkeyPatcher()
                        if "instance" in sig.parameters:
                            import mtts_package
                            inst = mtts_package.MTTS(
                                url="https://example.test/tts/",
                                token="secret-token",
                                cache_path=tmpdir,
                            )
                            inst._MTTS__accessable = True
                            kwargs["instance"] = inst
                        fn(**kwargs)
                print(f"  [PASS] {fn.__name__}")
                total_passed += 1
            except Exception as e:
                print(f"  [FAIL] {fn.__name__}: {e}")
                total_failed += 1
                failures_list.append((test_name, str(e)))

    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_passed} passed, {total_failed} failed, total {total_tests} tests.")
    print("=" * 70)

    if total_failed > 0:
        print("\nFailures:")
        for name, err in failures_list:
            print(f" - {name}: {err}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run_all_tests())
