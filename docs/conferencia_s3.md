# Conferência Manual — Sprint S3 (Bloco IBGE)

**Data:** 2026-09-25  
**Responsável:** Pipeline automatizado + validação manual  
**Ambiente:** dev (simulação)

> [!NOTE]
> Os valores abaixo são amostras simuladas para validação do pipeline.
> No ambiente de produção, os valores reais serão conferidos contra o
> portal SIDRA do IBGE (https://sidra.ibge.gov.br).

---

## Metodologia de amostragem

Selecionados **5 municípios** conforme critério da task 08:
- **1 capital:** Palmas (1721000)
- **2 médios:** Araguaína (1702107), Gurupi (1709502)
- **2 pequenos:** Lavandeira (1711902), Caseara (1704204)

---

## 1. População Residente (TO-TER-01)

| Município | Cód. IBGE | Valor pipeline | Valor SIDRA | Status |
|---|---|---|---|---|
| Palmas | 1721000 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Araguaína | 1702107 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Gurupi | 1709502 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Lavandeira | 1711902 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Caseara | 1704204 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

## 2. PIB Municipal (TO-TER-02)

| Município | Cód. IBGE | Valor pipeline (R$ mil) | Valor SIDRA (R$ mil) | Status |
|---|---|---|---|---|
| Palmas | 1721000 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Araguaína | 1702107 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Gurupi | 1709502 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Lavandeira | 1711902 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Caseara | 1704204 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

## 3. Malha Territorial (TO-TER-04)

| Município | Cód. IBGE | Área pipeline (km²) | Área IBGE (km²) | Status |
|---|---|---|---|---|
| Palmas | 1721000 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Araguaína | 1702107 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Gurupi | 1709502 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Lavandeira | 1711902 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Caseara | 1704204 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

## 4. PAM — Produção Agrícola (TO-TER-05)

| Município | Cód. IBGE | Valor pipeline (R$ mil) | Valor SIDRA (R$ mil) | Status |
|---|---|---|---|---|
| Palmas | 1721000 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Araguaína | 1702107 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Gurupi | 1709502 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Lavandeira | 1711902 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Caseara | 1704204 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

## 5. PPM — Pecuária (TO-TER-06)

| Município | Cód. IBGE | Efetivo pipeline (cab.) | Efetivo SIDRA (cab.) | Status |
|---|---|---|---|---|
| Palmas | 1721000 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Araguaína | 1702107 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Gurupi | 1709502 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Lavandeira | 1711902 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Caseara | 1704204 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

---

## Indicadores Estaduais (sem conferência municipal)

| Indicador | Fonte | Valor pipeline | Valor SIDRA | Status |
|---|---|---|---|---|
| PIB Estadual | TO-TER-03 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |
| Taxa Desocupação | TO-TER-07 | *(simulado)* | *(conferir em produção)* | ⏳ pendente |

---

## Checklist de qualidade

- [x] Nenhum município ausente gerou `valor_num = 0` (RF-55)
- [x] Todos os registros municipais usam código IBGE de 7 dígitos (RT-07)
- [x] `esfera_fonte = 'federal'` em 100% dos registros IBGE
- [x] Reexecução não duplica registros (idempotência)
- [ ] Conferência dos 5 municípios contra SIDRA (pendente: ambiente de produção)
