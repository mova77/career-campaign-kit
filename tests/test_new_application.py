import datetime as dt
import shutil
from pathlib import Path

import pytest

import new_application as na

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("text, slug", [
    ("Acme Corp", "acme-corp"),
    ("Łódź Software Sp. z o.o.", "lodz-software-sp-z-o-o"),
    ("Senior PM / Delivery Lead", "senior-pm-delivery-lead"),
    ("Straße & Söhne", "strasse-sohne"),
    ("!!!", "x"),
])
def test_slugify(text, slug):
    assert na.slugify(text) == slug


def test_slugify_truncates():
    assert len(na.slugify("a" * 100)) == 40


@pytest.fixture
def fake_root(tmp_path):
    shutil.copytree(ROOT / "applications" / "_template", tmp_path / "applications" / "_template")
    (tmp_path / "cv" / "data").mkdir(parents=True)
    return tmp_path


def test_scaffold_fills_placeholders(fake_root):
    target = na.scaffold("Acme", "Project Manager", dt.date(2026, 11, 3), root=fake_root)
    assert target.name == "2026-11-03-acme-project-manager"
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "# Acme — Project Manager" in readme
    for f in target.rglob("*.md"):
        assert "{{" not in f.read_text(encoding="utf-8"), f
    assert not (target / "cv.yaml").exists()      # no master yet


def test_scaffold_copies_master(fake_root):
    (fake_root / "cv" / "data" / "master.yaml").write_text("lang: en\n", encoding="utf-8")
    target = na.scaffold("Acme", "PM", dt.date(2026, 1, 1), root=fake_root)
    assert (target / "cv.yaml").read_text(encoding="utf-8") == "lang: en\n"


def test_scaffold_refuses_overwrite(fake_root):
    na.scaffold("Acme", "PM", dt.date(2026, 1, 1), root=fake_root)
    with pytest.raises(FileExistsError):
        na.scaffold("Acme", "PM", dt.date(2026, 1, 1), root=fake_root)
