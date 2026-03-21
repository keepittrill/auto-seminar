"""
auto-seminar build.py 단위 테스트
pytest tests/test_build.py
"""
import sys
import pathlib

# scripts/ 디렉토리를 경로에 추가
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import build as B


# ─────────────────────────────────────────────────────────────────
# split_fm / build_fm
# ─────────────────────────────────────────────────────────────────

class TestSplitFm:
    def test_no_frontmatter(self):
        fm, body = B.split_fm("# 제목\n내용")
        assert fm == {}
        assert body == "# 제목\n내용"

    def test_basic_frontmatter(self):
        text = "---\nmarp: true\ntheme: default\n---\n# 본문"
        fm, body = B.split_fm(text)
        assert fm["marp"] is True
        assert fm["theme"] == "default"
        assert body.strip() == "# 본문"

    def test_empty_frontmatter(self):
        fm, body = B.split_fm("---\n---\n내용")
        assert fm == {}
        assert "내용" in body

    def test_no_closing_delimiter(self):
        # 닫는 --- 없으면 frontmatter 없이 반환
        fm, body = B.split_fm("---\nmarp: true\n본문")
        assert fm == {}

    def test_unicode_values(self):
        text = "---\ntitle: 안녕하세요\n---\n본문"
        fm, _ = B.split_fm(text)
        assert fm["title"] == "안녕하세요"


class TestBuildFm:
    def test_roundtrip(self):
        fm = {"marp": True, "theme": "catppuccin", "paginate": True}
        body = "\n# 제목\n\n내용"
        result = B.build_fm(fm, body)
        assert result.startswith("---\n")
        assert "marp: true" in result
        assert "theme: catppuccin" in result
        assert "# 제목" in result

    def test_unicode_roundtrip(self):
        fm = {"title": "한국어 제목"}
        body = "본문"
        result = B.build_fm(fm, body)
        assert "한국어 제목" in result


# ─────────────────────────────────────────────────────────────────
# first_title
# ─────────────────────────────────────────────────────────────────

class TestFirstTitle:
    def test_basic(self):
        assert B.first_title("# 제목\n내용") == "제목"

    def test_with_leading_space(self):
        assert B.first_title("# Hello World\n") == "Hello World"

    def test_no_title(self):
        assert B.first_title("내용만 있고 제목 없음") == "Untitled"

    def test_h2_not_counted(self):
        # ## 는 title로 인식하지 않음
        assert B.first_title("## 섹션\n내용") == "Untitled"

    def test_title_with_special_chars(self):
        assert B.first_title("# 제목: 부제 (2024)") == "제목: 부제 (2024)"

    def test_multiline_finds_first(self):
        body = "intro\n# 첫 번째 제목\n내용\n# 두 번째 제목"
        assert B.first_title(body) == "첫 번째 제목"


# ─────────────────────────────────────────────────────────────────
# first_desc
# ─────────────────────────────────────────────────────────────────

class TestFirstDesc:
    def test_blockquote(self):
        body = "# 제목\n> 설명 텍스트\n내용"
        assert B.first_desc(body) == "설명 텍스트"

    def test_plain_paragraph(self):
        body = "# 제목\n\n이것이 설명 단락입니다."
        assert B.first_desc(body) == "이것이 설명 단락입니다."

    def test_skips_headings(self):
        body = "# 제목\n\n## 섹션\n\n실제 단락"
        assert B.first_desc(body) == "실제 단락"

    def test_skips_code_block(self):
        body = "# 제목\n\n```python\ncode\n```\n\n설명"
        assert B.first_desc(body) == "설명"

    def test_truncates_long_text(self):
        long = "a" * 200
        result = B.first_desc(f"# 제목\n\n{long}")
        assert len(result) <= 103  # 100 chars + "…"
        assert result.endswith("…")

    def test_empty_body(self):
        assert B.first_desc("") == ""

    def test_prefers_blockquote_over_paragraph(self):
        body = "일반 단락\n\n> blockquote 설명"
        assert B.first_desc(body) == "blockquote 설명"


# ─────────────────────────────────────────────────────────────────
# slide_count
# ─────────────────────────────────────────────────────────────────

class TestSlideCount:
    def test_no_h2(self):
        # h2 없으면 최소 1
        assert B.slide_count("# 제목\n내용") == 1

    def test_single_h2(self):
        body = "# 제목\n\n## 섹션1\n내용"
        assert B.slide_count(body) == 1

    def test_multiple_h2(self):
        body = "# 제목\n\n## 섹션1\n내용\n\n## 섹션2\n내용\n\n## 섹션3\n내용"
        assert B.slide_count(body) == 3

    def test_empty_body(self):
        assert B.slide_count("") == 1

    def test_h3_not_counted(self):
        body = "## 섹션1\n\n### 하위1\n### 하위2\n### 하위3"
        assert B.slide_count(body) == 1


# ─────────────────────────────────────────────────────────────────
# THEME_META integrity
# ─────────────────────────────────────────────────────────────────

class TestThemeMeta:
    def test_all_themes_have_label(self):
        for key, val in B.THEME_META.items():
            assert isinstance(val[0], str) and val[0], f"{key}: label이 없음"

    def test_all_themes_have_description(self):
        for key, val in B.THEME_META.items():
            assert isinstance(val[1], str) and val[1], f"{key}: description이 없음"

    def test_all_themes_have_colors(self):
        for key, val in B.THEME_META.items():
            assert isinstance(val[2], list), f"{key}: colors가 list가 아님"
            assert len(val[2]) >= 3, f"{key}: colors가 3개 미만"
            for c in val[2]:
                assert c.startswith('#') and len(c) == 7, f"{key}: 잘못된 hex 색상 {c!r}"

    def test_custom_themes_have_css_file(self):
        themes_dir = pathlib.Path(__file__).parent.parent / "themes"
        marp_builtin = {"default", "gaia", "uncover"}
        for key in B.THEME_META:
            if key in marp_builtin:
                continue
            css = themes_dir / f"{key}.css"
            assert css.exists(), f"themes/{key}.css 파일이 없음"

    def test_no_duplicate_keys(self):
        # dict이므로 자동으로 중복 없음 — 키 개수 확인
        assert len(B.THEME_META) == len(set(B.THEME_META.keys()))

    def test_expected_themes_present(self):
        expected = [
            "catppuccin", "gradient-dark", "minimal-white", "tech-dark",
            "ocean", "corporate", "retro", "nord", "sunset", "pastel",
            "monochrome", "aurora", "solarized", "sunshine", "sakura", "mint",
            "sky", "grape", "coffee",
            "slate", "lavender", "paper",
            "default", "gaia", "uncover",
        ]
        for t in expected:
            assert t in B.THEME_META, f"'{t}' 테마가 THEME_META에 없음"
