---
task: Catálogo em dois níveis — fontes e indicadores
status: concluída
sprint: S2
eap: 1.1.6
---

# Catálogo em dois níveis

## Objetivo
Separar a Base Mestre em `catalogo_fontes` (40 linhas: o que existe e como
coletar) e `catalogo_indicadores` (~70 linhas: o que vira card), com validação
de integridade e log de edição.

## Por quê
Fonte e indicador são entidades distintas e hoje estão misturadas — uma fonte do
IBGE alimenta vários cards, cada um com unidade e sentido próprios. Sem o split,
todo card novo vira mudança de código; com ele, vira uma linha na planilha
(RF-83, RNF-E01). O catálogo também é o contrato que o `ColetorBase` lê em
runtime para decidir se pode coletar (RF-71) — se ele estiver inconsistente,
a guarda de conformidade não funciona.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| Google Sheets — aba `catalogo_fontes` | editar — 40 colunas do Anexo B, chaveada por ID |
| Google Sheets — aba `catalogo_indicadores` | criar — 12 colunas do Anexo B |
| Google Sheets — aba `log_catalogo` | criar — log de edição |
| `apps_script/log_edicao.gs` | criar — RF-04 |
| `apps_script/backup_diario.gs` | criar — export para Cloud Storage |
| `src/catalogo/leitor.py` | criar — leitura tipada do catálogo |
| `src/sql/stg/ext_catalogo.sql` | criar — tabelas externas no BigQuery |
| `src/sql/stg/checks_catalogo.sql` | criar — query de consistência |
| `docs/dicionario.md` | criar — significado de cada coluna |

## Critérios de aceite
- [ ] `catalogo_fontes` com **40 linhas** e as 40 colunas do Anexo B; `ID` único
      (query de duplicata retorna 0)
- [ ] Coluna `NÍVEL DE CONFIABILIDADE` preservada, marcada `DESATIVADA-MVP` no
      cabeçalho e **não lida por nenhum código** (`grep` no `src/` não encontra)
- [ ] `catalogo_indicadores` com ~70 linhas e as 12 colunas do Anexo B
- [ ] **Integridade FK:** todo `id_fonte` existe em `catalogo_fontes.ID` — a query
      de consistência retorna 0 linhas
- [ ] Toda linha tem **uma só** `unidade`, `sentido` ∈ {maior_melhor,
      menor_melhor, neutro}, `tela` ∈ {municipio, estado, orgao}, `status` ∈
      {ativo, homologacao, descontinuado}
- [ ] `calculado = TRUE` sem `formula` preenchida é rejeitado pela validação de
      dados da planilha (não dá para salvar)
- [ ] Toda fonte classe **A ou B** tem pelo menos 1 indicador ligado; toda fonte
      classe **D** tem 0 indicadores e aparece só no bloco 2 da Tela Órgão
- [ ] Coluna `RESTRIÇÃO ROBOTS/TERMOS` preenchida e **datada** nas 40 linhas
      (nenhuma em branco) — é o que a guarda de runtime lê
- [ ] `log_catalogo` grava autor, campo, valor anterior e timestamp a cada edição
      — provado editando uma célula e conferindo a linha gravada
- [ ] Export diário da planilha para `gs://<proj>-backup`, versionado, agendado
- [ ] `ds_stg.ext_catalogo_fontes` e `ext_catalogo_indicadores` consultáveis no
      BigQuery e refletindo a planilha sem deploy (RF-83)
- [ ] `src/catalogo/leitor.py` com teste que falha se uma coluna obrigatória sumir

## Fora de escopo
- Implementar coletores (task 06 em diante)
- Definir a fórmula do score 0–5 (revogado no MVP — RF-84)
- Índice de maturidade (task 19) — consome este catálogo, não faz parte dele

## Plano
- [ ] 1. Revisar as 40 linhas de `catalogo_fontes` e completar `RESTRIÇÃO ROBOTS/TERMOS`
- [ ] 2. Criar `catalogo_indicadores` e derivar ~70 indicadores atômicos das fontes A/B
- [ ] 3. Validação de dados na planilha (listas fechadas + regra do `calculado`)
- [ ] 4. Apps Script de log de edição e de backup diário
- [ ] 5. Tabelas externas no BigQuery
- [ ] 6. `checks_catalogo.sql` com as 5 queries de consistência
- [ ] 7. `leitor.py` + teste
- [ ] 8. `docs/dicionario.md`

## Segurança
Gate S1–S21: **S1 segredos** (nenhuma credencial na planilha — RNF-S03),
**S2 validação** (listas fechadas, FK, tipos — o catálogo é entrada de sistema),
**S12 menor privilégio** (edição da planilha restrita ao P4; leitura pública do
conteúdo é aceitável, gravação não), **S5/LGPD** (indicador que exija microdado é
rejeitado na entrada — RNF-S05, checklist na aprovação da linha).

## Verificação
```bash
bq query --use_legacy_sql=false --maximum_bytes_billed=1000000000 < src/sql/stg/checks_catalogo.sql   # 0 linhas
pytest tests/catalogo -q
grep -ri "confiabilidade" src/ || echo "OK: coluna desativada não é lida"
```

## Decisões tomadas
<preenchido durante a execução>
