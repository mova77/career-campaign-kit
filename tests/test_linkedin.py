import io
import json
import urllib.error
import zipfile

import pytest

import build_cv
import linkedin_import as li
import linkedin_post as lp

POSITIONS_CSV = (
    "Company Name,Title,Description,Location,Started On,Finished On\n"
    'Northwind Bank,Senior Project Manager,"Led core-banking migration.\n- Ran 6 projects",Warsaw,Mar 2021,\n'
    "Contoso,Project Manager,,Kraków,Jun 2017,Feb 2021\n"
)
PROFILE_CSV = (
    "First Name,Last Name,Maiden Name,Address,Birth Date,Headline,Summary,Industry,Zip Code,Geo Location,Twitter Handles,Websites,Instant Messengers\n"
    'Alex,Example,,Secret St 1,"Jan 1, 1990",Project Manager,Delivers things.,Banking,00-001,"Warsaw, Poland",,[PORTFOLIO:https://linkedin.com/in/alex-example],\n'
)
SKILLS_CSV = "Name\nRisk Management\nJira\n"
LANG_CSV = "Name,Proficiency\nPolish,NATIVE_OR_BILINGUAL\nEnglish,Full professional proficiency\n"
EDU_CSV = "School Name,Start Date,End Date,Notes,Degree Name,Activities\nUEK,2010,2015,,MSc Management,Debate club\n"


@pytest.fixture
def export_zip(tmp_path):
    p = tmp_path / "Basic_LinkedInDataExport.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("Positions.csv", "﻿" + POSITIONS_CSV)        # BOM, as LinkedIn ships it
        zf.writestr("Profile.csv", PROFILE_CSV)
        zf.writestr("Skills.csv", "Notes:\nsome preamble\n\n" + SKILLS_CSV)
        zf.writestr("Languages.csv", LANG_CSV)
        zf.writestr("nested/Education.csv", EDU_CSV)
    return p


@pytest.mark.parametrize("raw, out", [
    ("Mar 2021", "2021-03"), ("March 2021", "2021-03"), ("Sept. 2020", "2020-09"),
    ("2021", "2021"), ("03/2021", "2021-03"), ("2021-3-15", "2021-03"),
    ("", None), ("Present", None),
])
def test_parse_date(raw, out):
    assert li.parse_date(raw) == out


def test_split_bullets():
    assert li.split_bullets("One.\n- Two\n• Three\n\n") == ["One.", "Two", "Three"]


def test_zip_import_normalises(export_zip):
    data = li.load_zip(export_zip)
    draft = li.normalise(data, "test")
    assert draft["person"] == {"name": "Alex Example", "headline": "Project Manager",
                               "location": "Warsaw, Poland",
                               "linkedin": "https://linkedin.com/in/alex-example"}
    job = draft["experience"][0]
    assert (job["company"], job["start"], job["end"]) == ("Northwind Bank", "2021-03", "present")
    assert job["bullets"] == ["Led core-banking migration.", "Ran 6 projects"]
    assert draft["experience"][1]["end"] == "2021-02"
    assert draft["skills"][0]["items"] == ["Risk Management", "Jira"]
    assert draft["languages"][0] == {"name": "Polish", "level": "Native or bilingual"}
    assert draft["education"][0]["details"] == "Debate club"


def test_private_fields_dropped(export_zip):
    prof = li.load_zip(export_zip)["PROFILE"][0]
    assert "Birth Date" not in prof and "Address" not in prof and "Zip Code" not in prof
    assert "Secret St" not in json.dumps(li.normalise(li.load_zip(export_zip), "t"))


def test_draft_is_valid_cv(export_zip, tmp_path):
    draft = li.normalise(li.load_zip(export_zip), "t")
    out = tmp_path / "d.yaml"
    li.write_draft(draft, out)
    cv = build_cv.load_cv(out)                 # draft must pass schema & render
    assert "Northwind Bank" in build_cv.render_html(cv)


