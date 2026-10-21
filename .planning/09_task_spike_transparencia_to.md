---
task: Spike — transparencia.to.gov.br (Gate 1)
status: concluída
sprint: S3
eap: — (spike de decisão)
timebox: 12h
---

# Spike: transparencia.to.gov.br — Gate 1

## Objetivo
Determinar, com evidência registrada, se o `transparencia.to.gov.br` expõe uma
camada JSON coletável, e decidir o escopo da Tela Órgão a partir disso.

## Por quê
É a única pergunta do projeto cuja resposta muda o escopo de três tasks (18, 19,
20). O portal roda em JSF/Vaadin, que frequentemente não expõe API pública
(RT-01, probabilidade Alta). **A spike não existe para fazer o portal funcionar —
existe para decidir rápido e seguir.** Por isso tem timebox: 12h estouradas sem
veredito é, por definição, "não coletável no MVP".

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `docs/spike_transparencia_to.md` | criar — evidências, endpoints, veredito |
| Google Sheets `catalogo_fontes` | editar — robots/termos datados, classe, método de coleta |
| `.planning/ROADMAP.md` | editar — registro da decisão do Gate 1 |
| `.planning/18_task_coletores_estaduais.md` | criar ou marcar `cortada` conforme o veredito |

## Critérios de aceite
- [ ] `robots.txt` e termos de uso lidos, **datados** e registrados nas linhas
      correspondentes do catálogo — se houver bloqueio, a investigação para aqui
      e o veredito é NÃO COLETÁVEL, sem tentativa de contorno (RF-71, RNF-S07)
- [ ] Inspeção XHR documentada: lista de endpoints observados, método, formato de
      payload, parâmetros, exigência de sessão/token, com prints
- [ ] Teste de reprodutibilidade: ao menos 1 requisição reproduzida fora do
      navegador (curl/python) com o resultado registrado — sucesso **ou** o erro exato
- [ ] **Veredito escrito, em uma das três formas:**
      `COLETÁVEL (JSON direto)` · `COLETÁVEL COM PLAYWRIGHT (custo X)` ·
      `NÃO COLETÁVEL NO MVP (motivo)`
- [ ] Se não coletável: confirmação de que o **SICONFI cobre parcialmente** a
      execução fiscal, com o recorte exato do que fica coberto e do que se perde
- [ ] Decisão do Gate 1 registrada no `ROADMAP.md` e comunicada ao orientador
- [ ] Task 18 criada (se aprovado) ou marcada `cortada` com o motivo (se reprovado)
- [ ] **Timebox de 12h respeitado** — horas gastas registradas no documento

## Fora de escopo
- Implementar o coletor estadual (é a task 18, condicional)
- Negociar acesso com a ATI (questão 4, fora do escopo até liberação formal)
- Qualquer tentativa de contornar bloqueio técnico ou de termos de uso

## Plano
- [ ] 1. Ler `robots.txt` e termos; registrar e datar no catálogo. Bloqueado → pula para o passo 6
- [ ] 2. Navegar o portal com o DevTools aberto e capturar as chamadas XHR
- [ ] 3. Identificar os endpoints que retornam dado estruturado
- [ ] 4. Reproduzir 1 requisição fora do navegador
- [ ] 5. Estimar o custo de coleta via Playwright, se for o caminho
- [ ] 6. Escrever o veredito e o impacto nas tasks 18, 19 e 20
- [ ] 7. Registrar no ROADMAP e comunicar o orientador

## Segurança
Gate S1–S21: **S2 validação** (nada é ingerido nesta task), **conformidade de
coleta (§12.3)** é o item central — robots.txt verificado e datado, rate limit
respeitado na inspeção, User-agent identificado, **nenhuma tentativa de burlar
bloqueio**. Bloqueio registrado no catálogo faz o coletor falhar por design
(RF-71); a spike não cria exceção a essa regra.

## Verificação
```bash
curl -s https://transparencia.to.gov.br/robots.txt
# Evidência de fechamento = docs/spike_transparencia_to.md com:
#   veredito + endpoints + prints + horas gastas + impacto nas tasks 18/19/20
```

## Decisões tomadas
<preenchido durante a execução — esta é a task em que a seção mais importa:
o veredito do Gate 1 é a decisão mais consequente do projeto>
