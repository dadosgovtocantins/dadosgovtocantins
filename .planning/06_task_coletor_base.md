---
task: Framework ColetorBase — extração, validação, idempotência e conformidade
status: concluída
sprint: S2
eap: 1.2.1
---

# Framework ColetorBase

## Objetivo
Implementar o contrato que todos os ~18 coletores herdam, padronizando hash,
zona bruta imutável, validação, idempotência, logging e a guarda de conformidade
de coleta.

## Por quê
É a peça que decide se o projeto cabe em 20h/semana: com ela, cada fonte nova
custa ~40 linhas (RNF-E02); sem ela, cada fonte vira um script único e o projeto
não chega a 18 fontes. É também onde moram três garantias que não podem depender
da disciplina do programador em cada coletor: **não coletar fonte bloqueada**
(RF-71), **nunca gravar zero por falha** (RF-66) e **reprocessar sem duplicar**
(RF-67).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletor_base/base.py` | criar — `ColetorBase` (Anexo D) |
| `src/coletor_base/conformidade.py` | criar — guarda de robots/termos |
| `src/coletor_base/validacao.py` | criar — schema, faixa, nulos, cobertura, 3σ |
| `src/coletor_base/armazenamento.py` | criar — raw imutável + hash + dedupe |
| `src/coletor_base/carga.py` | criar — MERGE idempotente no BigQuery |
| `src/coletor_base/log.py` | criar — log JSON da seção 11.3 |
| `src/coletor_base/http.py` | criar — rate limit e User-agent |
| `tests/coletor_base/` | criar — testes dos 7 módulos |

## Critérios de aceite
- [ ] `ColetorBase` expõe `extrair()` e `transformar()` abstratos e `executar()`
      concreto, na ordem do Anexo D: conformidade → extrair → hash → dedupe →
      salvar raw → transformar → validar → carregar
- [ ] **Guarda de conformidade:** coletor cuja fonte tem `RESTRIÇÃO
      ROBOTS/TERMOS` iniciando com "Sim" levanta `ColetaBloqueadaError`
      **antes de qualquer requisição de rede** — teste com mock de socket prova
      que nenhuma conexão foi aberta (RF-71)
- [ ] Hash SHA-256 idêntico ao da última execução ⇒ retorna `sem_mudanca`, não
      grava raw nem carrega (RF-62)
- [ ] Raw gravado em `gs://<proj>-raw/<id_fonte>/<data>/<hash>.<ext>`, imutável
      por retention policy — tentativa de sobrescrever falha (RF-61)
- [ ] Validação **rejeita** e não carrega: lista vazia, `periodo_ref` ausente,
      `valor_num` e `valor_texto` ambos nulos, cobertura municipal < 90%
- [ ] Variação > 3σ ⇒ grava com `qualidade='suspeito'` e **não publica** até
      revisão — teste com série sintética prova (RF-65)
- [ ] `MERGE` por `id_registro`: rodar o mesmo coletor 2x produz exatamente o
      mesmo número de linhas — teste de idempotência (RF-67)
- [ ] Falha de extração preserva o último valor válido com `qualidade='defasado'`
      e **nunca grava zero** — teste com fonte simulando timeout (RF-66)
- [ ] Log JSON com os 10 campos da seção 11.3 em toda execução, sucesso ou falha,
      emitido só por `src/coletor_base/log.py`; nenhum `print()` de texto livre em
      `src/` (busca por `print(` só encontra o módulo de log e o `cli.py`)
- [ ] Rate limit auto-imposto por fonte, mesmo quando a fonte não exige
- [ ] User-agent identifica projeto + instituição + contato público
      (**não** a conta-projeto — PRD §2.3)
- [ ] Execução de um coletor < 10 min (RNF-P04) — medido no coletor de referência
- [ ] Coletor de referência (fonte IBGE simples) implementado em ≤ 50 linhas,
      provando o RNF-E02
- [ ] `pytest --cov=src/coletor_base` ≥ 80%, tudo verde

## Fora de escopo
- Coletores reais além do de referência (tasks 08, 10, 14, 15, 18)
- Playwright (task 18) e parsing por IA (task 21)
- Entrada manual assistida (task 22)
- Cloud Scheduler (task 08)

## Plano
- [ ] 1. `base.py` com o contrato do Anexo D e as exceções específicas
- [ ] 2. `conformidade.py` + teste que prova zero requisições em fonte bloqueada
- [ ] 3. `armazenamento.py`: hash, dedupe, raw imutável
- [ ] 4. `validacao.py`: schema, nulos, faixa, cobertura, 3σ
- [ ] 5. `carga.py`: MERGE idempotente + `maximum_bytes_billed`
- [ ] 6. `log.py` e `http.py` (rate limit, User-agent, retry com backoff)
- [ ] 7. Coletor de referência + medição de tempo
- [ ] 8. Suíte de testes com fixtures de payload real (sem rede)

## Segurança
Gate S1–S21: **S1 segredos** (credenciais só do Secret Manager, nunca em código
ou log), **S2 validação** (toda entrada externa validada contra schema antes da
carga — PRD §12.1), **S3 SQL** (cliente oficial + parâmetros, nunca concatenação),
**S15 erros** (exceção específica; log não vaza credencial nem payload sensível),
**S12 menor privilégio** (SA do coletor só escreve no dataset do seu ambiente),
**S21 API keys** (rotação semestral, nenhuma chave em variável de ambiente em
texto plano).
Conformidade de coleta (§12.3): robots.txt verificado e **datado** por fonte,
rate limit auto-imposto, User-agent identificado.

## Verificação
```bash
pytest tests/coletor_base -q --cov=src/coletor_base --cov-report=term-missing
python -m src.cli coletar --fonte <ID_REFERENCIA> --ambiente dev   # 2x: 2ª deve retornar sem_mudanca
grep -rn "print(" src/ | grep -vE "coletor_base/log.py|cli.py" || echo "OK: log centralizado"
```

## Decisões tomadas
<preenchido durante a execução>
