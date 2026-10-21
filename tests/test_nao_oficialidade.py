"""Trava automatizada da regra que torna o painel publicável (RF-10, RNF-S08, RR-05).

Não é teste de fachada: RR-05 é o risco de maior probabilidade e impacto do
projeto, e a regra que o mitiga é fácil de quebrar sem perceber.
"""

import pathlib

import src

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# Termos que caracterizam uso de símbolo/identidade oficial do Estado (RNF-S08).
TERMOS_PROIBIDOS = ["brasão", "brasao", "governo do estado do tocantins publica"]


def test_aviso_tem_os_tres_elementos_obrigatorios():
    aviso = src.AVISO_NAO_OFICIALIDADE.lower()
    assert "unitins" in aviso
    assert "não é canal oficial" in aviso
    assert "fontes públicas" in aviso


def test_readme_carrega_o_aviso_de_nao_oficialidade():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8").lower()
    assert "não é um canal oficial do governo do tocantins" in readme
    assert "unitins" in readme


def test_readme_nao_usa_simbolo_oficial_do_estado():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8").lower()
    for termo in TERMOS_PROIBIDOS:
        assert termo not in readme, f"termo proibido no README: {termo}"


def test_conta_projeto_nunca_aparece_em_texto_publico():
    """dadosgovtocantins@ é conta de infraestrutura e nunca pode ser exposta (PRD 2.3)."""
    for arquivo in [RAIZ / "README.md", RAIZ / "LICENSE"]:
        assert "dadosgovtocantins" not in arquivo.read_text(encoding="utf-8")
