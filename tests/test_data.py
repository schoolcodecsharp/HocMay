import sqlite3
import numpy as np
import pytest
from src.common import ROOT
from src.data import load_california_housing, EXPECTED_FEATURES, TARGET
from src.database import read_cadata, to_features, DB_PATH
from src.split import split_ids
from src.features import linear_pipeline


def test_split_disjoint_complete_and_reproducible():
    ids = split_ids()
    assert ids == split_ids()
    sets = [set(v) for v in ids.values()]
    assert len(set.union(*sets)) == 20640
    assert sum(map(len, sets)) == 20640
    assert [len(v) for v in ids.values()] == [14448, 3096, 3096]


def test_scaler_fits_train_only():
    frame = load_california_housing()
    train = frame.iloc[split_ids()["train"]]
    pipe = linear_pipeline().fit(train[EXPECTED_FEATURES], train[TARGET])
    np.testing.assert_allclose(
        pipe.named_steps["scaler"].mean_, train[EXPECTED_FEATURES].mean()
    )
    assert pipe.named_steps["scaler"].n_samples_seen_ == 14448


@pytest.mark.skipif(
    not (ROOT / "houses/cadata.txt").exists(),
    reason="Optional local source not downloaded",
)
def test_cadata_matches_official_dataset():
    np.testing.assert_allclose(
        to_features(read_cadata(ROOT / "houses/cadata.txt")),
        load_california_housing(),
        rtol=0,
        atol=1e-12,
    )


@pytest.mark.skipif(
    not DB_PATH.exists(), reason="Run src.database for database integration tests"
)
def test_database_integrity():
    with sqlite3.connect(DB_PATH) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert (
            conn.execute("SELECT count(*) FROM housing_features").fetchone()[0] == 20640
        )
        assert (
            conn.execute("SELECT count(*) FROM split_membership").fetchone()[0] == 20640
        )
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_invalid_cadata_is_rejected(tmp_path):
    path = tmp_path / "cadata.txt"
    path.write_text("Header only\nNot a dataset", encoding="utf-8")
    with pytest.raises(ValueError, match="9"):
        read_cadata(path)


def test_short_cadata_is_rejected(tmp_path):
    path = tmp_path / "cadata.txt"
    path.write_text("100000 2 20 100 20 50 10 35 -120\n", encoding="utf-8")
    with pytest.raises(ValueError, match="20.640"):
        read_cadata(path)


@pytest.mark.skipif(not DB_PATH.exists(), reason="Requires local database")
def test_database_import_idempotent_and_detects_split_changes(tmp_path):
    import shutil
    from src.database import build_database

    source = ROOT / "houses/cadata.txt"
    if not source.exists():
        pytest.skip("Requires local cadata")
    copy = tmp_path / "copy.sqlite3"
    shutil.copy2(DB_PATH, copy)
    assert build_database(source, copy)["source_sha256"]
    with sqlite3.connect(copy) as conn:
        conn.execute(
            "UPDATE split_membership SET split='test' WHERE row_id=(SELECT row_id FROM split_membership WHERE split='train' LIMIT 1)"
        )
    with pytest.raises(ValueError, match="Split"):
        build_database(source, copy)
