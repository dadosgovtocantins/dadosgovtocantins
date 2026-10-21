import { renderKPICard } from './components/card.js';

let municipios = [];
let municipioSelecionado = null;
let abaAtiva = 'municipio';
let dadosColetadosReal = null;

// Só exibe valor com coleta real. Os demais eram calculados por fórmula a partir do código IBGE
// e passam a "sem dado" (revisão de código de 2026-10-14). Ranking e variação não têm fonte real.
const semDado = (c) => ({ ...c, valor_num: null, qualidade: 'sem_dado', variacao_percentual: null, posicao_ranking: null, dt_coleta: null });
const soReal = (c) => ({ ...c, variacao_percentual: null, posicao_ranking: null });

function populacaoEstadoReal() {
    const valores = (dadosColetadosReal?.ibge_populacao || []).map(r => Number(r.populacao_estimada)).filter(Number.isFinite);
    return valores.length === 139 ? valores.reduce((s, v) => s + v, 0) : null;
}

// Receita realizada exceto intraorçamentárias, líquida de deduções (SICONFI DCA Anexo I-C), em R$ mil.
function receitaEstadoReal() {
    const linhas = (dadosColetadosReal?.siconfi_execucao || []).filter(r => r.cod_conta === 'ReceitasExcetoIntraOrcamentarias');
    const bruta = linhas.find(r => r.coluna === 'Receitas Brutas Realizadas');
    if (!bruta) return null;
    const deducoes = linhas.filter(r => /Dedu[çc][õo]es/.test(r.coluna)).reduce((s, r) => s + Number(r.valor), 0);
    return Math.round((Number(bruta.valor) - deducoes) / 1000);
}

// Inicializa a aplicação
async function init() {
    try {
        const timestamp = Date.now();
        const response = await fetch(`./src/ui/data/municipios_to.json?t=${timestamp}`);
        municipios = await response.json();

        try {
            const respReal = await fetch(`./src/ui/data/dados_coletados_real.json?t=${timestamp}`);
            dadosColetadosReal = await respReal.json();
            console.log("✅ Dados reais da automação carregados:", dadosColetadosReal);
        } catch (e) {
            console.warn("Utilizando dataset padrão.");
        }
        
        preencherSelectMunicipios();
        
        // Seleciona Palmas por padrão (ou o 1º da lista)
        const padrao = municipios.find(m => m.nome === 'Palmas') || municipios[0];
        selecionarMunicipio(padrao.id_municipio);
        
        configurarEventos();
    } catch (err) {
        console.error("Erro ao carregar lista de municípios:", err);
    }
}

function preencherSelectMunicipios() {
    const select = document.getElementById('select-municipio');
    if (!select) return;

    select.innerHTML = municipios.map(m => `
        <option value="${m.id_municipio}">${m.nome} (Código IBGE: ${m.id_municipio})</option>
    `).join('');
}

function configurarEventos() {
    const select = document.getElementById('select-municipio');
    if (select) {
        select.addEventListener('change', (e) => {
            selecionarMunicipio(e.target.value);
        });
    }

    const selectOrgao = document.getElementById('select-orgao');
    if (selectOrgao) {
        selectOrgao.addEventListener('change', (e) => {
            renderizarTelaOrgao(e.target.value);
        });
    }

    const btnMunicipio = document.getElementById('tab-municipio');
    const btnEstado = document.getElementById('tab-estado');
    const btnOrgao = document.getElementById('tab-orgao');

    if (btnMunicipio && btnEstado && btnOrgao) {
        btnMunicipio.addEventListener('click', () => alternarAba('municipio'));
        btnEstado.addEventListener('click', () => alternarAba('estado'));
        btnOrgao.addEventListener('click', () => alternarAba('orgao'));
    }

    const btnSobre = document.getElementById('btn-sobre');
    const btnMetodologia = document.getElementById('btn-metodologia');
    const btnExport = document.getElementById('btn-export-csv');
    const modalClose = document.getElementById('modal-close');

    if (btnSobre) btnSobre.addEventListener('click', abrirModalSobre);
    if (btnMetodologia) btnMetodologia.addEventListener('click', abrirModalMetodologia);
    if (btnExport) btnExport.addEventListener('click', exportarCSV);
    if (modalClose) modalClose.addEventListener('click', fecharModal);
}

function abrirModalSobre() {
    const body = document.getElementById('modal-body');
    if (!body) return;
    body.innerHTML = `
        <h2 style="margin-bottom: 12px;">Sobre o Painel TO em Dados</h2>
        <p style="margin-bottom: 8px;"><strong>Vínculo:</strong> Projeto de Extensão Universitária PIBIEX / Unitins.</p>
        <p style="margin-bottom: 8px;"><strong>Objetivo:</strong> Consolidação e monitoramento de indicadores de políticas públicas dos 139 municípios do Estado do Tocantins com 100% de transparência e auditoria de fontes.</p>
        <p style="margin-top: 12px; font-size: 12px; color: var(--color-text-muted);">
            <strong>Aviso Legal (RR-05):</strong> Este painel é uma ferramenta acadêmica independente. Não possui vínculo e não representa o Governo do Estado do Tocantins.
        </p>
    `;
    document.getElementById('modal-info').style.display = 'flex';
}

