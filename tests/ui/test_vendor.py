"""Arquivos de terceiros servidos pelo próprio site (Task 36): versão fixa, licença e SHA-256 conferidos."""

import base64
import hashlib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).parents[2]
VENDOR = RAIZ / "src" / "ui" / "vendor"
MANIFESTO = RAIZ / "tests" / "fixtures" / "vendor_sha256.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_todo_arquivo_de_terceiros_tem_o_sha256_registrado_e_nao_mudou():
    """Trocar um arquivo do vendor exige atualizar o manifesto de propósito (revisão), nunca por acidente."""
    esperado = json.loads(MANIFESTO.read_text("utf-8"))
    atual = {
        p.relative_to(VENDOR).as_posix(): _sha(p) for p in sorted(VENDOR.rglob("*")) if p.is_file()
    }
    assert atual == esperado


def test_cada_biblioteca_traz_a_sua_licenca():
    for pasta, licenca in (("react", "LICENSE"), ("phosphor", "LICENSE"), ("inter", "LICENSE.txt")):
        texto = (VENDOR / pasta / licenca).read_text("utf-8")
        assert "MIT License" in texto or "SIL Open Font License" in texto, pasta


def test_react_servido_localmente_bate_com_o_sri_do_runtime():
    """O runtime (support.js) guarda o SHA-384 do React 18.3.1 original: a cópia local tem de ser idêntica."""
    runtime = (RAIZ / "support.js").read_text("utf-8")
    for var, arquivo in (
        ("REACT_SRI", "react.production.min.js"),
        ("REACT_DOM_SRI", "react-dom.production.min.js"),
    ):
        sri = re.search(rf'var {var} = "sha384-([^"]+)"', runtime).group(1)
        assert (
            base64.b64encode(
                hashlib.sha384((VENDOR / "react" / arquivo).read_bytes()).digest()
            ).decode()
            == sri
        )
    assert 'REACT_URL = "./src/ui/vendor/react/react.production.min.js"' in runtime
    assert 'REACT_DOM_URL = "./src/ui/vendor/react/react-dom.production.min.js"' in runtime


def test_runtime_nao_busca_nada_fora_do_site():
    runtime = (RAIZ / "support.js").read_text("utf-8")
    assert not re.search(r"https?://", runtime)


def test_phosphor_so_declara_a_fonte_que_o_site_serve():
    css = (VENDOR / "phosphor" / "style.css").read_text("utf-8")
    assert re.findall(r'url\("([^"]+)"\)', css) == ["./Phosphor.woff2"]
    assert (VENDOR / "phosphor" / "Phosphor.woff2").is_file()
