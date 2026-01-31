# -*- coding:utf-8 -*-
import sys
import types
import importlib
import os
from io import BytesIO
import pytest
from types import SimpleNamespace

# -------------------------
# Helper fixture: import the app with fake external dependencies
# -------------------------
@pytest.fixture
def app_module(monkeypatch, tmp_path, request):
    """
    Ensure money_app_v3 is (re)imported in a safe environment:
    - inject fake streamlit, openai, google.generativeai, PIL modules before import
    - return the imported module object
    """
    # --- fake streamlit ---
    st = types.ModuleType("streamlit")
    st.set_page_config = lambda *a, **k: None
    st.markdown = lambda *a, **k: None
    st.secrets = SimpleNamespace(get=lambda k, default=None: None)
    # sidebar object with expected methods
    class _Sidebar:
        def header(self, *a, **k): return None
        def text_input(self, *a, **k): return ""
        def divider(self, *a, **k): return None
        def markdown(self, *a, **k): return None
        def code(self, *a, **k): return None
        def caption(self, *a, **k): return None
        def expander(self, *a, **k):
            return self
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
    st.sidebar = _Sidebar()
    st.header = lambda *a, **k: None
    st.text_input = lambda *a, **k: ""
    st.divider = lambda *a, **k: None
    st.code = lambda *a, **k: None
    st.caption = lambda *a, **k: None
    st.title = lambda *a, **k: None
    st.session_state = {}
    st.file_uploader = lambda *a, **k: None
    st.image = lambda *a, **k: None
    st.button = lambda *a, **k: False
    st.text_area = lambda *a, **k: ""  # used at import-time in app
    class _Spinner:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
    st.spinner = lambda *a, **k: _Spinner()
    st.success = lambda *a, **k: None
    st.error = lambda *a, **k: None
    st.warning = lambda *a, **k: None
    st.balloons = lambda *a, **k: None
    st.columns = lambda n: (_Sidebar(), _Sidebar())
    st.expander = lambda title: _Sidebar()
    st.write = lambda *a, **k: None

    # --- fake openai (module) ---
    openai_mod = types.ModuleType("openai")
    # Provide a placeholder OpenAI so import doesn't fail; tests will override behavior as needed
    openai_mod.OpenAI = lambda *a, **k: None

    # --- fake google.generativeai ---
    google_pkg = types.ModuleType("google")
    genai_mod = types.ModuleType("google.generativeai")
    genai_mod.GenerativeModel = lambda *a, **k: None
    google_pkg.generativeai = genai_mod

    # --- fake PIL with Image.open ---
    pil_mod = types.ModuleType("PIL")
    class FakeImage:
        @staticmethod
        def open(f):
            # return a sentinel image object; tests may override
            return "IMG_OBJ"
    pil_mod.Image = FakeImage

    # inject into sys.modules before importing the app
    monkeypatch.setitem(sys.modules, "streamlit", st)
    monkeypatch.setitem(sys.modules, "openai", openai_mod)
    monkeypatch.setitem(sys.modules, "google", google_pkg)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai_mod)
    monkeypatch.setitem(sys.modules, "PIL", pil_mod)

    # Ensure fresh import
    if "money_app_v3" in sys.modules:
        del sys.modules["money_app_v3"]

    # Import the target module
    mod = importlib.import_module("money_app_v3")
    return mod

# -------------------------
# Tests
# -------------------------

def test_load_valid_keys_creates_and_reads(tmp_path, app_module):
    """
    When keys.txt does not exist, load_valid_keys should create it and return default.
    When keys.txt exists, should read and return lines (stripped).
    """
    mod = app_module
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        # Ensure file does not exist
        if (tmp_path / "keys.txt").exists():
            (tmp_path / "keys.txt").unlink()
        keys = mod.load_valid_keys()
        assert keys == ["ADMIN123"]
        assert (tmp_path / "keys.txt").exists()

        # Write custom keys and read again
        (tmp_path / "keys.txt").write_text("CODE1\nCODE2\n", encoding="utf-8")
        keys2 = mod.load_valid_keys()
        assert keys2 == ["CODE1", "CODE2"]
    finally:
        os.chdir(cwd)

def test_get_ielts_feedback_uses_mock_openai(app_module, monkeypatch):
    """
    Replace the OpenAI client used in module with a FakeOpenAI that returns a predictable structure.
    """
    mod = app_module

    # Fake OpenAI client class that matches the usage in get_ielts_feedback
    class FakeChoice:
        def __init__(self, text):
            self.message = SimpleNamespace(content=text)
    class FakeResponse:
        def __init__(self, text):
            self.choices = [FakeChoice(text)]
    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            # Provide nested attribute chat.completions.create
            self.chat = SimpleNamespace(completions=SimpleNamespace(
                create=lambda **kwargs: FakeResponse("FAKE_REPORT_FROM_DEEPSEEK")
            ))

    # Override the OpenAI symbol in the imported module
    monkeypatch.setattr(mod, "OpenAI", FakeOpenAI, raising=False)

    res = mod.get_ielts_feedback("some essay text", api_key="DUMMY")
    assert isinstance(res, str)
    assert "FAKE_REPORT_FROM_DEEPSEEK" in res

def test_upload_to_gemini_success_and_fallback(app_module, monkeypatch):
    """
    Test: when flash model works -> returns flash result; when flash raises -> fallback to pro result.
    """
    mod = app_module

    # Override Image.open to return a sentinel
    monkeypatch.setattr(mod, "Image", types.SimpleNamespace(open=lambda f: "IMG_OBJ"), raising=False)

    # Fake GenerativeModel that can be configured to raise for flash
    class FakeGenModel:
        raise_on_flash = False
        def __init__(self, model_name):
            self.model_name = model_name
        def generate_content(self, args):
            if "flash" in self.model_name and FakeGenModel.raise_on_flash:
                raise RuntimeError("flash not available")
            class R: pass
            r = R(); r.text = f"{self.model_name}-result"
            return r

    # Patch module's genai.GenerativeModel to our FakeGenModel
    if hasattr(mod, "genai"):
        monkeypatch.setattr(mod.genai, "GenerativeModel", FakeGenModel, raising=False)
    else:
        # fallback: set attribute on module
        fake_genai = types.SimpleNamespace(GenerativeModel=FakeGenModel)
        monkeypatch.setattr(mod, "genai", fake_genai, raising=False)

    # Case 1: flash works
    FakeGenModel.raise_on_flash = False
    fake_file = BytesIO(b"fake-image-bytes")
    res1 = mod.upload_to_gemini(fake_file)
    assert res1 == "models/gemini-1.5-flash-result"

    # Case 2: flash fails -> fallback to pro
    FakeGenModel.raise_on_flash = True
    fake_file2 = BytesIO(b"fake-image-bytes")
    res2 = mod.upload_to_gemini(fake_file2)
    assert res2 == "models/gemini-1.5-pro-result"
