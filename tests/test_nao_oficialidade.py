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


def test_email_da_conta_de_infraestrutura_nunca_aparece_em_texto_publico():
    """O e-mail da conta de infraestrutura nunca pode ser exposto (PRD 2.3, RNF-S08). O NOME da conta e o
    endereço do painel são públicos por escolha do Bruno (task 36): o que se proíbe é o e-mail, isto é, o
    nome da conta seguido de "@". O padrão completo (local, segredo do CI) é conferido por varrer_segredos.sh."""
    publicos = [RAIZ / "README.md", RAIZ / "LICENSE", RAIZ / "index.html"]
    for arquivo in publicos:
        assert "dadosgovtocantins@" not in arquivo.read_text(encoding="utf-8").lower(), arquivo.name