function abrirModalMetodologia() {
    const body = document.getElementById('modal-body');
    if (!body) return;
    body.innerHTML = `
        <h2 style="margin-bottom: 12px;">Metodologia e Qualidade de Dados</h2>
        <p style="margin-bottom: 8px;"><strong>Regra Fundamental (RF-55):</strong> Distinção estrita entre ausência de dado (omissão declaratória <code>sem_dado</code>) e dado zero.</p>
        <ul style="margin-left: 20px; font-size: 13px; line-height: 1.6;">
            <li><strong>ok:</strong> Dado oficial coletado e validado.</li>
            <li><strong>estimado:</strong> Estimativa metodológica IBGE.</li>
            <li><strong>sem_dado:</strong> Município omisso na publicação oficial — nunca exibido como zero.</li>
            <li><strong>gerado_por_ia:</strong> Dado estruturado via IA Gemini (sempre auditado).</li>
        </ul>
    `;
    document.getElementById('modal-info').style.display = 'flex';
}

function fecharModal() {
    const modal = document.getElementById('modal-info');
    if (modal) modal.style.display = 'none';
}

function exportarCSV() {
    const cards = document.querySelectorAll('.kpi-card:not(.loading)');
    if (cards.length === 0) return alert('Nenhum indicador disponível para exportação.');

    let csv = 'Indicador,Valor,Unidade,Qualidade,Esfera,Fonte\n';
    cards.forEach(c => {
        const title = c.querySelector('.kpi-card-title')?.textContent || '';
        const val = c.querySelector('.kpi-value')?.textContent || '';
        const unit = c.querySelector('.kpi-unit')?.textContent || '';
        const qual = c.getAttribute('data-qualidade') || 'ok';
        const esf = c.querySelector('.badge-esfera')?.textContent || '';
        const fonte = c.querySelector('.kpi-fonte-link')?.textContent || '';
        csv += `"${title}","${val}","${unit}","${qual}","${esf}","${fonte}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `painel_to_indicadores_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function alternarAba(aba) {
    abaAtiva = aba;
    const btnMunicipio = document.getElementById('tab-municipio');
    const btnEstado = document.getElementById('tab-estado');
    const btnOrgao = document.getElementById('tab-orgao');
    const controlBar = document.querySelector('.control-bar');
    const municipioContainer = document.getElementById('municipio-selector-container');
    const orgaoContainer = document.getElementById('orgao-selector-container');
    const title = document.querySelector('.section-title');

    [btnMunicipio, btnEstado, btnOrgao].forEach(b => b?.classList.remove('active'));

    if (aba === 'municipio') {
        btnMunicipio?.classList.add('active');
        if (controlBar) controlBar.style.display = 'flex';
        if (municipioContainer) municipioContainer.style.display = 'flex';
        if (orgaoContainer) orgaoContainer.style.display = 'none';
        if (title) title.textContent = 'Indicadores de Políticas Públicas e Desenvolvimento Municipal';
        if (municipioSelecionado) renderizarCardsMunicipio(municipioSelecionado.id_municipio);
    } else if (aba === 'estado') {
        btnEstado?.classList.add('active');
        if (controlBar) controlBar.style.display = 'flex';
        if (municipioContainer) municipioContainer.style.display = 'none';
        if (orgaoContainer) orgaoContainer.style.display = 'none';
        if (title) title.textContent = 'Indicadores Agregados do Estado do Tocantins';
        renderizarCardsEstado();
    } else if (aba === 'orgao') {
        btnOrgao?.classList.add('active');
        if (controlBar) controlBar.style.display = 'flex';
        if (municipioContainer) municipioContainer.style.display = 'none';
        if (orgaoContainer) orgaoContainer.style.display = 'flex';
        if (title) title.textContent = 'Diagnóstico de Maturidade e Catálogo por Órgão';
        const selectOrgao = document.getElementById('select-orgao');
        renderizarTelaOrgao(selectOrgao ? selectOrgao.value : 'IBGE');
    }
}

function selecionarMunicipio(id_municipio) {
    municipioSelecionado = municipios.find(m => m.id_municipio === id_municipio);
    if (!municipioSelecionado) return;

    const select = document.getElementById('select-municipio');
    if (select && select.value !== id_municipio) {
        select.value = id_municipio;
    }

    const info = document.getElementById('municipio-info-detalhe');
    if (info) {
        info.textContent = `Exibindo indicadores municipais de ${municipioSelecionado.nome} (Código IBGE: ${id_municipio})`;
    }

    renderizarCardsMunicipio(id_municipio);
}

function renderizarCardsMunicipio(id_municipio) {
    const grid = document.getElementById('cards-grid');
    if (!grid) return;

    const seed = parseInt(id_municipio.replace('17', ''), 10) || 1;

    // Busca valor populacional real coletado via automação Python da API SIDRA do IBGE
    let valorPopReal = null;
    let dtColetaPop = null;
    if (dadosColetadosReal && dadosColetadosReal.ibge_populacao) {
        const itemReal = dadosColetadosReal.ibge_populacao.find(r => String(r.id_municipio) === String(id_municipio));
        if (itemReal && itemReal.populacao_estimada) {
            valorPopReal = itemReal.populacao_estimada;
            if (itemReal.dt_coleta) dtColetaPop = new Date(itemReal.dt_coleta).toLocaleDateString('pt-BR');
        }
    }

    // Gerador de cards cobrindo os indicadores municipais catalogados na planilha
    const cardsData = [
        {
            id_indicador: 'populacao_residente',
            nome_indicador: 'População Estimada por Município',
            valor_num: valorPopReal,
            unidade: 'hab',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-01',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: dtColetaPop,
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 1.4
        },
        {
            id_indicador: 'pib_municipal',
            nome_indicador: 'PIB Municipal',
            valor_num: 50000 + seed * 3200,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-02',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 3.2
        },
        {
            id_indicador: 'area_territorial',
            nome_indicador: 'Malha Territorial dos Municípios',
            valor_num: 1500.0 + seed * 20.0,
            unidade: 'km²',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-04',
            fonte_url: 'https://www.ibge.gov.br/geociencias',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 0.0
        },
        {
            id_indicador: 'producao_agricola',
            nome_indicador: 'Produção Agrícola Municipal (PAM)',
            valor_num: 8000.0 + seed * 500.0,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-05',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 5.8
        },
        {
            id_indicador: 'ideb_anos_iniciais',
            nome_indicador: 'Ideb 2025 — Rede Municipal',
            valor_num: Number((4.5 + (seed % 25) * 0.1).toFixed(1)),
            unidade: 'nota',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-EDU-01',
            fonte_url: 'https://www.gov.br/inep',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 4.5
        },
        {
            id_indicador: 'saeb_proficiencia',
            nome_indicador: 'Saeb 2025 — Proficiência L.P. e Mat.',
            valor_num: Number((210.0 + (seed % 30) * 1.5).toFixed(1)),
            unidade: 'pontos',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-EDU-03',
            fonte_url: 'https://www.gov.br/inep',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 2.3
        },
        {
            id_indicador: 'censo_escolar_matriculas',
            nome_indicador: 'Censo Escolar — Matrículas e Infraestrutura',
            valor_num: 450 + seed * 40,
            unidade: 'matrículas',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-EDU-04',
            fonte_url: 'https://www.gov.br/inep',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 1.8
        },
        {
            id_indicador: 'indicadores_educacionais_icg',
            nome_indicador: 'Indicadores Educacionais — Rendimento e Distorção',
            valor_num: Number((12.5 + (seed % 15) * 0.4).toFixed(1)),
            unidade: '% distorção',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-EDU-05',
            fonte_url: 'https://www.gov.br/inep',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: -0.8
        },
        {
            id_indicador: 'repasses_fnde',
            nome_indicador: 'Repasses FNDE Educação (PNAE/PNATE)',
            valor_num: 150000.0 + seed * 4500.0,
            unidade: 'BRL',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-EDU-02',
            fonte_url: 'https://www.fnde.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 8.3
        },
        {
            id_indicador: 'saldo_emprego_caged',
            nome_indicador: 'Novo CAGED — Saldo de Empregos Formais',
            valor_num: (seed * 37) % 500 - 100,
            unidade: 'postos',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TRAB-01',
            fonte_url: 'https://pdet.mte.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: -1.2
        },
        {
            id_indicador: 'exportacoes_comex',
            nome_indicador: 'Exportações Municipais (Comex Stat)',
            valor_num: (seed * 12345) % 1000000,
            unidade: 'USD',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-ECO-01',
            fonte_url: 'http://comexstat.mdic.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 12.4
        },
        {
            id_indicador: 'empresas_ativas',
            nome_indicador: 'Mapa de Empresas — Abertura e Fechamento',
            valor_num: 300 + seed * 25,
            unidade: 'empresas',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-ECO-02',
            fonte_url: 'https://www.gov.br/empresas-e-negocios',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 6.7
        },
        {
            id_indicador: 'producao_ambulatorial_datasus',
            nome_indicador: 'Produção Ambulatorial e Rede (SIA/SIH/CNES)',
            valor_num: 1200 + seed * 85,
            unidade: 'procedimentos',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-SAU-01',
            fonte_url: 'https://datasus.saude.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 2.7
        },
        {
            id_indicador: 'receitas_despesas_municipios',
            nome_indicador: 'Receitas, Despesas e Licitações dos Municípios',
            valor_num: 185000.0 + seed * 3200.0,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-02',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 4.1
        },
        {
            id_indicador: 'indicadores_lrf_municipal',
            nome_indicador: 'Indicadores da LRF (Pessoal e Dívida)',
            valor_num: Number((42.0 + (seed % 15) * 0.8).toFixed(1)),
            unidade: '% RCL',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-03',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 0.5
        },
        {
            id_indicador: 'cotacoes_ceasa',
            nome_indicador: 'Cotações Agropecuárias da CEASA',
            valor_num: Number((85.5 + (seed % 10) * 1.2).toFixed(2)),
            unidade: 'R$/saco',
            qualidade: 'ok',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-AGR-01',
            fonte_url: 'https://ceasa.to.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: (seed % 139) + 1,
            variacao_percentual: 1.5
        },
        {
            id_indicador: 'execucao_orcamentaria_local',
            nome_indicador: 'Execução Orçamentária Municipal (Transparência)',
            valor_num: null,
            unidade: 'BRL',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-EST-01',
            fonte_url: 'https://transparencia.to.gov.br',
            dt_coleta: '2026-09-24',
            posicao_ranking: null,
            variacao_percentual: null
        }
    ];

    grid.innerHTML = cardsData
        .map(c => renderKPICard(c.id_indicador === 'populacao_residente' && c.valor_num !== null ? soReal(c) : semDado(c)))
        .join('');
}

function renderizarCardsEstado() {
    const grid = document.getElementById('cards-grid');
    if (!grid) return;

    const estadoCards = [
        {
            id_indicador: 'pib_estadual',
            nome_indicador: 'PIB Estadual (Contas Regionais)',
            valor_num: 43500000.0,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-03',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: 4.8
        },
        {
            id_indicador: 'taxa_desocupacao_pnadc',
            nome_indicador: 'Mercado de Trabalho — PNAD Contínua',
            valor_num: 6.8,
            unidade: '% desocupação',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-07',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: -0.5
        },
        {
            id_indicador: 'populacao_total_to',
            nome_indicador: 'População Total do Tocantins',
            valor_num: 1607363,
            unidade: 'hab',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-01',
            fonte_url: 'https://sidra.ibge.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: 1.2
        },
        {
            id_indicador: 'camadas_geoespaciais',
            nome_indicador: 'Camadas Geoespaciais do Estado',
            valor_num: 139,
            unidade: 'camadas GIS',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-04',
            fonte_url: 'https://www.ibge.gov.br/geociencias',
            dt_coleta: '2026-09-24',
            variacao_percentual: 0.0
        },
        {
            id_indicador: 'tocantins_em_numeros',
            nome_indicador: 'Tocantins em Números / Estatísticas Estaduais',
            valor_num: 2026,
            unidade: 'edição',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-TER-01',
            fonte_url: 'https://seplan.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'receitas_publicas_estaduais',
            nome_indicador: 'Receitas Públicas Estaduais (SICONFI)',
            valor_num: 14200000.0,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-02',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: 5.4
        },
        {
            id_indicador: 'despesas_publicas_estaduais',
            nome_indicador: 'Despesas Públicas Estaduais (SICONFI)',
            valor_num: 13800000.0,
            unidade: 'R$ mil',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-02',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: 4.9
        },
        {
            id_indicador: 'execucao_orcamentaria_estadual',
            nome_indicador: 'Execução Orçamentária Estadual',
            valor_num: 97.1,
            unidade: '% executado',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-02',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: 1.1
        },
        {
            id_indicador: 'indicadores_lrf_estadual',
            nome_indicador: 'Indicadores da LRF Estadual (Dívida e Pessoal)',
            valor_num: 46.2,
            unidade: '% RCL',
            qualidade: 'ok',
            esfera_fonte: 'Federal',
            id_fonte: 'TO-REC-03',
            fonte_url: 'https://siconfi.tesouro.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: -0.4
        },
        {
            id_indicador: 'ocorrencias_seguranca',
            nome_indicador: 'Ocorrências de Segurança Pública',
            valor_num: null,
            unidade: 'casos',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-SEG-01',
            fonte_url: 'https://ssp.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'fluxo_oferta_turistica',
            nome_indicador: 'Fluxo e Oferta Turística',
            valor_num: null,
            unidade: 'visitantes',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-TUR-01',
            fonte_url: 'https://adetuc.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'rodovias_obras_estaduais',
            nome_indicador: 'Rodovias e Obras Estaduais',
            valor_num: null,
            unidade: 'km obras',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-OBR-01',
            fonte_url: 'https://ageto.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'ouvidoria_controle_interno',
            nome_indicador: 'Ouvidoria e Controle Interno',
            valor_num: null,
            unidade: 'manifestações',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-CGE-01',
            fonte_url: 'https://cge.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'servicos_publicos_digitais',
            nome_indicador: 'Monitoramento de Serviços Públicos Digitais',
            valor_num: null,
            unidade: 'serviços',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-ATI-01',
            fonte_url: 'https://ati.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'chamados_ti_producao_documental',
            nome_indicador: 'Monitoramento de Chamados e TI Estadual',
            valor_num: null,
            unidade: 'chamados',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-ATI-02',
            fonte_url: 'https://ati.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        },
        {
            id_indicador: 'atos_oficiais_publicados',
            nome_indicador: 'Atos Oficiais Publicados (Diário Oficial)',
            valor_num: null,
            unidade: 'edições',
            qualidade: 'sem_dado',
            esfera_fonte: 'Estadual',
            id_fonte: 'TO-EST-04',
            fonte_url: 'https://diariooficial.to.gov.br',
            dt_coleta: '2026-09-24',
            variacao_percentual: null
        }
    ];

    const reais = { populacao_total_to: populacaoEstadoReal(), receitas_publicas_estaduais: receitaEstadoReal() };
    grid.innerHTML = estadoCards
        .map(c => renderKPICard(reais[c.id_indicador] != null ? soReal({ ...c, valor_num: reais[c.id_indicador], dt_coleta: null }) : semDado(c)))
        .join('');
}

function renderizarTelaOrgao(orgaoNome = 'IBGE') {
    const grid = document.getElementById('cards-grid');
    if (!grid) return;

    // Mapa de Maturidade e Indicadores por Órgão Catalogado (11 Órgãos — Mapeamento Completo dos 30 Indicadores)
    const mapaOrgaos = {
        'IBGE': {
            nomeCompleto: 'IBGE — Instituto Brasileiro de Geografia e Estatística',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '7 fontes abertas / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Proporção de fontes reutilizáveis em formato aberto (API SIDRA / JSON / CSV).',
            cards: [
                { id_indicador: 'populacao_residente', nome_indicador: 'População Estimada por Município', valor_num: 1607363, unidade: 'hab', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-01', fonte_url: 'https://sidra.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 1.4 },
                { id_indicador: 'pib_municipal', nome_indicador: 'PIB Municipal', valor_num: 50000.0, unidade: 'R$ mil', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-02', fonte_url: 'https://sidra.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 3.2 },
                { id_indicador: 'pib_estadual', nome_indicador: 'PIB Estadual (Contas Regionais)', valor_num: 43500000.0, unidade: 'R$ mil', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-03', fonte_url: 'https://sidra.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 4.8 },
                { id_indicador: 'area_territorial', nome_indicador: 'Malha Territorial dos Municípios', valor_num: 1500.0, unidade: 'km²', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-04', fonte_url: 'https://www.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 0.0 },
                { id_indicador: 'producao_agricola', nome_indicador: 'Produção Agrícola Municipal (PAM)', valor_num: 8500.0, unidade: 'R$ mil', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-05', fonte_url: 'https://sidra.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 5.8 },
                { id_indicador: 'pnad_continua', nome_indicador: 'Mercado de Trabalho — PNAD Contínua', valor_num: 6.8, unidade: '% desocupação', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-07', fonte_url: 'https://sidra.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: -0.5 },
                { id_indicador: 'camadas_geoespaciais', nome_indicador: 'Camadas Geoespaciais do Estado', valor_num: 139, unidade: 'camadas GIS', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TER-04', fonte_url: 'https://www.ibge.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 0.0 }
            ]
        },
        'INEP': {
            nomeCompleto: 'INEP — Instituto Nacional de Estudos e Pesquisas Educacionais',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '4 fontes abertas / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Indicadores educacionais oficiais em Microdados e APIs do Ministério da Educação.',
            cards: [
                { id_indicador: 'ideb_2025', nome_indicador: 'Ideb 2025 — Rede Estadual e Municipal', valor_num: 5.8, unidade: 'nota', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-EDU-01', fonte_url: 'https://www.gov.br/inep', dt_coleta: '2026-09-24', variacao_percentual: 4.5 },
                { id_indicador: 'saeb_2025', nome_indicador: 'Saeb 2025 — Proficiência L.P. e Matemática', valor_num: 215.4, unidade: 'pontos', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-EDU-03', fonte_url: 'https://www.gov.br/inep', dt_coleta: '2026-09-24', variacao_percentual: 2.3 },
                { id_indicador: 'censo_escolar', nome_indicador: 'Censo Escolar — Matrículas e Infraestrutura', valor_num: 312000, unidade: 'matrículas', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-EDU-04', fonte_url: 'https://www.gov.br/inep', dt_coleta: '2026-09-24', variacao_percentual: 1.8 },
                { id_indicador: 'indicadores_educacionais_rendimento', nome_indicador: 'Indicadores Educacionais — Rendimento e ICG', valor_num: 88.5, unidade: '% aprovação', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-EDU-05', fonte_url: 'https://www.gov.br/inep', dt_coleta: '2026-09-24', variacao_percentual: 1.2 }
            ]
        },
        'FNDE': {
            nomeCompleto: 'FNDE — Fundo Nacional de Desenvolvimento da Educação',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '1 fonte aberta / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Repasses financeiros da educação (PNAE, PNATE, FUNDEB) em dados abertos.',
            cards: [
                { id_indicador: 'repasses_fnde', nome_indicador: 'Repasses FNDE Educação (PNAE/PNATE/FUNDEB)', valor_num: 150000.0, unidade: 'BRL', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-EDU-02', fonte_url: 'https://www.fnde.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 8.3 }
            ]
        },
        'MTE': {
            nomeCompleto: 'MTE — Ministério do Trabalho e Emprego',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '1 fonte aberta / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Dados mensais de movimentação do emprego formal via Novo CAGED.',
            cards: [
                { id_indicador: 'novo_caged', nome_indicador: 'Novo CAGED — Saldo de Empregos Formais', valor_num: 250, unidade: 'postos', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-TRAB-01', fonte_url: 'https://pdet.mte.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 2.5 }
            ]
        },
        'MDIC': {
            nomeCompleto: 'MDIC — Ministério do Desenvolvimento, Indústria e Comércio',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '1 fonte aberta / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Estatísticas de comércio exterior municipal e balança comercial via Comex Stat.',
            cards: [
                { id_indicador: 'exportacoes_comex', nome_indicador: 'Exportações Municipais (Comex Stat)', valor_num: 450000.0, unidade: 'USD', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-ECO-01', fonte_url: 'http://comexstat.mdic.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 12.4 }
            ]
        },
        'ME': {
            nomeCompleto: 'ME — Ministério da Economia / Mapa de Empresas',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '1 fonte aberta / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Painel e dados abertos de empresas ativas e tempo de abertura por município.',
            cards: [
                { id_indicador: 'mapa_empresas', nome_indicador: 'Mapa de Empresas — Abertura e Fechamento', valor_num: 1250, unidade: 'empresas', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-ECO-02', fonte_url: 'https://www.gov.br/empresas-e-negocios', dt_coleta: '2026-09-24', variacao_percentual: 6.7 }
            ]
        },
        'DATASUS': {
            nomeCompleto: 'DATASUS — Departamento de Informática do SUS',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '3 fontes abertas / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'Bases de dados da saúde pública (CNES, PNI, SIM/SINASC, SIA/SIH) via PySUS e FTP oficial.',
            cards: [
                { id_indicador: 'producao_ambulatorial_sia_sih', nome_indicador: 'Produção Ambulatorial e Internações (SIA/SIH/CNES)', valor_num: 45, unidade: 'leitos', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-SAU-01', fonte_url: 'https://datasus.saude.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 1.1 },
                { id_indicador: 'cobertura_vacinal', nome_indicador: 'Cobertura Vacinal (PNI)', valor_num: 85.4, unidade: '%', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-SAU-02', fonte_url: 'https://datasus.saude.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 3.2 },
                { id_indicador: 'mortalidade_infantil', nome_indicador: 'Mortalidade Infantil (SIM)', valor_num: 11.2, unidade: 'óbitos/mil nascidos', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-SAU-03', fonte_url: 'https://datasus.saude.gov.br', dt_coleta: '2026-09-24', variacao_percentual: -1.5 }
            ]
        },
        'STN': {
            nomeCompleto: 'STN — Secretaria do Tesouro Nacional / SICONFI',
            nivel: 'Avançado',
            percentual: '100%',
            fontesTexto: '4 fontes abertas / 0 apenas-link (Grau A)',
            classeBadge: 'avançado',
            bgColor: '#FFFFFF',
            borderColor: 'var(--color-border)',
            textColor: 'var(--color-text-primary)',
            desc: 'API oficial de informações contábeis e fiscais (SICONFI) e avaliação CAPAG.',
            cards: [
                { id_indicador: 'receitas_despesas_municipios', nome_indicador: 'Receitas, Despesas e Licitações dos Municípios', valor_num: 250000.0, unidade: 'R$ mil', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-REC-02', fonte_url: 'https://siconfi.tesouro.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 5.4 },
                { id_indicador: 'indicadores_lrf', nome_indicador: 'Indicadores da LRF (Pessoal e Dívida)', valor_num: 'Regular', unidade: 'status', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-REC-02', fonte_url: 'https://siconfi.tesouro.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null },
                { id_indicador: 'execucao_orcamentaria_stn', nome_indicador: 'Execução Orçamentária (DCA/RREO)', valor_num: 14200000.0, unidade: 'R$ mil', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-REC-02', fonte_url: 'https://siconfi.tesouro.gov.br', dt_coleta: '2026-09-24', variacao_percentual: 4.8 },
                { id_indicador: 'capag_capacidade_pagamento', nome_indicador: 'Capacidade de Pagamento (CAPAG STN)', valor_num: 'Conceito B', unidade: 'conceito', qualidade: 'ok', esfera_fonte: 'Federal', id_fonte: 'TO-REC-03', fonte_url: 'https://www.tesouro.fazenda.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null }
            ]
        },
        'SEFAZ-TO': {
            nomeCompleto: 'SEFAZ-TO — Secretaria da Fazenda do Estado do Tocantins',
            nivel: 'Inexistente',
            percentual: '0%',
            fontesTexto: '0 fontes abertas / 3 apenas-link (Grau D — Gate 1)',
            classeBadge: 'inexistente',
            bgColor: '#FEF3C7',
            borderColor: '#FDE68A',
            textColor: '#92400E',
            desc: 'Portal em Vaadin 8.9.2 sem API REST/JSON pública. Cobertura fiscal do estado assegurada via SICONFI/STN.',
            cards: [
                { id_indicador: 'receitas_publicas_estaduais', nome_indicador: 'Receitas Públicas Estaduais', valor_num: null, unidade: 'BRL', qualidade: 'sem_dado', esfera_fonte: 'Estadual', id_fonte: 'TO-EST-01', fonte_url: 'https://transparencia.to.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null },
                { id_indicador: 'despesas_publicas_estaduais', nome_indicador: 'Despesas Públicas Estaduais', valor_num: null, unidade: 'BRL', qualidade: 'sem_dado', esfera_fonte: 'Estadual', id_fonte: 'TO-EST-01', fonte_url: 'https://transparencia.to.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null },
                { id_indicador: 'atos_oficiais_publicados', nome_indicador: 'Atos Oficiais Publicados (Diário Oficial)', valor_num: null, unidade: 'edições', qualidade: 'sem_dado', esfera_fonte: 'Estadual', id_fonte: 'TO-EST-04', fonte_url: 'https://diariooficial.to.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null }
            ]
        },
        'SES-TO': {
            nomeCompleto: 'SES-TO — Secretaria de Estado da Saúde do Tocantins',
            nivel: 'Inexistente',
            percentual: '0%',
            fontesTexto: '0 fontes abertas / 1 apenas-link (Grau D)',
            classeBadge: 'inexistente',
            bgColor: '#FEF3C7',
            borderColor: '#FDE68A',
            textColor: '#92400E',
            desc: 'Publicações exclusivamente em boletins HTML/PDF sem API pública. Cobertura da saúde assegurada via DATASUS.',
            cards: [
                { id_indicador: 'boletim_saude_estadual', nome_indicador: 'Boletim Epidemiológico e Saúde Estadual', valor_num: null, unidade: 'unid', qualidade: 'sem_dado', esfera_fonte: 'Estadual', id_fonte: 'TO-EST-02', fonte_url: 'https://saude.to.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null }
            ]
        },
        'SEDUC-TO': {
            nomeCompleto: 'SEDUC-TO — Secretaria da Educação do Estado do Tocantins',
            nivel: 'Inexistente',
            percentual: '0%',
            fontesTexto: '0 fontes abertas / 1 apenas-link (Grau D)',
            classeBadge: 'inexistente',
            bgColor: '#FEF3C7',
            borderColor: '#FDE68A',
            textColor: '#92400E',
            desc: 'Portal de relatórios em PDF sem API REST aberta. Cobertura educacional mantida via INEP e FNDE.',
            cards: [
                { id_indicador: 'divulgacoes_programas_educacionais', nome_indicador: 'Divulgações e Programas Educacionais do Estado', valor_num: null, unidade: 'unid', qualidade: 'sem_dado', esfera_fonte: 'Estadual', id_fonte: 'TO-EST-03', fonte_url: 'https://seduc.to.gov.br', dt_coleta: '2026-09-24', variacao_percentual: null }
            ]
        },
        'TCE-TO': {
            nomeCompleto: 'TCE-TO — Tribunal de Contas do Estado do Tocantins',
            nivel: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'Intermediário (Web Scraper)' : 'Inexistente',
            percentual: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '50%' : '0%',
            fontesTexto: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '1 fonte raspada via Web Scraper Opção 2 / 1 apenas-link' : '0 fontes abertas / 2 apenas-link (Grau D — Gate 1)',
            classeBadge: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'intermediário' : 'inexistente',
            bgColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#EFF6FF' : '#FEF3C7',
            borderColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#BFDBFE' : '#FDE68A',
            textColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#1E40AF' : '#92400E',
            desc: 'Raspagem automatizada em Python (Opção 2) no Portal e Boletim do TCE-TO (tceto.tc.br) capturando Pautas de Julgamento e Alertas da LRF.',
            cards: [
                { id_indicador: 'prestacao_contas_tce', nome_indicador: 'Prestação de Contas Municipais (TCE-TO)', valor_num: 139, unidade: 'municípios auditados', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-TCE-01', fonte_url: 'https://www.tceto.tc.br/pautas-das-sessoes/', dt_coleta: '2026-09-24', variacao_percentual: 2.1 },
                { id_indicador: 'alertas_lrf_tce', nome_indicador: 'Alertas LRF e Controle de Contas (TCE-TO)', valor_num: 139, unidade: 'alertas monitorados', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-TCE-02', fonte_url: 'https://app.tceto.tc.br/boletim/publico/app/index.php', dt_coleta: '2026-09-24', variacao_percentual: 0.0 }
            ]
        },
        'SEAGRO-TO': {
            nomeCompleto: 'SEAGRO-TO — Sec. da Agricultura, Pecuária e Aquicultura / Lab63',
            nivel: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'Intermediário (Web Scraper)' : 'Inexistente',
            percentual: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '50%' : '0%',
            fontesTexto: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '1 fonte raspada via Web Scraper Opção 2 / 1 apenas-link' : '0 fontes abertas / 2 apenas-link (Grau D — Gate 1)',
            classeBadge: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'intermediário' : 'inexistente',
            bgColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#EFF6FF' : '#FEF3C7',
            borderColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#BFDBFE' : '#FDE68A',
            textColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#1E40AF' : '#92400E',
            desc: 'Raspagem automatizada em Python (Opção 2) no Portal SEAGRO/Lab63 (seagro.to.gov.br) capturando Cotações da CEASA e Boletins Agrícolas.',
            cards: [
                { id_indicador: 'painel_agropecuario_lab63', nome_indicador: 'Painel de Dados Agropecuários (SEAGRO / Lab63)', valor_num: 12, unidade: 'boletins safra', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-AGR-02', fonte_url: 'https://seagro.to.gov.br/', dt_coleta: '2026-09-24', variacao_percentual: 5.0 },
                { id_indicador: 'cotacoes_agronegocio_seagro', nome_indicador: 'Cotações do Agronegócio Tocantinense', valor_num: 85.5, unidade: 'R$/saco (CEASA)', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-AGR-03', fonte_url: 'https://seagro.to.gov.br/', dt_coleta: '2026-09-24', variacao_percentual: 1.5 }
            ]
        },
        'CGE-TO': {
            nomeCompleto: 'CGE-TO — Controladoria-Geral do Estado / SIAFE-TO',
            nivel: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'Intermediário (Web Scraper)' : 'Inexistente',
            percentual: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '50%' : '0%',
            fontesTexto: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '1 fonte raspada via Web Scraper Opção 2 / 1 apenas-link' : '0 fontes abertas / 2 apenas-link (Grau D — Gate 1)',
            classeBadge: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? 'intermediário' : 'inexistente',
            bgColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#EFF6FF' : '#FEF3C7',
            borderColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#BFDBFE' : '#FDE68A',
            textColor: (dadosColetadosReal && dadosColetadosReal.scraped_estaduais) ? '#1E40AF' : '#92400E',
            desc: 'Raspagem automatizada em Python (Opção 2) no Portal da Transparência SIAFE (transparencia.to.gov.br) capturando execução orçamentária e relatórios CGE.',
            cards: [
                { id_indicador: 'execucao_siafe_cge', nome_indicador: 'Execução Orçamentária e Financeira SIAFE (CGE-TO)', valor_num: 14200000.0, unidade: 'R$ mil executado', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-CGE-02', fonte_url: 'https://transparencia.to.gov.br/', dt_coleta: '2026-09-24', variacao_percentual: 4.8 },
                { id_indicador: 'relatorios_gestao_cge', nome_indicador: 'Relatórios de Gestão Fiscal e Ouvidoria (CGE-TO)', valor_num: 580, unidade: 'relatórios ouvidos', qualidade: 'ok', esfera_fonte: 'Estadual', id_fonte: 'TO-CGE-03', fonte_url: 'https://cge.to.gov.br/', dt_coleta: '2026-09-24', variacao_percentual: 3.4 }
            ]
        }
    };

    const info = mapaOrgaos[orgaoNome] || mapaOrgaos['IBGE'];

    grid.innerHTML = `
        <div style="grid-column: 1 / -1;">
            <!-- Bloco 1: Diagnóstico de Maturidade de Dados Abertos do Órgão -->
            <div class="maturidade-card" style="background-color: ${info.bgColor}; border-color: ${info.borderColor};">
                <div>
                    <h3 style="font-size: 18px; margin-bottom: 4px; color: ${info.textColor};">
                        Índice de Maturidade de Dados Abertos — ${info.nomeCompleto}
                    </h3>
                    <p style="font-size: 13px; color: var(--color-text-secondary);">
                        ${info.desc}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span class="maturidade-nivel ${info.classeBadge}">Nível ${info.nivel} (${info.percentual} Reuso)</span>
                    <p style="font-size: 12px; color: var(--color-text-muted); margin-top: 4px;">${info.fontesTexto}</p>
                </div>
            </div>

            <h3 style="font-size: 16px; margin: 24px 0 12px 0;">Indicadores Fornecidos por ${orgaoNome}</h3>
        </div>
        ${info.cards.map(c => renderKPICard(semDado(c))).join('')}
    `;
}

document.addEventListener('DOMContentLoaded', init);

