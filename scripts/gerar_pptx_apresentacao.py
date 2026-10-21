"""
Script para geração automática da apresentação em PowerPoint (.pptx)
do projeto "Painel TO em Dados" (PIBIEX / Unitins).
"""

import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


def criar_apresentacao():
    prs = Presentation()

    # Configurar tamanho 16:9 Widescreen (13.333 x 7.5 polegadas)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Cores do Design System do Projeto
    COLOR_PRIMARY = RGBColor(15, 23, 42)  # Slate 900
    COLOR_SECONDARY = RGBColor(30, 41, 59)  # Slate 800
    COLOR_ACCENT = RGBColor(14, 165, 233)  # Sky 500 (Azul destaque)
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
    COLOR_BG_CARD = RGBColor(241, 245, 249)  # Slate 100
    COLOR_WHITE = RGBColor(255, 255, 255)

    blank_layout = prs.slide_layouts[6]

    slides_data = [
        {
            "titulo": "Painel de Indicadores de Políticas Públicas",
            "subtitulo": "Trajetória, Arquitetura e Execução do Projeto — Estado do Tocantins\nProjeto de Extensão Universitária PIBIEX / TO Graduado / Unitins",
            "tipo": "capa",
        },
        {
            "titulo": "1. Visão Geral & Propósito 🎯",
            "subtitulo": "O que é o projeto e qual problema ele resolve?",
            "pontos": [
                (
                    "Consulta Unificada",
                    "Portal público de consulta que reúne dados dos 139 municípios do Tocantins no mesmo lugar.",
                ),
                (
                    "Território vs. Gestão",
                    "O painel mede o território e a eficácia das políticas públicas, sem vínculo com gestão governamental específica.",
                ),
                (
                    "Custo R$ 0 (OPEX Zero)",
                    "Construído 100% sob a franquia gratuita do Google Cloud (BigQuery, Cloud Run, Storage, Looker).",
                ),
                (
                    "Paridade Municipal",
                    "Garante que municípios pequenos (ex: Lagoa da Confusão, Araguatins) tenham o mesmo destaque que Palmas.",
                ),
            ],
        },
        {
            "titulo": "2. O Problema Diagnostico 🧩",
            "subtitulo": "Por que o projeto foi criado?",
            "pontos": [
                (
                    "Dados Pulverizados",
                    "Informações públicas estavam dispersas em mais de 15 portais (IBGE, DATASUS, SICONFI, INEP).",
                ),
                (
                    "Baixa Reutilização",
                    "Grande parte das fontes estaduais é publicada apenas em PDF ou HTML não estruturado.",
                ),
                (
                    "Compilação Manual",
                    "Cruzamento de dados fiscais e sociais exigia montagem manual de planilhas complexas.",
                ),
                (
                    "Solução Entregue",
                    "Uma camada automática de ingestão que coleta, padroniza e exibe tudo lado a lado.",
                ),
            ],
        },
        {
            "titulo": "3. Concepção & Leitura do PRD 📋",
            "subtitulo": "Regras de negócio e governança do produto",
            "pontos": [
                (
                    "Catálogo de 40 Fontes",
                    "Mapeamento metodológico de 40 fontes (federais e estaduais) divididas em 2 níveis.",
                ),
                (
                    "Catálogo em 2 Níveis",
                    "Nível 1: Fontes de Coleta | Nível 2: Indicadores Atômicos exibidos ao público (~70 cards).",
                ),
                (
                    "Honestidade Estatística",
                    "Distinção explícita entre 'Sem dado' (não declarado) e 'Dado zero' para não penalizar municípios.",
                ),
                (
                    "Identidade Independente",
                    "Projeto acadêmico neutro, sem símbolos oficiais do governo nem uso de marcas estaduais.",
                ),
            ],
        },
        {
            "titulo": "4. O Roadmap & Metodologia 🗺️",
            "subtitulo": "Planejamento estruturado em Sprints (GSD)",
            "pontos": [
                (
                    "18 Semanas de Trabalho",
                    "Organizado em 9 Sprints de 2 semanas (~22 horas/semana de dedicação técnica).",
                ),
                (
                    "25 Tarefas Principais",
                    "Escopo dividido desde a Fundação GCP até a Entrega Acadêmica e Go-Live.",
                ),
                (
                    "Arquitetura Medallion",
                    "Estrutura de dados em 3 camadas: Raw (bruto) -> STG (tratado) -> Mart (agregados).",
                ),
                (
                    "Chave Canônica IBGE",
                    "Todos os dados são unificados usando o código oficial do IBGE de 7 dígitos por município.",
                ),
            ],
        },
        {
            "titulo": "5. Mão na Massa — Quinta-feira (24/09) 🔨",
            "subtitulo": "Desenvolvimento do motor do sistema",
            "pontos": [
                (
                    "Coletores de Dados (src/coletores)",
                    "Construção dos módulos em Python para extração via API do IBGE (SIDRA) e STN (SICONFI).",
                ),
                (
                    "Modelo SQL & DDL (src/sql)",
                    "Criação dos esquemas relacionais no formato Star Schema (Fato e Dimensões).",
                ),
                (
                    "Interface Web (index.html / src/ui)",
                    "Desenvolvimento da tela de navegação responsiva com seletores para os 139 municípios.",
                ),
                (
                    "Automação (automacao_coleta.py)",
                    "Criação do script central de orquestração sequencial de coleta sem falha manual.",
                ),
            ],
        },
        {
            "titulo": "6. Primeira Execução Real — Sexta-feira (25/09) 🚀",
            "subtitulo": "Sucesso na extração automatizada de dados",
            "pontos": [
                (
                    "Extração IBGE Concluída",
                    "População residente de 100% dos 139 municípios do TO ingerida com sucesso.",
                ),
                (
                    "Extração SICONFI Concluída",
                    "Coleta de receitas correntes líquidas e indicadores de gestão fiscal dos municípios.",
                ),
                (
                    "Geração de Arquivos em data/",
                    "Criação automatizada das planilhas ibge_populacao_to.csv e siconfi_execucao_to.csv.",
                ),
                (
                    "Exportação para UI",
                    "Geração do arquivo dados_coletados_real.json para exibição imediata no painel web.",
                ),
            ],
        },
        {
            "titulo": "7. Onde os Dados Estão Hoje? 💾",
            "subtitulo": "Localização e persistência das informações",
            "pontos": [
                (
                    "Armazenamento na Máquina Local",
                    "Os dados reais coletados nos testes dos dias 24/25 estão salvos localmente em data/ e src/ui/data/.",
                ),
                (
                    "Estrutura no BigQuery (Nuvem)",
                    "As tabelas e datasets em nuvem estão prontos no projeto GCP do Painel TO em Dados.",
                ),
                (
                    "Sincronização Simples",
                    "Os arquivos locais podem ser carregados para o BigQuery a qualquer momento via script DDL ou upload direct.",
                ),
                (
                    "Segurança & Backup",
                    "Dados brutos com assinatura SHA-256 para auditoria e histórico preservado.",
                ),
            ],
        },
        {
            "titulo": "8. Inovação & Entregáveis Acadêmicos 💡",
            "subtitulo": "O legado do projeto para a extensão e pesquisa",
            "pontos": [
                (
                    "Índice de Maturidade de Dados",
                    "Mede percentualmente o nível de dados abertos reutilizáveis por órgão no TO.",
                ),
                (
                    "Metodologia Replicável",
                    "Estrutura pronta que pode ser replicada para qualquer outro estado brasileiro.",
                ),
                (
                    "Código Aberto & Relatórios",
                    "Entregáveis acadêmicos incluindo relatórios PIBIEX, artigo científico e repositório público.",
                ),
                (
                    "Transparência Cidadã",
                    "Democratização do acesso aos dados de políticas públicas sem necessidade de conhecimentos técnicos.",
                ),
            ],
        },
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Fundo do slide
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_WHITE if data.get("tipo") != "capa" else COLOR_PRIMARY
        bg.line.fill.background()

        if data.get("tipo") == "capa":
            # Slide de Capa
            tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.5))
            tf = tb.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            p1.text = data["titulo"]
            p1.font.size = Pt(40)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_ACCENT
            p1.alignment = PP_ALIGN.LEFT

            p2 = tf.add_paragraph()
            p2.text = data["subtitulo"]
            p2.font.size = Pt(20)
            p2.font.color.rgb = COLOR_WHITE
            p2.space_before = Pt(24)
            p2.alignment = PP_ALIGN.LEFT

        else:
            # Barra superior decorativa
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(0.15), Inches(0.9)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = COLOR_ACCENT
            bar.line.fill.background()

            # Título do Slide
            tb_title = slide.shapes.add_textbox(Inches(1.1), Inches(0.5), Inches(11.5), Inches(1.1))
            tf_title = tb_title.text_frame
            tf_title.word_wrap = True

            p_t = tf_title.paragraphs[0]
            p_t.text = data["titulo"]
            p_t.font.size = Pt(28)
            p_t.font.bold = True
            p_t.font.color.rgb = COLOR_PRIMARY

            p_sub = tf_title.add_paragraph()
            p_sub.text = data["subtitulo"]
            p_sub.font.size = Pt(14)
            p_sub.font.color.rgb = COLOR_TEXT_MUTED
            p_sub.space_before = Pt(4)

            # Cards de Conteúdo (2x2 Grid)
            pontos = data.get("pontos", [])
            grid_positions = [
                (Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4)),
                (Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.4)),
                (Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.4)),
                (Inches(6.8), Inches(4.5), Inches(5.6), Inches(2.4)),
            ]

            for i, (head, desc) in enumerate(pontos):
                if i < len(grid_positions):
                    left, top, width, height = grid_positions[i]

                    # Card background
                    card = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
                    )
                    card.fill.solid()
                    card.fill.fore_color.rgb = COLOR_BG_CARD
                    card.line.fill.background()

                    # Card text
                    tb_card = slide.shapes.add_textbox(
                        left + Inches(0.2),
                        top + Inches(0.2),
                        width - Inches(0.4),
                        height - Inches(0.4),
                    )
                    tf_card = tb_card.text_frame
                    tf_card.word_wrap = True

                    pc_head = tf_card.paragraphs[0]
                    pc_head.text = head
                    pc_head.font.size = Pt(18)
                    pc_head.font.bold = True
                    pc_head.font.color.rgb = COLOR_PRIMARY

                    pc_desc = tf_card.add_paragraph()
                    pc_desc.text = desc
                    pc_desc.font.size = Pt(13)
                    pc_desc.font.color.rgb = COLOR_SECONDARY
                    pc_desc.space_before = Pt(8)

    # Salvar na raiz e na pasta de artefatos
    output_filename = "apresentacao_painel_to.pptx"
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_filename
    )
    prs.save(output_path)
    print(f"✅ Apresentação gerada com sucesso em: {output_path}")
    return output_path


if __name__ == "__main__":
    criar_apresentacao()
