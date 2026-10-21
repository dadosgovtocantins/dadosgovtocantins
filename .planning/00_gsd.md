# GSD — Get Shit Done
## O sistema de execução do Painel TO em Dados

> Este arquivo não descreve o produto. Descreve **como o trabalho sai**.
> O `01_system_prompt.md` diz o que vale no código. O `ROADMAP.md` diz o que
> vem depois. O GSD diz o que fazer **nas próximas 4 horas**.

---

## Por que este arquivo existe

O PRD lista dois riscos que matam o projeto, e nenhum deles é técnico:

| Risco | O que é | Onde o GSD ataca |
|---|---|---|
| **RF-08** | Fim da bolsa antes do go-live | Ordem de sacrifício (§5) + entregável fechado por sprint (§3) |
| **RT-09** | Conhecimento concentrado em uma pessoa | Registro obrigatório de decisão (§4) + runbook desde a S1 |

São ~390h em 18 semanas por **uma pessoa só**, que também tem disciplinas —
**~22h/semana**, não 20h. O prazo é fixo; a capacidade é que foi recalibrada. Não há squad, não há revisor, não há quem cubra uma semana perdida.
Um projeto assim não morre de problema difícil — morre de **semana que passou
sem entregar nada fechado**.

O GSD é a trava contra isso.

---

## 1. As sete leis

**Lei 1 — WIP = 1.**
Uma task em `em andamento` por vez. Sempre. Se você quer abrir a próxima, a
atual fecha ou volta explicitamente para `pendente` com o motivo escrito.

**Lei 2 — Nada é feito até estar fechado.**
Código na máquina não conta. Conta: commitado, CI verde, critério de aceite
marcado com evidência colada. "Quase pronto" é igual a não começado.

**Lei 3 — Spec just-in-time.**
Só existe spec completa para a task atual e a próxima. Escrever spec detalhada
de algo que acontece em 3 meses é trabalho que vai ser jogado fora.

**Lei 4 — Timebox de 45 minutos.**
Travou 45 min no mesmo problema sem avançar? Para. Escreve em
`## Decisões tomadas` o que tentou. Escolhe: (a) caminho mais burro que funciona,
(b) marca como bloqueio e pula para outro passo, (c) pergunta ao orientador.
Nunca (d) continuar batendo.

**Lei 5 — O escopo é a variável de ajuste. O prazo não é.**
Atrasou? Não estende a semana. Corta pela ordem de sacrifício (§5).

**Lei 6 — Toda decisão não-óbvia vira uma linha escrita.**
No task file, no momento em que acontece. Não no fim do sprint, não no relatório.
O relatório PIBIEX se escreve sozinho se esta lei for cumprida.

**Lei 7 — Publicar cedo, publicar feio.**
Repositório público desde a S1, mesmo vazio. Catálogo publicado antes do painel
existir. Se a bolsa acabar na S11, o que estiver público é o resultado. O que
estiver na sua máquina, não é.

---

## 2. O bloco de trabalho (a unidade real de execução)

~22h/semana = **4 blocos de 5h30** ou **5 blocos de 4h30**. Escolha um formato e não
mude. O bloco é a unidade — não o dia, não a semana.

### Ritual de entrada (5 min, obrigatório)
```bash
cd "/Users/brunovima/DADOS GOV"
grep -l "status: em andamento" .planning/*.md   # qual é a task
# abre o arquivo, lê o último [x], lê as Decisões tomadas
```
Escreve em uma linha, em voz alta ou no arquivo: **"neste bloco eu fecho o passo N."**
Um passo. Não "avanço na task".

### Durante
- Um passo do plano por vez.
- Terminou o passo → marca `[x]` **no arquivo, na hora**. Não no fim do bloco.
- Decisão não-óbvia → uma linha em `## Decisões tomadas`, na hora.
- Ideia nova que não está na spec → vai para `## Fora de escopo` ou vira task
  nova no ROADMAP. **Não entra de contrabando.**

### Ritual de saída (5 min, obrigatório)
```bash
git add -A && git commit -m "<task NN>: <o que fechou>"
git push
```
Commit todo bloco, mesmo incompleto. Se o próximo bloco for daqui a 4 dias, o
commit é a sua memória. E escreva no task file, em uma linha, **onde exatamente
você parou** — não "parei no passo 3", mas "passo 3: falta tratar o caso de
município sem PIB no SIDRA".

**Bloco sem commit = bloco que não aconteceu.**

---

