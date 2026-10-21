---
task: Bloco IBGE — primeiras 7 fontes e Demo 1
status: concluída
sprint: S3
eap: 1.2.2
---

# Bloco IBGE

## Objetivo
Colocar PIB municipal e estadual, população, malha territorial, PAM, PPM e PNADC
na base, com os 139 municípios cobertos e agendamento independente por fonte.

## Por quê
É o primeiro dado real do projeto e o marco da **Demo 1**. O bloco IBGE sustenta
a Tela Município, que é a prioridade 1, e é onde se descobre se o `ColetorBase`
realmente funciona — sete fontes com padrões de acesso diferentes (SIDRA, malha,
PNADC) são o teste de fogo do RNF-E02. Se cada uma custar muito mais que ~40
linhas, o framework volta para a bancada antes de existirem mais 11 coletores.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/<id_fonte>.py` | criar — 7 coletores |
| `tests/coletores/` | criar — 7 testes com fixture de payload real |
| `infra/schedulers.yaml` | criar — 1 job por fonte |
| `docs/conferencia_s3.md` | criar — amostra de conferência manual |

## Critérios de aceite
- [ ] 7 coletores implementados: PIB municipal, PIB estadual, população, malha
      territorial, PAM, PPM, PNADC — cada um herdando de `ColetorBase`
- [ ] Cada coletor em ≤ ~50 linhas; nenhum sobrescreve `executar()`
- [ ] **Cobertura 100%:** query retorna 139 municípios com PIB e 139 com população
      (evidência colada)
- [ ] Conferência manual de **5 municípios amostrados** (1 capital, 2 médios,
      2 pequenos) batendo com o SIDRA — planilha de evidência em
      `docs/conferencia_s3.md`, com o valor da fonte e o valor da base lado a lado
- [ ] Município sem dado na fonte entra como `qualidade='sem_dado'`, **nunca** 0
- [ ] Cada coletor executa em < 10 min (RNF-P04) — tempo medido e registrado
- [ ] Reexecução não duplica: contagem de linhas idêntica antes e depois
- [ ] Cloud Scheduler com job independente por fonte, periodicidade conforme o
      catálogo (RF-68)
- [ ] Falha de uma fonte não derruba as outras — teste com uma fonte forçada a falhar
- [ ] Janela total de atualização < 60 min (RNF-P05) para o conjunto
- [ ] Testes rodam sem rede (fixtures gravadas)

## Fora de escopo
- Tela Município (task 13) — aqui o dado fica no BigQuery, não na tela
- Ranking e variação (task 11)
- Demais blocos de fonte (tasks 10, 14, 15)

## Plano
- [ ] 1. Conferir as 7 linhas no `catalogo_indicadores` com `status = homologacao` (RF-82)
- [ ] 2. Coletor de população (o mais simples) → provar o caminho completo
- [ ] 3. PIB municipal e estadual
- [ ] 4. Malha territorial (TO-TER-01) para a miniatura de mapa
- [ ] 5. PAM, PPM, PNADC
- [ ] 6. Conferência manual dos 5 municípios
- [ ] 7. Agendamento por fonte + teste de falha isolada
- [ ] 8. **Demo 1** gravada em `docs/demos/`

## Segurança
Gate S1–S21: **S2 validação** (payload do SIDRA validado contra schema antes da
carga), **S3 SQL** (carga parametrizada), **S15 erros** (fonte fora do ar vira
`defasado`, não exceção silenciosa), **S12 menor privilégio** (SA do ambiente).
Conformidade (§12.3): robots.txt do IBGE verificado e datado no catálogo;
rate limit auto-imposto; User-agent identificado; citação da fonte primária
registrada por indicador (RNF-S06).

## Verificação
```bash
pytest tests/coletores -q
for f in <7 IDs>; do python -m src.cli coletar --fonte $f --ambiente hml; done
bq query --use_legacy_sql=false --maximum_bytes_billed=1000000000 \
  'SELECT id_indicador, COUNT(DISTINCT id_municipio) AS cobertura
   FROM `<proj>.hml_mart.fato_indicador` GROUP BY 1 ORDER BY 2'   # esperado: 139
```

## Decisões tomadas
<preenchido durante a execução>