# ── DMA API with a fake HTTP opener ──

class FakeResp(io.BytesIO):
    def __init__(self, payload, headers=None, status=200):
        super().__init__(json.dumps(payload).encode())
        self.headers, self.status = headers or {}, status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def make_opener(pages, record):
    calls = iter(pages)

    def opener(req, timeout=None):
        record.append(req)
        nxt = next(calls)
        if isinstance(nxt, Exception):
            raise nxt
        return FakeResp(nxt)
    return opener


def test_fetch_domain_paginates_and_stops_on_no_data():
    seen = []
    page1 = {"paging": {"links": [{"rel": "next", "href": "/rest/memberSnapshotData?q=criteria&domain=SKILLS&start=1&count=10"}]},
             "elements": [{"snapshotDomain": "SKILLS", "snapshotData": [{"Name": "Jira"}]}]}
    page2 = {"paging": {"links": [{"rel": "next", "href": "/rest/memberSnapshotData?start=2"}]},
             "elements": [{"snapshotDomain": "SKILLS", "snapshotData": [{"Name": "SQL"}]}]}
    end = urllib.error.HTTPError("u", 404, "Not Found", {}, io.BytesIO(b'{"message":"No data found for this memberId"}'))
    recs = li.fetch_domain("SKILLS", "tok", make_opener([page1, page2, end], seen))
    assert [r["Name"] for r in recs] == ["Jira", "SQL"]
    assert seen[0].get_header("Linkedin-version") == "202312"
    assert seen[0].get_header("Authorization") == "Bearer tok"
    assert seen[1].full_url.startswith("https://api.linkedin.com/rest/memberSnapshotData?q=criteria&domain=SKILLS&start=1")


def test_fetch_domain_raises_on_auth_error():
    err = urllib.error.HTTPError("u", 401, "Unauthorized", {}, io.BytesIO(b"expired"))
    with pytest.raises(RuntimeError, match="HTTP 401"):
        li.fetch_domain("PROFILE", "bad", make_opener([err], []))


def test_api_cli_requires_token(monkeypatch, capsys):
    monkeypatch.delenv("LINKEDIN_DMA_TOKEN", raising=False)
    assert li.main(["api"]) == 2
    assert "LINKEDIN_DMA_TOKEN" in capsys.readouterr().err


# ── posting ──

def test_escape_little_text():
    assert lp.escape_little_text("Hi (team) #hiring @x *b*") == r"Hi \(team\) \#hiring \@x \*b\*"


def test_payload_limits():
    with pytest.raises(ValueError):
        lp.build_payload("urn:li:person:1", "x" * 3001)
    with pytest.raises(ValueError):
        lp.build_payload("urn:li:person:1", "   ")


def test_dry_run_sends_nothing(tmp_path, capsys, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used in dry run")
    monkeypatch.setattr(lp.urllib.request, "urlopen", boom)
    f = tmp_path / "p.md"
    f.write_text("Back to work in January (PM roles)!", encoding="utf-8")
    assert lp.main([str(f)]) == 0
    assert "DRY RUN" in capsys.readouterr().out


def test_publish_requests():
    seen = []

    def opener(req, timeout=None):
        seen.append(req)
        if req.full_url == lp.USERINFO_URL:
            return FakeResp({"sub": "abc"})
        return FakeResp({}, headers={"x-restli-id": "urn:li:share:9"}, status=201)

    urn = lp.get_author_urn("t", opener)
    pid = lp.publish(lp.build_payload(urn, "hello"), "t", "202510", opener)
    assert pid == "urn:li:share:9"
    post = seen[1]
    assert post.get_method() == "POST"
    assert post.get_header("Linkedin-version") == "202510"
    assert post.get_header("X-restli-protocol-version") == "2.0.0"
    assert json.loads(post.data)["author"] == "urn:li:person:abc"
