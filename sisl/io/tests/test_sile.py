import pytest
from pathlib import Path
import os.path as osp

from sisl.io.sile import __siles

pytestmark = pytest.mark.only
_dir = osp.join("sisl", "io")


@pytest.mark.parametrize("pickle_mod", ["pickle", "dill"])
@pytest.mark.parametrize("sile_cls", __siles)
def test_sile_pickling(sisl_tmp, sile_cls, pickle_mod):
    # fail if module is not available
    pickle_mod = pytest.importorskip(pickle_mod)

    # sisl_tmp is a global fixture to retrieve files
    # This fixture also automatically deletes files
    tmp_file = sisl_tmp.file("test", _dir)

    # Create sile
    sile = sile_cls(tmp_file, _open=False)

    with open(tmp_file, "wb") as fh:
        pickle_mod.dump(sile, fh)

    with open(tmp_file, "rb") as fh:
        loaded_sile = pickle_mod.load(fh)