## 3. A cadência do sprint (2 semanas = ~44h)

| Momento | Quando | O que acontece | Timebox |
|---|---|---|---|
| **Abertura** | Bloco 1 da semana ímpar | Lê o ROADMAP, escreve a spec das tasks do sprint (Lei 3), define o marco | 1h |
| **Execução** | Blocos 2 a 7 | Uma task por vez, WIP=1 | ~39h |
| **Fechamento** | Último bloco | Roda a verificação, marca critérios com evidência, atualiza ROADMAP | 2h |
| **Demo / registro** | Fim do sprint | Grava 3 min de tela OU escreve 10 linhas + 1 print. Vai para `docs/demos/` | 30 min |

A demo não é cerimônia — é o insumo do relatório PIBIEX (1.7.1/1.7.2) e a prova
de vida do projeto para o orientador. **Sprint sem demo é sprint que não aconteceu.**

### Os quatro marcos que não se negociam

| Sprint | Marco | O que precisa estar de pé |
|---|---|---|
| **S3** | Demo 1 | PIB e população dos 139 municípios consultáveis no BigQuery |
| **S5** | Demo 2 | Tela Município navegável nos 139 |
| **S6** | Demo 3 | Tela Estado completa |
| **S7** | Demo 4 | Tela Órgão com os 3 blocos |

Marco perdido dispara a ordem de sacrifício (§5) **no mesmo dia**, não no
sprint seguinte.

---

## 4. Definição de Pronto (DoD) — vale para toda task, sem exceção

Uma task só vira `status: concluída` quando **todas** as linhas abaixo são verdade:

- [ ] Todos os passos do `## Plano` com `[x]`
- [ ] Todos os `## Critérios de aceite` com `[x]` **e evidência colada** (saída
      de comando, `arquivo:linha`, print) — não "funcionou", mas *o que* provou
- [ ] `## Verificação` rodado, **saída real colada no arquivo**
- [ ] `## Decisões tomadas` preenchido (ou "nenhuma decisão não-óbvia" escrito)
- [ ] Commitado e no GitHub, CI verde
- [ ] Gate S1–S21 rodado se a task toca coleta, endpoint, credencial, dado
      público ou deploy — tabela colada no arquivo, **nenhum ❌**
- [ ] `ROADMAP.md` atualizado
- [ ] Runbook (`docs/runbook.md`) atualizado se mudou algo operacional

Sem os 8, o status continua `em andamento`. Não existe "concluída com pendência".

---

## 5. Ordem de sacrifício — o que se corta quando atrasa

Decidida **agora**, com a cabeça fria, para não ser decidida na S15 com a cabeça
quente. Corta-se de cima para baixo:

| # | Corta primeiro | Por quê dá para cortar |
|---|---|---|
| 1 | Modo TV/quiosque (RF-57) | Zero usuários hoje; puro enfeite |
| 2 | Resumo narrativo por IA (RF-26) | Painel funciona inteiro sem ele; é o item de maior risco/menor valor |
| 3 | Parsing por IA do DOE-TO (RF-70, 1.2.9) | Já é piloto no PRD; vira v2 sem perda |
| 4 | Coletores estaduais (1.2.7) | Se o Gate 1 reprovar, já caem sozinhos |
| 5 | Fontes classe B do lote 2 | Reduz de ≥18 para ≥12 fontes ativas; o painel continua de pé |
| 6 | Tela Estado (prioridade 2) | Município é a prioridade 1 e carrega o projeto sozinha |

**O que NUNCA se corta, em nenhuma hipótese:**

| Nunca corta | Por quê |
|---|---|
| Regras de não-oficialidade (RF-10 a RF-14) | Sem isso o painel não pode ir ao ar — é RR-05, risco reputacional |
| Conferência número a número (1.6.2) | Número errado publicado é RF-04 e destrói a credibilidade do projeto |
| Distinção sem_dado × zero (RF-55) | É uma das quatro inovações declaradas do projeto |
| Catálogo + índice de maturidade (RF-43) | É o resultado de pesquisa que sobrevive ao painel (§9.4 do PRD) |
| Código e catálogo abertos no GitHub | É o plano de continuidade inteiro |
| Budget alert e `maximum_bytes_billed` | Sem eles, o teto de R$ 0 vira dívida no cartão pessoal |

---

## 6. Regra de desbloqueio

