/**
 * Componente Renderizador de Card de Indicador (Task 12)
 * Suporta os 7 estados: ok, estimado, defasado, suspeito, sem_dado, falho, carregando
 */

export function renderKPICard(data) {
    if (data.estado === 'carregando') {
        return `
            <div class="kpi-card loading" aria-busy="true">
                <div class="kpi-card-header">
                    <div class="skeleton" style="width: 60%; height: 16px;"></div>
                    <div class="skeleton" style="width: 50px; height: 16px;"></div>
                </div>
                <div class="kpi-card-body">
                    <div class="skeleton" style="width: 40%; height: 32px; margin-bottom: 8px;"></div>
                    <div class="skeleton" style="width: 30%; height: 14px;"></div>
                </div>
                <div class="kpi-card-footer">
                    <div class="skeleton" style="width: 40%; height: 12px;"></div>
                    <div class="skeleton" style="width: 30%; height: 12px;"></div>
                </div>
            </div>
        `;
    }

    const {
        id_indicador,
        nome_indicador,
        valor_num,
        unidade,
        qualidade = 'ok',
        esfera_fonte = 'federal',
        id_fonte,
        fonte_url = '#',
        dt_coleta,
        posicao_ranking,
        variacao_percentual
    } = data;

    // Trata estado sem_dado declaratório (RF-55 / RT-11) - NUNCA exibe como zero
    const isSemDado = qualidade === 'sem_dado' || valor_num === null || valor_num === undefined;
    const valorFormatado = isSemDado 
        ? 'Sem dado publicado' 
        : (typeof valor_num === 'number' ? valor_num.toLocaleString('pt-BR') : valor_num);

    const variacaoHTML = (!isSemDado && variacao_percentual !== undefined && variacao_percentual !== null)
        ? `<span class="kpi-variation ${variacao_percentual >= 0 ? 'positive' : 'negative'}">
            ${variacao_percentual >= 0 ? '▲' : '▼'} ${Math.abs(variacao_percentual).toFixed(1)}%
           </span>`
        : '';

    const rankingHTML = (!isSemDado && posicao_ranking)
        ? `<div class="kpi-ranking">Posição: <strong>${posicao_ranking}º</strong> no TO</div>`
        : '';

    return `
        <div class="kpi-card" data-indicador="${id_indicador}" data-qualidade="${qualidade}">
            <div class="kpi-card-header">
                <h3 class="kpi-card-title">${nome_indicador}</h3>
                <div class="kpi-badges">
                    <span class="badge-esfera ${esfera_fonte.toLowerCase()}">${esfera_fonte}</span>
                    <span class="badge-qualidade ${qualidade}">${qualidade.replace('_', ' ')}</span>
                </div>
            </div>
            
            <div class="kpi-card-body">
                <div class="kpi-value-container">
                    <span class="kpi-value ${isSemDado ? 'sem-dado' : ''}">${valorFormatado}</span>
                    ${!isSemDado && unidade ? `<span class="kpi-unit">${unidade}</span>` : ''}
                </div>
                ${variacaoHTML}
                ${rankingHTML}
            </div>

            <div class="kpi-card-footer">
                <span>Fonte: <a href="${fonte_url}" target="_blank" rel="noopener noreferrer" class="kpi-fonte-link">${id_fonte}</a></span>
                <span>Atualizado: ${dt_coleta || 'N/A'}</span>
            </div>
        </div>
    `;
}
