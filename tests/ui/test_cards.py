"""
Testes do Design System de Cards (Task 12).
"""

from pathlib import Path


def test_arquivos_css_e_js_existem():
    ui_path = Path(__file__).parents[2] / "src" / "ui"
    assert (ui_path / "css" / "tokens.css").exists()
    assert (ui_path / "css" / "cards.css").exists()
    assert (ui_path / "components" / "card.js").exists()


def test_card_js_trata_sem_dado_sem_zerar():
    card_js = (Path(__file__).parents[2] / "src" / "ui" / "components" / "card.js").read_text(
        "utf-8"
    )
    assert "Sem dado publicado" in card_js
    assert "isSemDado" in card_js
    assert "loading" in card_js