| Situação | Ação, nesta ordem |
|---|---|
| Fonte federal fora do ar | Não espera. Pula para a próxima fonte do bloco. Volta no próximo sprint. |
| Coletor quebrado por mudança de layout | Timebox 45 min. Não resolveu → marca `qualidade='defasado'` e registra como bloqueio. |
| Decisão que não está na spec | Para. Escreve a pergunta. Se for reversível, decide sozinho e registra. Se for irreversível (ID de projeto, chave canônica, licença), pergunta ao orientador. |
| Gate 1 ou Gate 2 travado | Executa o plano B **já escrito** na task. Nunca improvisa plano B na hora. |
| Duas semanas sem conseguir trabalhar (prova, doença) | Registra no ROADMAP, corta pela ordem de sacrifício, **não tenta recuperar fazendo 40h numa semana**. |

---

## 7. Painel de vida do projeto

Atualizado no fechamento de cada sprint, no topo do `ROADMAP.md`. Seis números,
nada além disso:

| Métrica | Meta no go-live | Fonte |
|---|---|---|
| Fontes com coleta automática | ≥ 18 de 40 | `catalogo_fontes` |
| Municípios com dado (indicadores prioritários) | 139 de 139 | query de cobertura |
| Cards com selo de data + fonte + esfera | 100% | inspeção |
| Serviços pagos ativos | **0** | Cloud Billing |
| % da franquia gratuita consumida no mês | < 70% | Budget alerts + `INFORMATION_SCHEMA` |
| Tasks concluídas / total do sprint | — | `ROADMAP.md` |
| Horas gastas na semana | ~22h | contagem simples |

**A estratégia de custo é uma só: tudo no nível gratuito do Google.** BigQuery,
Cloud Run, Cloud Storage, Scheduler, Logging, Sheets, Apps Script, Looker Studio
e Gemini via AI Studio — todos têm franquia gratuita que cobre a volumetria do
MVP (PRD §5.2). Nenhum serviço fora da franquia é habilitado; quando um serviço
ameaça sair dela, ele é **substituído ou recortado**, nunca pago (RF-95).

Se "% da franquia" passar de 70% em qualquer mês, **isso vira a task mais
importante do sprint seguinte**, na frente de qualquer feature. É restrição de
projeto, não boa prática.

---

## 8. Retomar depois de sumir

```bash
cd "/Users/brunovima/DADOS GOV"
ls .planning/
grep -l "status: em andamento" .planning/*.md
git log --oneline -15
```

Lê o task file em andamento → último `[x]` → `## Decisões tomadas` → a linha de
"onde parei". **Nunca recomeça uma task do zero porque "não lembra".** Se não
lembra, é porque a Lei 6 não foi cumprida — cumpra antes de continuar.

---

## 9. Anti-padrões — o que mata projeto de bolsista

| Anti-padrão | Como se manifesta aqui | Antídoto |
|---|---|---|
| **Arquitetura primeiro** | 3 semanas montando o framework perfeito antes do primeiro dado entrar | Lei 2: a S3 precisa de PIB dos 139 na base, não de abstração bonita |
| **Escopo por empolgação** | "Já que estou aqui, faço o mapa coroplético" | §7.2 do PRD é lei. Ideia boa vira issue, não commit |
| **Perfeccionismo de coletor** | Refazer o coletor do IBGE 4x buscando elegância | RNF-E02: ~40 linhas por fonte. Feio e funcionando > bonito e pendente |
| **Silêncio com o orientador** | 6 semanas sem contato, aí o Gate 2 é uma surpresa | Demo por sprint, mesmo que seja um e-mail de 10 linhas |
| **Guardar para o fim** | Relatório PIBIEX escrito na semana 17 | Lei 6: cada decisão registrada já é parágrafo do relatório |
| **Otimizar custo tarde** | Descobrir o estouro da franquia pela fatura | §7: métrica de franquia todo sprint, desde a S1 |
| **Trabalhar sem fechar** | Semana inteira em 4 tasks, nenhuma concluída | Lei 1: WIP = 1 |

---

## 10. Cartão de bolso

```
ENTRAR:  qual task? qual passo? fecho ESTE passo neste bloco.
DURANTE: 1 passo → [x] na hora → decisão vira linha escrita.
TRAVOU:  45 min. Caminho burro, pula, ou pergunta. Nunca insiste.
SAIR:    commit + push + "onde parei" escrito. Sempre.
SPRINT:  demo + métricas + ROADMAP atualizado.
ATRASOU: corta pela ordem de sacrifício. Nunca estende o prazo.
```
