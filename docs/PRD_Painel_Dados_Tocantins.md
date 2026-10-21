# **PRD v4 — Painel de Business Intelligence para Consolidação e Monitoramento de Indicadores de Políticas Públicas do Estado do Tocantins**

**Nome curto de trabalho:** Painel TO em Dados **Versão:** 4.2 — com justificativa e inovação do projeto **Autor / Executor:** Bruno Vieira de Melo Aguiar — aluno bolsista PIBIEX, TO Graduado / Unitins **Data:** 31/08/2026 **Estrutura:** Framework de Documentação de Projetos — 12 seções

&nbsp;

## **0\. Sumário executivo**

| Item | Definição |
| :---- | :---- |
| **Nome oficial** | Painel de Business Intelligence para Consolidação e Monitoramento de Indicadores de Políticas Públicas do Estado do Tocantins |
| **Natureza** | Projeto de extensão universitária (PIBIEX / TO Graduado / Unitins) |
| **Executor** | Bruno Vieira de Melo Aguiar, aluno bolsista |
| **Problema** | Indicadores sobre o Tocantins espalhados em 15+ portais, sem camada semântica única |
| **Solução** | Portal público de leitura em 3 níveis: Município → Estado → Órgão |
| **Stack** | Google Sheets \+ Cloud Run \+ BigQuery \+ Looker Studio \+ Gemini |
| **Catálogo** | 40 fontes (30 do lote 1 \+ 10 do lote 2\) |
| **Prazo MVP** | 18 semanas / 9 sprints (recalibrado para 20h/semana) |
| **Custo direto** | Bolsa PIBIEX (institucional) \+ OPEX com teto de R$ 0 |
| **Risco \#1** | Painel público ser lido como canal oficial do Governo do TO |
| **Risco \#2** | Nenhuma fonte estadual é automatizável — o painel mede o território, não a gestão |

---

## **0.1. Reposicionamento institucional — a mudança central da v4**

O projeto não tem sponsor governamental. É executado sob bolsa de extensão universitária, com o aluno como responsável e a Unitins como instituição.

### **O que isso resolve**

| Problema anterior | Como o vínculo acadêmico resolve |
| :---- | :---- |
| **Gate 0 travava tudo** — sem sponsor de órgão, o projeto não avançava | Gate 0 satisfeito: o vínculo institucional é o PIBIEX. O projeto tem legitimidade própria |
| **Risco de leitura política** (RR-01) — governo publicando painel sobre si mesmo | Elimina-se. Painel acadêmico sobre políticas públicas é gênero consolidado e neutro |
| **Reposicionamento “território, não gestão”** era uma concessão desconfortável | Vira coerência. “Indicadores de políticas públicas” é exatamente o que fontes federais medem |
| **Órgãos como validadores obrigatórios** | Deixam de ser gargalo. Viram colaboradores opcionais |

O nome escolhido — *Indicadores de Políticas Públicas do Estado do Tocantins* — já reflete esse reposicionamento corretamente. Não promete entregas de gestão. Promete indicadores de política pública, que é o que o catálogo sustenta.

### **O que isso cria de novo**

| Novo problema | Tratamento |
| :---- | :---- |
| **Sem autoridade para exigir dado de órgão** | Escopo restrito a dados abertos já publicados — regra que a Base Mestre já aplica |
| **Sem orçamento de infraestrutura** | OPEX com teto de R$ 0: arquitetura precisa caber no nível gratuito (seção 5.2) |
| **Painel público sem vínculo com o Estado pode ser confundido com canal oficial** | **Novo risco RR-05.** Regras de não-oficialidade obrigatórias (seção 1.2) |
| **Carga de trabalho de bolsista, não de squad** | Cronograma recalibrado de 12 para 18 semanas (seção 4\) |
| **Descontinuidade ao fim da bolsa** | Plano de continuidade e código aberto como entregável (seção 9.4) |
| **Entregáveis acadêmicos além do software** | Relatórios PIBIEX, resumo e apresentação entram na EAP (seção 3\) |

### **Decisão sobre identidade visual**

O benchmark de Mato Grosso usa brasão do Estado e foto do governador como peça de identidade visual oficial. **Isso não pode ser replicado aqui.** Usar identidade visual oficial em painel não-oficial induz a erro sobre a origem do produto e pode configurar uso indevido de símbolo oficial.

* Identidade visual própria do projeto, com marca da Unitins e do PIBIEX.

* Sem brasão do Estado, sem paleta institucional do Governo do TO, sem foto de secretário ou qualquer agente público além do titular eleito do cargo.

* Aviso permanente e visível: projeto acadêmico de extensão; não é canal oficial do Governo do Tocantins; dados reproduzidos de fontes públicas com indicação de origem.

* **Exceção estreita (2026-10-14):** a ficha informativa do titular do cargo
  (prefeito/prefeita de município, governador/governadora) pode exibir o
  retrato de identificação do eleito, como dado de identificação da pessoa no
  cargo — não como peça de identidade visual do painel. Regras: (1) fonte
  citada na legenda (TSE/DivulgaCandContas); (2) aviso de não-oficialidade
  mantido na mesma tela; (3) nunca usado em logotipo, capa, splash ou material
  de comunicação do projeto; (4) nunca acompanhado de brasão, paleta ou marca
  de governo. Ver task `30_task_coletor_titulares.md`.

---

## **0.2. Respostas consolidadas às questões abertas da v3**

| \# | Questão | Resposta | Efeito no PRD |
| :---- | :---- | :---- | :---- |
| 1 | Sponsor formal | PIBIEX / TO Graduado / Unitins — Bruno Vieira de Melo Aguiar como bolsista | Seção 0.1, 9.1 |
| 2 | Público ou interno na v1 | **Público** | Seção 1.2, RR-05, rigor de conferência elevado |
| 3 | Conta GCP institucional ou pessoal | **Resolvida — opção B:** conta dedicada (e-mail guardado fora do repositório, com o Bruno) | Seção 2.3 |
| 4 | Fórmula do score de confiabilidade | Não existe → **score numérico removido do MVP** | RF-74 revogado; usar CLASSIFICAÇÃO A–D e QUADRANTE Q1/Q2, que são critérios documentados |
| 5 | transparencia.to.gov.br tem camada JSON? | Em aberto — depende do spike | Gate 1, S4 |
| 6 | Base estruturada de “Entregas do Estado” | Não existe → **card removido do MVP** | Escopo 7.2 |
| 7 | Pastas piloto | **Todos os órgãos referenciados na Base Mestre** | Seção 1.2, Tela Órgão |
| 8 | ATI libera datasets do Lab63? | Em aberto | Fora do escopo até liberação formal |
| 9 | Nome oficial | Definido | Cabeçalho |

**Nota sobre a resposta 4:** a leitura mais provável é que o score numérico não tem fórmula documentada. Como “Entregas do Estado” também não tem fonte, os dois foram removidos do MVP. Se a intenção era apenas um deles, o outro pode voltar sem impacto estrutural.

---

## **0.3. Justificativa e inovação do projeto**

Escrita para compor o plano de trabalho e o relatório PIBIEX. Distingue o que é **inovação de produto** (visível ao usuário) do que é **inovação de método** (o valor que sobrevive mesmo que o painel um dia saia do ar — ver seção 9.4).

### **A pergunta certa não é “o dado existe?” — é “o dado é utilizável?”**

O senso comum é que falta dado público no Tocantins. O diagnóstico da seção 0.1 mostra outra coisa: **o dado existe em volume — o catálogo reúne 40 fontes —, mas 15 das 17 fontes estaduais estão em formato que não permite reuso** (HTML dinâmico, PDF, Power BI embutido, robots.txt restritivo). O problema não é ausência de dado. É ausência de uma camada que o torne utilizável.

Nenhum projeto público ou acadêmico no Tocantins hoje **mede essa distância entre “publicado” e “utilizável”** de forma sistemática. Essa medição é a primeira inovação do projeto.

### **1\. Inovação: um índice de maturidade de dados abertos por órgão (RF-43)**

Não existe hoje, para o Governo do Tocantins, um indicador que responda: *“desse órgão, quanto do que ele publica pode ser efetivamente reutilizado por um sistema, e não apenas lido por uma pessoa?”*

O projeto produz esse índice como subproduto direto do catálogo: proporção de fontes por órgão que são classe A/B (ingerível) versus classe D (só link). É um instrumento de diagnóstico que outros estados começam a adotar em iniciativas de dados abertos, mas que não existe hoje aplicado ao Tocantins.

**Por que isso é mais que um card no painel:** é um resultado publicável de pesquisa por si só, independente do painel estar ou não no ar (ver os três cenários de continuidade na seção 9.4). Um catálogo de 40 fontes com classificação metodológica documentada é um artefato acadêmico com valor mesmo se nenhuma linha de coleta automática for escrita.

### **2\. Inovação: cruzamento que hoje só existe manualmente, se existir**

Um card isolado (PIB de um município, cobertura vacinal de outro) já está disponível em algum portal federal. O que não está disponível em lugar nenhum é o **mesmo município, no mesmo momento, com os eixos social, econômico e fiscal lado a lado** — o que a Tela Município entrega. Hoje, produzir essa visão exige abrir SIDRA, TabNet, INEP e SICONFI separadamente e montar a planilha na mão. O projeto elimina esse trabalho de compilação, mas o ganho central não é a economia de tempo — é que a comparação passa a **existir como produto consultável**, o que hoje simplesmente não existe para os 139 municípios.

### **3\. Inovação: tratamento explícito da diferença entre “sem dado” e “dado zero”**

Um detalhe técnico que é, na prática, um ganho de honestidade estatística: fontes declaratórias (SNIS, SICONFI, SINESP) omitem entes que não responderam. Painéis convencionais tendem a exibir isso como zero, o que é factualmente errado e pode penalizar reputacionalmente um município que simplesmente não enviou o dado. O modelo do projeto (qualidade \= 'sem\_dado', RF-55) resolve isso na origem — um cuidado metodológico raro em painéis de dados públicos, inclusive comerciais.

### **4\. Inovação: metodologia replicável, não só um produto**

16 das fontes automatizáveis do catálogo são federais (Anexo A) e seguem o mesmo padrão de acesso (SIDRA, TabNet, SICONFI) para qualquer unidade da federação — troca-se o filtro de UF/município. Isso significa que o ColetorBase e o modelo de catálogo em dois níveis (Anexo B) não são específicos do Tocantins: são um método replicável para qualquer estado brasileiro fazer o mesmo diagnóstico. Essa portabilidade é, ela mesma, um resultado de pesquisa (RNF-E06) — o projeto não entrega só um painel, entrega uma metodologia testada.

---

### **Ganhos para o Estado do Tocantins**

| Ganho | Como se realiza |
| :---- | :---- |
| **Diagnóstico gratuito de maturidade de dados abertos** | O índice de maturidade (item 1\) é, na prática, um raio-x de conformidade com a Lei de Acesso à Informação e com a política de dados abertos, produzido sem custo para o Estado |
| **Evidência para priorização de investimento em TI** | Hoje não há como saber, sem esse diagnóstico, quais sistemas (SIAFE, Lab63, portais setoriais) mais precisam de camada de API pública. O catálogo aponta exatamente onde |
| **Redução de solicitações repetidas via LAI** | Se o dado estiver consolidado e citável no painel, parte da demanda por pedidos formais de acesso à informação tende a cair — o mesmo padrão observado em outros portais de transparência consolidados |
| **Modelo de baixo custo e baixo risco político** | Por ser produto de extensão universitária, o Estado pode observar o resultado, usar o catálogo e eventualmente institucionalizar o painel (cenário 1 da seção 9.4) sem ter comprometido orçamento ou reputação na fase de prova de conceito |
| **Alinhamento com a Lei nº 14.129/2021 (Governo Digital)** e com a política de dados abertos do Estado, sem custo de implementação para o Executivo | O projeto realiza, na prática, parte do que a política pública já prevê — apenas por outra via |
| **Insumo para o TCE-TO e a CGE-TO** | O índice de maturidade e o catálogo de fontes fiscais organizadas por unidade gestora são diretamente aproveitáveis pelos órgãos de controle, que já usam esse tipo de indicador em suas próprias auditorias |

### **Ganhos para o cidadão — além de tempo e agilidade**

| Ganho | Diferença em relação a “economizar tempo” |
| :---- | :---- |
| **Os 139 municípios são tratados com paridade** | Hoje, dado consolidado e navegável de fato só existe, na prática, para a capital e os municípios grandes — os pequenos ficam invisíveis entre planilhas do IBGE. O painel dá a Lagoa da Confusão o mesmo tratamento de Palmas |
| **Instrumento de accountability, não só de consulta** | Jornalista, vereador ou conselho municipal passa a ter uma fonte citável e rastreável (RF-52, ficha de indicador) para cobrar — hoje, cobrar com dado exige primeiro compilar o dado, o que na prática filtra quem consegue fiscalizar |
| **Alfabetização de dados públicos** | As fichas de indicador (RF-54) e a página de metodologia (RF-14) explicam o que cada número significa e de onde vem — o produto ensina a interpretar dado público, não só o exibe |
| **Canal formal de correção** | O formulário público de contestação (RF-58) dá ao cidadão um meio de apontar erro em um número oficial, algo que hoje normalmente exige ofício ou contato informal |
| **Ponto de entrada único para pesquisa e jornalismo de dados** | Reduz a barreira técnica de entrada: hoje, cruzar bases exige saber usar SIDRA, TabNet e SICONFI. Um estudante de jornalismo ou um pesquisador de outra área passa a acessar isso pronto, com export em CSV |
| **Transparência sobre a própria transparência** | O cidadão passa a ver não só o dado, mas **quais órgãos publicam dado reutilizável e quais não** (bloco 3 da Tela Órgão) — informação que hoje não existe em lugar nenhum, nem para o próprio cidadão engajado |

### **Resumo para uso direto no plano de trabalho PIBIEX**

O projeto inova ao (1) medir, pela primeira vez de forma sistemática, a distância entre “dado publicado” e “dado utilizável” no Governo do Tocantins; (2) produzir uma visão municipal consolidada que hoje não existe em nenhum portal, cobrindo os 139 municípios com paridade; (3) tratar com rigor metodológico a diferença entre ausência de dado e dado zero, evitando distorção estatística comum em painéis públicos; e (4) construir um método replicável para qualquer estado brasileiro, não apenas um produto local. Para o Estado, o principal ganho é um diagnóstico gratuito de maturidade de dados abertos, aproveitável por órgãos de controle e planejamento. Para o cidadão, o ganho vai além da agilidade de consulta: é paridade de atenção entre municípios grandes e pequenos, um instrumento citável de accountability, e visibilidade sobre quais órgãos efetivamente praticam dados abertos.

---

# **1\. Escopo de Requisitos Funcionais (RF)**

## **1.1. Gestão de Usuários e Acessos (RBAC)**

Sem Google Workspace institucional do Governo, os perfis mudam.

| ID | Perfil | Autenticação | Permissões |
| :---- | :---- | :---- | :---- |
| P0 | **Público** | Anônimo | Leitura de todas as telas, export CSV, fichas de indicador |
| P1 | **Colaborador do projeto** | Conta Google convidada | P0 \+ telas em homologação |
| P2 | **Ponto focal de órgão (voluntário)** | Conta Google convidada | P1 \+ registrar contestação de indicador |
| P3 | **Orientador PIBIEX** | Conta Google convidada | P2 \+ aprovar publicação de novos indicadores |
| P4 | **Executor / bolsista** | Google Cloud IAM \+ 2FA | Tudo: catálogo, coletores, BigQuery, Cloud Run |
| P5 | **Conta-projeto (owner)** | Cloud IAM \+ 2FA | Billing, IAM, transferência de titularidade |

* **RF-01** — Painel público é anônimo. Não há cadastro de cidadão.

* **RF-02** — Perfis P1–P3 controlados por Google Group do projeto.

* **RF-03** — Service Accounts distintas por ambiente, com menor privilégio.

* **RF-04** — Toda edição no catálogo gera log (autor, campo, valor anterior, timestamp) via Apps Script.

* **RF-05** — **P4 e P5 são contas distintas**, ainda que operadas pela mesma pessoa. Isso viabiliza a transferência de titularidade prevista na seção 9.4 sem entregar a conta pessoal.

* **RF-06** — 2FA obrigatório em P4 e P5.

## **1.2. Módulo Painel Público**

### **Regras de não-oficialidade (novas na v4, obrigatórias)**

* **RF-10** — Aviso fixo no cabeçalho ou rodapé de todas as telas: projeto acadêmico de extensão da Unitins; não é canal oficial do Governo do Tocantins.

* **RF-11** — Identidade visual própria; sem brasão do Estado e sem foto de agentes públicos, **exceto** o retrato de identificação do titular eleito do cargo (prefeito/governador) na própria ficha informativa, com fonte citada — nunca em peça de identidade visual do painel (seção 0.1).

* **RF-12** — Todo card exibe a fonte e a esfera (federal / estadual) do dado.

* **RF-13** — Página “Sobre o projeto”: vínculo PIBIEX, metodologia, catálogo de fontes, licença e canal de contato para correções.

* **RF-14** — Página de metodologia pública, com o critério de classificação das fontes (A–D e Q1/Q2).

### **Tela Município — prioridade 1**

Nove fontes classe A do lote 1 e três do lote 2 sustentam esta tela.

* **RF-20** — Seletor dos 139 municípios com busca por nome.

* **RF-21** — Miniatura do mapa com o município destacado (malha IBGE, TO-TER-01).

* **RF-22** — Cards socioeconômicos: população, PIB municipal, saldo de empregos, produção agrícola, rebanho, exportações.

* **RF-23** — Cards de serviço público: IDEB, matrículas, produção ambulatorial, cobertura vacinal, saneamento.

* **RF-24** — Cards de recurso: convênios federais, repasses FNDE, CAPAG municipal.

* **RF-25** — Posição do município no ranking estadual (1º a 139º) por indicador.

* **RF-26** — Bloco de resumo narrativo por IA, com rótulo explícito de origem automatizada.

### **Tela Estado — prioridade 2**

* **RF-30** — Indicadores estaduais: PIB, PNAD Contínua, IDEB estadual, CAPAG, execução fiscal (SICONFI), convênios totais.

* **RF-31** — Cada card: ícone, valor principal, valor secundário, rótulo, selo de data, selo de esfera.

* **RF-32** — Variação vs. período anterior (▲/▼), colorida conforme o campo sentido.

### **Tela Órgão — prioridade 3, escopo redefinido na v4**

A resposta 7 pede todos os órgãos da Base Mestre, não 5 pastas piloto. Como quase todas as fontes estaduais são classe D, a tela muda de natureza: deixa de ser painel de execução e passa a ser **ficha do órgão**.

* **RF-40** — Seletor com todos os órgãos referenciados na Base Mestre: SEPLAN, SEFAZ, CGE-TO, ATI-TO, SEDUC-TO, SSP-TO, SECTUR, AGETO, SEAGRO/CEASA, TCE-TO e Diário Oficial do Estado.

* **RF-41** — Bloco 1 — **indicadores disponíveis**: cards com dado real, quando houver fonte classe A/B ligada ao órgão.

* **RF-42** — Bloco 2 — **catálogo de fontes do órgão**: lista das fontes classe C/D com link direto, formato, periodicidade e classificação. Entrega valor sem exigir ingestão.

* **RF-43** — Bloco 3 — **transparência do catálogo**: quantas fontes o órgão publica, quantas são reutilizáveis, quantas têm API. Vira um indicador de maturidade de dados abertos por órgão.

* **RF-44** — Selo de cobertura: proporção de fontes do órgão com ingestão automática.

**Por que essa redefinição é melhor:** a Tela Órgão deixa de depender do Gate 1 para existir. Com o Gate 1 aprovado, os blocos 1 e 2 ganham dados de execução. Reprovado, a tela continua entregando o que nenhum portal do Estado entrega hoje — um índice navegável de onde cada órgão publica seus dados. O bloco 3 é, por si só, um resultado de pesquisa de extensão.

### **Transversais**

* **RF-50** — Selo de data de atualização em 100% dos cards.

* **RF-51** — Tooltip com definição em linguagem cidadã.

* **RF-52** — Link “ver fonte original”.

* **RF-53** — Export CSV por indicador, por município e da tela completa.

* **RF-54** — Ficha do indicador: definição, fórmula, fonte, periodicidade, histórico.

* **RF-55** — **Distinção visual entre “sem dado” e “valor zero”** (fontes declaratórias omitem quem não respondeu).

* **RF-56** — Responsividade mobile.

* **RF-57** — Modo TV/quiosque com rotação automática.

* **RF-58** — Canal público de correção: formulário para apontar erro em qualquer card.

## **1.3. Módulo de Ingestão e Operação de Dados**

* **RF-60** — Cada fonte tem coletor herdando de ColetorBase (extrair() / transformar() / executar()).

* **RF-61** — Toda coleta grava o arquivo bruto imutável no Cloud Storage com hash SHA-256.

* **RF-62** — Deduplicação por hash.

* **RF-63** — Camadas obrigatórias: ds\_raw → ds\_stg → ds\_mart.

* **RF-64** — Validação antes da carga: schema, tipo, nulos obrigatórios, faixa plausível, cobertura municipal.

* **RF-65** — Variação \> 3σ entra como qualidade \= 'suspeito' e não publica até revisão.

* **RF-66** — Falha de coleta preserva o último valor válido com selo defasado. Nunca zero por falha.

* **RF-67** — Reprocessamento idempotente via MERGE por id\_registro.

* **RF-68** — Agendamento independente por fonte no Cloud Scheduler.

* **RF-69** — Entrada manual assistida via Sheets \+ Apps Script.

* **RF-70** — Parsing por IA estrutura HTML/PDF em JSON com schema fixo. **IA não calcula valor.**

* **RF-71** — **Conformidade com robots.txt como guarda em runtime**: coletor sobre fonte com bloqueio registrado no catálogo falha por design.

* **RF-72** — Indicador calculado pelo painel exige fórmula publicada na ficha e marcação calculado \= TRUE.

## **1.4. Módulo Administrativo e Base Mestre**

### **Catálogo em dois níveis**

catalogo\_fontes (40 linhas)        → o que existe, onde está, como coletar  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓ 1:N  
catalogo\_indicadores (\~70 linhas)  → o que vira card: 1 unidade, 1 sentido, 1 tela, 1 posição

* **RF-80** — Aba catalogo\_fontes: as 40 colunas atuais, chaveadas por ID.

* **RF-81** — Aba catalogo\_indicadores: id\_indicador, id\_fonte (FK), nome\_exibicao, definicao\_cidadao, unidade, sentido, tela, ordem\_card, icone, calculado, formula, status.

* **RF-82** — Nenhum coletor é implementado antes de a linha existir com status \= homologacao.

* **RF-83** — Alteração no Sheets reflete no painel na próxima sincronização, sem deploy.

* **RF-84** — **Coluna NÍVEL DE CONFIABILIDADE (0-5) desativada no MVP.** A classificação de qualidade passa a usar CLASSIFICAÇÃO (A–D) e QUADRANTE (Q1/Q2), que têm critério explícito. Coluna preservada na planilha para uso futuro, com fórmula documentada.

* **RF-85** — Painel interno de saúde da operação.

* **RF-86** — Fluxo de contestação aberto ao público (RF-58) e a pontos focais.

* **RF-87** — Mudança de metodologia é versionada e exibida na ficha.

## **1.5. Módulo de Custos e Recursos (FinOps) — teto de R$ 0**

Sem orçamento de infraestrutura, o controle de custo deixa de ser boa prática e vira restrição de projeto.

* **RF-90** — Budget alert no Cloud Billing configurado com teto simbólico baixo e alertas em 50%, 80% e 100%.

* **RF-91** — maximum\_bytes\_billed obrigatório em toda consulta.

* **RF-92** — Labels (projeto, ambiente, modulo) em todo recurso.

* **RF-93** — Retenção: Cloud Storage migra para Nearline em 90 dias e Coldline em 365\.

* **RF-94** — Teto mensal de tokens do Gemini; ultrapassado, o parsing por IA suspende e cai para fila manual.

* **RF-95** — **Revisão mensal de aderência ao nível gratuito.** Qualquer serviço que ultrapasse a franquia entra em análise de substituição antes de virar despesa.

---

# **2\. Requisitos Não Funcionais (RNF) e Arquitetura Tecnológica**

## **2.1. Definição de Stack**

| Camada | Tecnologia | Justificativa |
| :---- | :---- | :---- |
| Catálogo / config | Google Sheets \+ Apps Script | Editável por não-técnico; tabela externa no BigQuery |
| Ingestão | Python 3.11 em Cloud Run Jobs | Serverless, escala a zero, nível gratuito generoso |
| Scraping complexo | Playwright em container Cloud Run | Portais JSF/Vaadin |
| Ingestão DATASUS | PySUS ou FTP público | DBC → DBF → CSV |
| Orquestração | Cloud Scheduler | Cron gerenciado |
| Zona bruta | Cloud Storage | Auditabilidade e reprocessamento |
| Warehouse | BigQuery particionado \+ clusterizado | SQL, conector nativo Looker |
| Visualização | Looker Studio | Gratuito, embed público |
| IA | Gemini via AI Studio | Parsing, classificação, narrativa |
| Segredos | Secret Manager | Zero credencial em código |
| Versionamento | GitHub | Histórico, CI/CD e código aberto (seção 9.4) |
| CI/CD | Cloud Build | Nativo GCP |
| Observabilidade | Cloud Logging \+ Monitoring \+ Error Reporting | Nativo |

### **Decisões arquiteturais inegociáveis**

1. **Sheets é catálogo. BigQuery é dado.**

2. **Catálogo em dois níveis.** Fonte e indicador são entidades distintas.

3. **Código IBGE de 7 dígitos é a chave canônica de município.**

4. **Toda escolha de arquitetura é subordinada ao teto de custo zero.** Onde houver conflito entre elegância técnica e franquia gratuita, vence a franquia.

## **2.2. Critérios de Aceite Técnicos**

### **Segurança e Conformidade**

| ID | Critério |
| :---- | :---- |
| RNF-S01 | Zero microdado pessoal — somente agregados |
| RNF-S02 | Criptografia em trânsito (TLS 1.2+) e em repouso |
| RNF-S03 | Nenhuma credencial em código ou no Sheets; scan automatizado no CI |
| RNF-S04 | Audit Logs de acesso a datasets retidos por 12 meses |
| RNF-S05 | LGPD por design: indicador que exija microdado é rejeitado no catálogo. Nome, cargo e retrato de titular eleito em exercício são dado público de transparência ativa (não microdado pessoal) — não se aplica a servidor/secretário |
| RNF-S06 | Licença de uso declarada e citação obrigatória da fonte primária |
| RNF-S07 | Conformidade com robots.txt verificada, datada e aplicada em runtime |
| **RNF-S08** | **Nenhum símbolo oficial do Estado na interface** (RF-11) — brasão, marca e paleta institucional seguem proibidos sem exceção; retrato do titular eleito é a única exceção estreita, limitada à ficha informativa |

### **Performance**

| ID | Critério | Meta |
| :---- | :---- | :---- |
| RNF-P01 | Carregamento da tela principal | \< 5s no p95 |
| RNF-P02 | Troca de município/órgão | \< 3s |
| RNF-P03 | Consulta do painel contra ds\_mart | \< 1 GB processado |
| RNF-P04 | Execução de um coletor | \< 10 min |
| RNF-P05 | Janela total de atualização diária | \< 60 min |
| RNF-P06 | Geração do resumo por IA | \< 15s, pré-computado |
| RNF-P07 | Processamento do Censo Escolar (\>1 GB) | Por chunks; materializar só o recorte TO |

### **Disponibilidade**

| ID | Critério | Meta |
| :---- | :---- | :---- |
| RNF-D01 | Uptime do painel | ≥ 99% mensal, sem compromisso contratual |
| RNF-D02 | Taxa de falha de coletas agendadas | \< 5% |
| RNF-D03 | Backup BigQuery | Snapshot diário, retenção 30 dias |
| RNF-D04 | Backup da Base Mestre | Cópia versionada diária no Cloud Storage |
| RNF-D05 | RPO | 24h |
| RNF-D06 | RTO | 8h úteis, sem plantão |

### **Escalabilidade**

| ID | Critério |
| :---- | :---- |
| RNF-E01 | Novo indicador não exige alteração de código quando a fonte já existe |
| RNF-E02 | Nova fonte \= uma subclasse de ColetorBase (\~40 linhas) |
| RNF-E03 | Arquitetura suporta 40 → 300 indicadores sem redesenho |
| RNF-E04 | Particionamento e clustering mantêm custo estável com o histórico |
| RNF-E05 | Cloud Run escala a zero |
| RNF-E06 | **16 das fontes automatizáveis são federais — o modelo é replicável para qualquer UF trocando o filtro de código.** Isso é resultado de pesquisa publicável, não só arquitetura |

## **2.3. Decisão pendente — conta e projeto no Google Cloud**

Resposta direta à questão 3\.

### **Como o Google Cloud se organiza**

São três camadas distintas, frequentemente confundidas:

| Camada | O que é | Analogia |
| :---- | :---- | :---- |
| **Conta Google** | A identidade que faz login (algo@gmail.com ou algo@unitins.br) | A pessoa |
| **Projeto** | O contêiner onde vivem BigQuery, Cloud Run, buckets. Tem ID próprio | A pasta do projeto |
| **Conta de faturamento** | Onde um meio de pagamento é vinculado. Um projeto só consome recursos pagos se estiver ligado a uma | A carteira |

Uma quarta camada opcional, a **Organização**, existe quando a instituição tem Google Workspace: aí os projetos pertencem à instituição, não à pessoa.

### **As três opções**

| Opção | Como fica | Vantagem | Risco |
| :---- | :---- | :---- | :---- |
| **A — Conta Google pessoal** | Projeto sob o Gmail pessoal do Bruno | Começa hoje, zero burocracia | Projeto acadêmico público hospedado em conta privada; faturamento no cartão pessoal; confusão entre patrimônio pessoal e produto de extensão |
| **B — Conta Google dedicada ao projeto** | Nova conta Google criada só para o painel, ex.: painel.indicadores.to@gmail.com | Isola do pessoal; transferível por entrega de credencial; começa hoje | Ainda não é institucional; depende de disciplina de custódia |
| **C — Conta institucional Unitins** | Projeto sob @unitins.br, idealmente dentro da Organização da universidade | Titularidade institucional correta; continuidade garantida; alinhado à natureza do PIBIEX | Depende da TI da Unitins; pode levar semanas; pode não existir Workspace configurado |

### **Decisão tomada — opção B**

**Conta-projeto:** e-mail guardado fora do repositório, com o Bruno **Data:** 31/08/2026 **Status:** conta criada; configuração de projeto e faturamento pendente.

A opção A foi descartada corretamente. A opção C (@unitins.br) permanece como destino desejável e deve ser negociada em paralelo, sem bloquear o início.

### **Ações restantes para a S1**

1. **Ativar 2FA e configurar recuperação da conta** — telefone e e-mail de recuperação distintos. Esta conta passa a ser ponto único de falha do projeto inteiro (ver ressalva abaixo).

2. Criar o projeto GCP com ID estável (ex.: painel-indicadores-to). O ID é imutável depois de criado.

3. Ativar a conta de faturamento com um meio de pagamento e **configurar budget alert com teto baixo** — o cartão existe para desbloquear serviços, não para gastar.

4. Verificar na página oficial do Google Cloud os créditos de teste vigentes para contas novas e os programas de crédito para pesquisa e educação. Valores e prazos mudam; confirmar antes de contar com eles.

5. Perguntar à coordenação do TO Graduado se a Unitins tem Google Workspace e se há política para projetos de extensão em nuvem (habilita a opção C).

6. Documentar no runbook o procedimento de transferência de titularidade, desde o primeiro dia.

7. Registrar a custódia das credenciais em local seguro e informar o orientador sobre a existência da conta.

### **Ressalvas sobre a conta escolhida**

**1\. Ponto único de falha (novo risco RT-14).** Uma conta Google pessoal não pertence a uma Organização. Consequências práticas: não há administrador institucional capaz de recuperá-la, não há políticas de organização, e a perda de acesso significa a perda do projeto — BigQuery, buckets, agendamentos e o painel publicado. Mitigação: 2FA, recuperação configurada, custódia documentada e código aberto no GitHub desde a S1 (seção 9.4).

**2\. O endereço soa oficial — não usar como canal público (reforça RR-05).** dadosgovtocantins@ lê-se como “dados do Governo do Tocantins”. Para uma conta de infraestrutura isso é irrelevante, porque ela nunca aparece ao usuário. Mas se o mesmo endereço for usado como contato da página Sobre, no rodapé do painel ou no User-agent dos coletores, ele passa a sugerir vínculo governamental — exatamente o que as regras de não-oficialidade (RF-10 a RF-14) existem para evitar.

**Regra decorrente:** \- O e-mail da conta-projeto → uso exclusivamente interno: titularidade do projeto GCP, faturamento, IAM. Nunca exibido ao público. \- Contato público, User-agent dos coletores e rodapé do painel → endereço distinto, preferencialmente institucional (@unitins.br) ou um alias que identifique o projeto como acadêmico, sem a partícula “gov”.

**O que continua valendo:** não vincular o projeto ao e-mail institucional do Governo do Tocantins. O projeto não é do Estado, e um vínculo desses confunde a titularidade.

---

# **3\. Estrutura Analítica do Projeto (EAP)**

1.0 PAINEL DE BI — INDICADORES DE POLÍTICAS PÚBLICAS DO TOCANTINS  
│  
├── 1.1 GOVERNANÇA E FUNDAÇÃO  
│   ├── 1.1.1 Plano de trabalho PIBIEX e alinhamento com o orientador  
│   ├── 1.1.2 Decisão e criação da conta/projeto GCP (seção 2.3)  
│   ├── 1.1.3 Datasets BigQuery (raw/stg/mart) e buckets  
│   ├── 1.1.4 Repositório GitHub público \+ Cloud Build  
│   ├── 1.1.5 Ambientes dev / homologação / produção  
│   ├── 1.1.6 Split do catálogo em catalogo\_fontes \+ catalogo\_indicadores  
│   └── 1.1.7 Identidade visual do projeto e regras de não-oficialidade  
│  
├── 1.2 PACOTE 1 — INGESTÃO DE DADOS  
│   ├── 1.2.1 Framework ColetorBase \+ validação \+ logging \+ guarda de robots.txt  
│   ├── 1.2.2 Bloco IBGE (PIB municipal e estadual, população, malha, PAM, PPM, PNADC)  
│   ├── 1.2.3 Bloco Educação (Saeb, Censo Escolar, Indicadores educacionais, Ideb, FNDE)  
│   ├── 1.2.4 Bloco Trabalho e Economia (Novo CAGED, Comex Stat, Mapa de Empresas)  
│   ├── 1.2.5 Bloco Saúde (SIA/SIH/CNES, PNI, SIM/SINASC via PySUS)  
│   ├── 1.2.6 Bloco Recursos (Transferegov, SICONFI, CAPAG)  
│   ├── 1.2.7 Bloco Estadual condicional (Transparência TO, TCE-TO)  
│   ├── 1.2.8 Módulo de scraping com Playwright  
│   ├── 1.2.9 Módulo de parsing por IA (Gemini)  
│   ├── 1.2.10 Entrada manual assistida  
│   └── 1.2.11 Agendamento e orquestração  
│  
├── 1.3 PACOTE 2 — MODELAGEM E CAMADA SEMÂNTICA  
│   ├── 1.3.1 Dimensões (indicador, órgão, município, fonte, tempo)  
│   ├── 1.3.2 Tabela fato \+ particionamento/clustering  
│   ├── 1.3.3 Views e agregados de consumo  
│   ├── 1.3.4 Ranking municipal (1º a 139º) e variação  
│   ├── 1.3.5 Indicadores calculados  
│   ├── 1.3.6 Índice de maturidade de dados abertos por órgão (RF-43)  
│   └── 1.3.7 Testes de qualidade de dado  
│  
├── 1.4 PACOTE 3 — FRONT-END (LOOKER STUDIO)  
│   ├── 1.4.1 Design system dos cards e paleta própria  
│   ├── 1.4.2 Tela Município (prioridade 1\)  
│   ├── 1.4.3 Tela Estado (prioridade 2\)  
│   ├── 1.4.4 Tela Órgão — 3 blocos (prioridade 3\)  
│   ├── 1.4.5 Fichas de indicador, página Sobre e metodologia  
│   ├── 1.4.6 Export CSV e canal de correção  
│   └── 1.4.7 Modo TV/quiosque  
│  
├── 1.5 PACOTE 4 — ADMINISTRAÇÃO E FINOPS  
│   ├── 1.5.1 Dashboard de saúde da operação  
│   ├── 1.5.2 Fluxo de contestação  
│   ├── 1.5.3 Alertas de defasagem  
│   └── 1.5.4 Budget alerts, quotas e revisão de aderência ao nível gratuito  
│  
├── 1.6 QUALIDADE E GO-LIVE  
│   ├── 1.6.1 Testes automatizados dos coletores  
│   ├── 1.6.2 Conferência número a número vs. fonte oficial  
│   ├── 1.6.3 Revisão de publicação pelo orientador  
│   ├── 1.6.4 Consulta opcional aos órgãos  
│   ├── 1.6.5 Error Reporting e alertas  
│   ├── 1.6.6 Documentação técnica \+ runbook  
│   └── 1.6.7 Deploy em produção e publicação  
│  
└── 1.7 ENTREGÁVEIS ACADÊMICOS (novo na v4)  
&nbsp;&nbsp;&nbsp;&nbsp;├── 1.7.1 Plano de trabalho e relatório parcial PIBIEX  
&nbsp;&nbsp;&nbsp;&nbsp;├── 1.7.2 Relatório final de extensão  
&nbsp;&nbsp;&nbsp;&nbsp;├── 1.7.3 Resumo/artigo: diagnóstico de maturidade de dados abertos no TO  
&nbsp;&nbsp;&nbsp;&nbsp;├── 1.7.4 Apresentação em seminário de iniciação científica/extensão  
&nbsp;&nbsp;&nbsp;&nbsp;└── 1.7.5 Publicação do código e do catálogo como recurso aberto

---

# **4\. Cronograma Executivo e Validações**

**9 sprints de 2 semanas — 18 semanas.** Recalibrado da v3 (12 semanas) para carga de bolsista.

**Premissa de capacidade:** \~20h/semana. O CAPEX de \~350h dividido por 20h/semana resulta em \~18 semanas. Manter 12 semanas exigiria 29h/semana, incompatível com carga de bolsa somada às disciplinas do curso.

| Sprint | Sem. | Tarefa (EAP) | Marco de Validação |
| :---- | :---- | :---- | :---- |
| **S1** | 1–2 | 1.1.1 Plano de trabalho e alinhamento com orientador | Plano aprovado |
|  |  | 1.1.2 Decisão da conta GCP \+ criação do projeto | Projeto GCP ativo com budget alert |
|  |  | 1.1.3–1.1.5 Datasets, CI/CD, ambientes | Pipeline de deploy funcionando |
| **S2** | 3–4 | 1.1.6 Split do catálogo em dois níveis | 40 fontes \+ \~70 indicadores mapeados |
|  |  | 1.1.7 Identidade visual e regras de não-oficialidade | Protótipo com aviso e sem símbolo oficial |
|  |  | 1.2.1 Framework ColetorBase | Teste unitário passando |
| **S3** | 5–6 | 1.2.2 Bloco IBGE — testar os 7 endpoints “PROPOSTO” | **Demo 1:** PIB e população dos 139 municípios na base |
|  |  | 1.3.1–1.3.2 Dimensões \+ fato | dim\_municipio com 139 registros |
|  |  | **Spike: inspeção XHR do transparencia.to.gov.br** | **Gate 1:** decisão sobre dados de execução estadual |
| **S4** | 7–8 | 1.2.3–1.2.4 Educação, Trabalho e Economia | ≥ 10 fontes ativas |
|  |  | 1.3.4 Ranking municipal e variação | Consulta \< 1 GB |
|  |  | 1.4.1 Design system dos cards | Protótipo aprovado |
| **S5** | 9–10 | 1.4.2 **Tela Município** | **Demo 2:** navegável nos 139 municípios |
|  |  | 1.2.5 Bloco Saúde (PySUS) | 3 sistemas DATASUS integrados |
|  |  | 1.7.1 Relatório parcial PIBIEX | Relatório entregue |
| **S6** | 11–12 | 1.2.6 Bloco Recursos (Transferegov, SICONFI, CAPAG) | ≥ 18 fontes ativas |
|  |  | 1.3.5 Indicadores calculados | Fórmulas publicadas nas fichas |
|  |  | 1.4.3 Tela Estado | **Demo 3:** Tela Estado completa |
| **S7** | 13–14 | 1.2.7 Coletores estaduais **se Gate 1 aprovado** | Dados de execução ou justificativa registrada |
|  |  | 1.3.6 Índice de maturidade de dados abertos por órgão | Índice calculado para os 11 órgãos |
|  |  | 1.4.4 **Tela Órgão** (3 blocos) | **Demo 4:** 3 telas completas |
| **S8** | 15–16 | 1.2.9 Parsing por IA (DOE-TO, boletins) | 2 fontes PDF/HTML estruturadas |
|  |  | 1.4.5–1.4.7 Fichas, Sobre, metodologia, CSV, quiosque | Telas de apoio publicadas |
|  |  | 1.5.1–1.5.4 Saúde da operação e FinOps | Budget alerts ativos, custo dentro da franquia |
|  |  | 1.6.1 Testes automatizados | Cobertura dos coletores críticos |
| **S9** | 17–18 | 1.6.2 Conferência número a número | 100% dos cards batendo com a fonte |
|  |  | 1.6.3 Revisão de publicação pelo orientador | **Gate 2:** aprovação acadêmica para publicar |
|  |  | 1.6.4 Consulta opcional aos órgãos | Retorno registrado, sem bloqueio |
|  |  | 1.6.5–1.6.7 Monitoramento, runbook, deploy | **Go-Live** |
|  |  | 1.7.2–1.7.5 Entregáveis acadêmicos | Relatório final, resumo, código aberto |

### **Gates de decisão — revisados**

| Gate | Sem. | Pergunta | Se não passar |
| :---- | :---- | :---- | :---- |
| ~~Gate 0~~ | — | **Resolvido pela v4:** o vínculo institucional é o PIBIEX | — |
| **Gate 1** | 6 | O transparencia.to.gov.br expõe camada JSON coletável? | Tela Órgão entrega os blocos 2 e 3 (catálogo e maturidade), sem execução orçamentária |
| **Gate 2** | 17 | O orientador aprova a publicação? | Painel fica restrito ao grupo do projeto até correção |

**Mudança importante no Gate 2:** na v3 ele dependia do aceite dos órgãos. Órgãos não têm obrigação de homologar um projeto acadêmico, e transformar isso em gate criaria uma dependência sem contrapartida. A validação passa a ser: conferência número a número (interna) \+ aprovação do orientador (institucional) \+ consulta aos órgãos (informativa, não bloqueante).

---

# **5\. Planejamento Financeiro**

## **5.1. CAPEX**

| Item | Esforço (h) |
| :---- | :---- |
| Governança e fundação (1.1) | 50 |
| Ingestão — framework \+ \~18 coletores (1.2) | 130 |
| Modelagem e camada semântica (1.3) | 55 |
| Front-end Looker (1.4) | 60 |
| Administração e FinOps (1.5) | 20 |
| Qualidade e go-live (1.6) | 45 |
| **Entregáveis acadêmicos (1.7)** | **30** |
| **Total** | **\~390h** |

**Natureza do custo:** o esforço é coberto pela bolsa PIBIEX, não por contrato. Não há CAPEX financeiro relevante além do tempo.

| Custo não-hora | Estimativa |
| :---- | :---- |
| Domínio próprio (opcional) | R$ 0–100/ano |
| Certificado SSL | R$ 0 (gerenciado) |
| Licenças de software | R$ 0 (nível gratuito Google \+ open source) |

**Valor de referência para o relatório PIBIEX:** \~390h a preço de mercado (R$ 120–180/h) equivalem a R$ 47–70 mil. Registrar isso no relatório final dimensiona corretamente o produto de extensão entregue.

## **5.2. OPEX — teto de R$ 0**

| Serviço | Driver | Volumetria MVP | Cabe na franquia? |
| :---- | :---- | :---- | :---- |
| BigQuery — storage | GB armazenados | \< 20 GB | Sim, se o Censo Escolar for materializado só no recorte TO |
| **BigQuery — consultas** | **TB processados/mês** | Depende de acessos ao painel público | **Sim, apenas com agregados \+ cache** |
| Cloud Run Jobs | vCPU-s e requisições | Execuções curtas diárias | Sim |
| Cloud Storage | GB \+ classe | \< 10 GB | Sim |
| Cloud Scheduler | Jobs ativos | \< 25 jobs | Sim |
| Cloud Logging | GB ingeridos | Baixo | Sim |
| Gemini API | Tokens | Parsing eventual com teto | Sim, com teto |
| Looker Studio | — | — | Gratuito |

### **Alerta crítico — agora é restrição, não recomendação**

O painel é **público**. Isso muda o cálculo: o número de consultas deixa de ser previsível. BigQuery cobra por **byte processado**, não por consulta. Um painel público lendo a tabela fato bruta pode sair da franquia gratuita em um único dia de tráfego atípico — uma matéria de jornal citando o painel, por exemplo.

**Controles obrigatórios (não opcionais neste cenário):**

1. Looker consulta **apenas** agregados pré-materializados em ds\_mart, com poucos MB por consulta.

2. **Extract Data ativado** nas três telas públicas — o Looker passa a servir de um snapshot em memória, não do BigQuery a cada acesso.

3. maximum\_bytes\_billed em toda consulta.

4. Particionamento por periodo\_ref obrigatório.

5. Budget alert com teto baixo e notificação imediata.

6. Revisão mensal de aderência à franquia (RF-95).

**Métrica de acompanhamento:** bytes processados por 1.000 sessões. É a métrica que decide se o projeto sobrevive sem orçamento.

---

# **6\. Stack Tecnológica e Ferramentas de Execução**

| Categoria | Ferramenta | Uso |
| :---- | :---- | :---- |
| Gestão e backlog | GitHub Projects | EAP → issues → sprints |
| Documentação | Google Docs \+ /docs em Markdown | PRD, runbook, dicionário de dados, relatórios PIBIEX |
| UI/UX | Figma | Protótipo dos cards e identidade própria |
| Modelagem de dados | dbdiagram.io / Markdown | Star schema |
| IDE | VS Code | Python \+ SQL |
| Controle de versão | Git \+ GitHub **público** | main (prod), hml, feature/\* |
| CI/CD | Cloud Build | Push → build → deploy |
| Cloud | Google Cloud Platform | Projeto único, 3 ambientes |
| Containerização | Docker | Python \+ Playwright \+ PySUS |
| Segredos | Secret Manager | Chaves de API |
| Monitoramento | Cloud Monitoring \+ Error Reporting | Uptime e falhas de job |
| Logs | Cloud Logging | 30 dias padrão |
| IA de apoio | Gemini (AI Studio) | Parsing, classificação, narrativa |
| Referência acadêmica | Zotero ou similar | Bibliografia dos entregáveis 1.7 |

---

# **7\. Escopo do Projeto (In/Out)**

## **7.1. In Scope — MVP v1**

| \# | Entrega |
| :---- | :---- |
| 1 | Tela Município (139) — prioridade 1 |
| 2 | Tela Estado — prioridade 2 |
| 3 | Tela Órgão em 3 blocos, cobrindo os 11 órgãos da Base Mestre |
| 4 | 40 fontes catalogadas; ≥ 18 com coleta automatizada |
| 5 | \~70 indicadores atômicos mapeados a cards |
| 6 | Catálogo em dois níveis com governança de edição |
| 7 | Star schema completo no BigQuery com histórico |
| 8 | Selo de atualização, esfera da fonte e link para origem em 100% dos cards |
| 9 | Ficha de indicador com definição, fórmula e metodologia |
| 10 | Export CSV por indicador e por município |
| 11 | Ranking municipal (1º a 139º) |
| 12 | **Índice de maturidade de dados abertos por órgão** |
| 13 | Resumo narrativo por IA com revisão humana |
| 14 | Página Sobre, metodologia e canal público de correção |
| 15 | Regras de não-oficialidade aplicadas em todas as telas |
| 16 | Dashboard interno de saúde da operação |
| 17 | Runbook operacional \+ documentação técnica |
| 18 | Modo TV/quiosque |
| 19 | **Entregáveis acadêmicos: relatórios PIBIEX, resumo/artigo, código aberto** |

## **7.2. Out of Scope**

| \# | Fora do escopo | Justificativa | Destino |
| :---- | :---- | :---- | :---- |
| 1 | **Card “Entregas do Estado”** | **Confirmado: não existe base estruturada no TO** | Fora do roadmap |
| 2 | **Score numérico de confiabilidade (0–5)** | **Confirmado: não há fórmula documentada**; classificação A–D e Q1/Q2 cumprem a função | v2, com fórmula publicada |
| 3 | Mapa coroplético interativo | Custo alto no Looker | v2 |
| 4 | Metas do PPA vs. realizado | Exige base de metas estruturada | v2, após diagnóstico |
| 5 | Alertas automáticos de variação para gestores | Depende de base madura | v2 |
| 6 | API pública de saída | O painel consome, não serve dados a terceiros | v3 |
| 7 | App mobile nativo | Web responsiva atende | Fora do roadmap |
| 8 | Login com senha própria | Painel público é anônimo | Fora do roadmap |
| 9 | Ranking comparativo entre gestões | Painel é descritivo, não avaliativo | Fora do roadmap |
| 10 | Microdados e dados pessoais | LGPD | Fora do roadmap |
| 11 | Fontes que exijam ofício ou acordo institucional | Projeto acadêmico sem poder requisitório | Lista de expansão negociada |
| 12 | Ingestão de fontes com robots.txt restritivo (Lab63) | Termos de uso; entram como link | Até liberação formal da ATI |
| 13 | Integração com SIAFE, folha e sistemas internos | Exige acesso privilegiado | Fora do roadmap |
| 14 | Diário Oficial com extração por IA em produção | Entra como piloto na S8 | v2 |
| 15 | Camadas temáticas do Geoportal | Malha IBGE cobre o mapa base | v2 |
| 16 | Acessibilidade AA certificada | Básica sim; certificação exige auditoria | v2 |
| 17 | **Uso de brasão, marca ou identidade visual do Governo do TO** | **Projeto não é oficial** | Fora do roadmap |

**Cláusula de controle:** item desta lista solicitado durante a execução gera solicitação formal de mudança (seção 9), com reestimativa e ciência do orientador.

---

# **8\. Riscos do Projeto**

## **8.1. Riscos Técnicos**

| \# | Risco | Prob. | Impacto | Mitigação |
| :---- | :---- | :---- | :---- | :---- |
| RT-10 | Nenhuma fonte estadual é classe A — o painel mede o território, não a gestão | Confirmada | Médio | Reposicionamento resolvido pelo nome e pela natureza acadêmica; selo de esfera por card |
| RT-01 | transparencia.to.gov.br em JSF sem API pública | Alta | Médio | Gate 1 na S6; Playwright como plano B; SICONFI como cobertura parcial |
| RT-02 | Painéis Lab63 com robots.txt restritivo | Confirmada | Baixo | Fora do escopo de ingestão; entram como link |
| RT-03 | Fonte muda layout e quebra o coletor | Alta | Médio | Hash de estrutura \+ alerta \+ selo defasado |
| RT-04 | Rate limit ou instabilidade de APIs federais | Média | Médio | Retry com backoff; coleta fora do pico; cache do último payload |
| RT-05 | Performance do Looker | Média | Médio | Agregados \+ Extract Data |
| RT-06 | IA alucina valor no parsing | Média | Alto | IA não calcula; validação de schema; flag gerado\_por\_ia |
| RT-07 | Divergência de código de município | Alta | Médio | Código IBGE 7 dígitos como chave canônica |
| RT-08 | Vazamento por indicador mal catalogado | Baixa | Alto | Checklist LGPD na aprovação |
| RT-09 | Conhecimento concentrado em uma pessoa | Alta | Alto | Runbook \+ ColetorBase \+ código aberto |
| RT-11 | Fontes declaratórias omitem entes que não responderam | Alta | Alto | Distinguir “sem dado” de zero |
| RT-12 | Indicadores calculados divergem de números oficiais | Alta | Alto | Fórmula publicada; média trienal em municípios pequenos |
| RT-13 | Censo Escolar \> 1 GB estoura memória do Cloud Run | Média | Médio | Processamento por chunks |
| **RT-14** | **Conta-projeto é Google pessoal, sem Organização — perda de acesso implica perda do projeto** | Baixa | **Crítico** | 2FA, recuperação configurada, custódia documentada, código e catálogo abertos no GitHub, migração para @unitins.br quando viável |

## **8.2. Riscos Financeiros**

| \# | Risco | Prob. | Impacto | Mitigação |
| :---- | :---- | :---- | :---- | :---- |
| **RF-07** | **Painel público gera pico de tráfego e estoura a franquia gratuita** | **Média** | **Alto** | Extract Data, agregados, maximum\_bytes\_billed, budget alert com teto baixo |
| RF-01 | Consulta não otimizada eleva custo do BigQuery | Alta | Alto | Mesmos controles da seção 5.2 |
| RF-02 | Custo de Gemini escalando com parsing | Média | Baixo | Teto mensal; cache por hash |
| RF-03 | Retrabalho por mudança de escopo | Média | Médio | Seção 7.2 \+ esteira da seção 9 |
| RF-04 | Retrabalho por número contestado após publicação | Média | Alto | Conferência número a número; canal de correção |
| **RF-08** | **Fim da bolsa antes do go-live** | **Média** | **Alto** | Cronograma de 18 semanas com folga; entregáveis parciais em cada sprint; código aberto desde a S1 |

## **8.3. Riscos de Reputação e Institucionais**

| \# | Risco | Prob. | Impacto | Mitigação |
| :---- | :---- | :---- | :---- | :---- |
| **RR-05** | **Painel público ser lido como canal oficial do Governo do TO** | **Alta** | **Alto** | RF-10 a RF-14: aviso permanente, identidade própria, sem símbolo oficial, página Sobre explicando o vínculo PIBIEX |
| RR-02 | Órgão discorda de um número | Média | Médio | Card leva à fonte original; canal público de correção; resposta em até 5 dias úteis |
| RR-03 | Painel desatualizado transmite descaso | Média | Médio | Selo de data; defasagem sinalizada, não escondida |
| **RR-06** | **Índice de maturidade por órgão ser lido como ranking de exposição** | Média | Médio | Publicar como diagnóstico de dados abertos, com metodologia e sem tom avaliativo; enquadrar como contribuição, não denúncia |
| RR-01 | Leitura política do painel | Baixa | Médio | Natureza acadêmica reduz o risco; manter caráter descritivo |

**Sobre RR-06:** o índice de maturidade (RF-43) é a contribuição científica mais original do projeto e, simultaneamente, o item mais sensível. Ele torna visível quais órgãos publicam dados reutilizáveis e quais não. Publicá-lo como resultado metodológico de extensão é legítimo; publicá-lo como ranking de “quem é transparente” muda o tom e cria atrito desnecessário.

---

# **9\. Governança e Continuidade**

## **9.1. Papéis**

| Papel | Quem | Responsabilidade |
| :---- | :---- | :---- |
| **Instituição** | Unitins / TO Graduado / PIBIEX | Vínculo institucional e legitimidade |
| **Orientador** | A definir na S1 | Aprova publicação, valida método, avalia entregáveis |
| **Executor / bolsista** | Bruno Vieira de Melo Aguiar | Produto, catálogo, coletores, painel, relatórios |
| **Pontos focais de órgão** | Voluntários | Colaboração e contestação — **sem obrigação formal** |
| **Público** | Cidadãos, jornalistas, pesquisadores | Consumo e apontamento de correções |

## **9.2. Esteira de controle de mudanças**

Solicitação de mudança  
&nbsp;&nbsp;↓ registro em issue (o quê / por quê / quem pediu)  
Classificação: \[Correção\] · \[Melhoria\] · \[Novo escopo\]  
&nbsp;&nbsp;↓  
Correção     → sprint corrente  
Melhoria     → backlog priorizado  
Novo escopo  → estimativa \+ ciência do orientador  
&nbsp;&nbsp;↓ registro no changelog  
Execução

Alteração de metodologia de indicador é versionada e exibida na ficha.

## **9.3. Regras de acesso administrativo**

* Escrita no BigQuery de produção: exclusiva das Service Accounts do pipeline.

* Alteração em produção só por merge em main com CI verde.

* 2FA obrigatório em P4 e P5.

* Credenciais custodiadas na conta-projeto, não na conta pessoal (RF-05).

## **9.4. Continuidade — o ponto crítico de um projeto de bolsa**

Projeto de bolsa tem prazo. Sem plano, o painel sai do ar quando a bolsa acaba. Quatro medidas:

1. **Código aberto desde a S1.** Repositório público no GitHub, com licença permissiva. O trabalho sobrevive à conta.

2. **Catálogo publicado como recurso aberto.** As 40 fontes catalogadas têm valor independente do painel — é um produto de extensão por si só.

3. **Conta-projeto separada da pessoal** (seção 2.3, opção B), com procedimento de transferência documentado no runbook desde o primeiro dia.

4. **Três cenários de saída documentados no relatório final:**

   * *Institucionalização:* Unitins ou órgão do Estado assume o projeto e a titularidade da conta.

   * *Manutenção acadêmica:* novo bolsista assume; a documentação e o ColetorBase viabilizam a transição.

   * *Arquivamento:* painel é desligado, mas código, catálogo e relatórios permanecem públicos como resultado de pesquisa.

O cenário de arquivamento não é fracasso. Um catálogo de 40 fontes documentadas e um diagnóstico de maturidade de dados abertos do estado são resultado de extensão válido mesmo sem painel no ar.

---

# **10\. Atendimento e Suporte**

## **10.1. SLA — recalibrado para projeto acadêmico**

| Sev. | Definição | Resposta | Resolução |
| :---- | :---- | :---- | :---- |
| **S1 — Crítica** | Número comprovadamente errado publicado, ou painel fora do ar | 1 dia útil | 3 dias úteis |
| **S2 — Alta** | Tela indisponível ou fonte crítica sem coleta há \> 7 dias | 3 dias úteis | 7 dias úteis |
| **S3 — Média** | Indicador defasado, falha isolada de coletor | 5 dias úteis | Próximo sprint |
| **S4 — Baixa** | Melhoria, ajuste visual, dúvida | 7 dias úteis | Backlog |

**Mudança em relação à v3:** o SLA de 1h para S1 era incompatível com um executor único e bolsista. Prometer o que não se pode cumprir é pior que declarar o prazo real. O painel é informativo, não transacional, e o SLA declarado na página Sobre deve ser este.

## **10.2. Matriz de escalonamento**

| Nível | Escopo | Quem | Ações |
| :---- | :---- | :---- | :---- |
| **N1 — Triagem** | Recebe e classifica correções do público e de órgãos | Executor (via formulário RF-58) | Registro em issue, resposta ao solicitante |
| **N2 — Aplicação e dados** | Bugs e falhas de coleta | Executor | Reexecutar coletor, corrigir view, reprocessar |
| **N3 — Infra e crítico** | Falhas de plataforma, custo, segurança | Executor \+ suporte GCP \+ orientador | Restauração de backup, contenção de custo, incidente |

**Pré-requisito mantido:** o suporte não inicia antes de a stack de monitoramento (seção 11\) estar em produção.

---

# **11\. Monitoramento**

## **11.1. Separação estrita de ambientes**

| Ambiente | Datasets | Origem | Uso |
| :---- | :---- | :---- | :---- |
| **DEV** | dev\_raw, dev\_stg, dev\_mart | Amostra reduzida | Desenvolvimento |
| **HML** | hml\_raw, hml\_stg, hml\_mart | Dado real, não publicado | Homologação |
| **PROD** | ds\_raw, ds\_stg, ds\_mart | Dado real, publicado | Operação |

Nenhum coletor vai a PROD sem passar por HML. Nenhuma alteração manual em PROD.

## **11.2. O que é monitorado**

| Camada | Métrica | Ferramenta | Alerta |
| :---- | :---- | :---- | :---- |
| Disponibilidade | Uptime da URL | Uptime Check | 2 checks falhos |
| Pipeline | Sucesso/falha por job | Logging \+ Monitoring | Qualquer falha |
| Frescor | Indicadores além da periodicidade | Query agendada | Diário |
| Qualidade | Registros com qualidade ≠ ok | Dashboard interno | \> 5% |
| Anomalia | Variação \> 3σ | Query agendada | Bloqueio de publicação |
| Cobertura | % dos 139 municípios com dado por indicador | Query agendada | \< 90% |
| **Custo / franquia** | **Bytes processados e % da franquia consumida** | **Budget alerts \+ BigQuery INFORMATION\_SCHEMA** | **50 / 80 / 100%** |
| Erros | Exceções nos coletores | Error Reporting | Exceção nova |
| Uso | Sessões e telas mais acessadas | Google Analytics | Relatório mensal |

## **11.3. Padrão de log**

Log estruturado (JSON) por execução: id\_execucao, id\_fonte, id\_indicador, status, linhas\_processadas, municipios\_cobertos, duracao\_ms, bytes\_processados, hash\_origem, erro.

## **11.4. Dashboard de saúde da operação**

Painel Looker interno: fontes ativas vs. falhando, última coleta por fonte, indicadores defasados, cobertura municipal, taxa de falha 30 dias, **consumo da franquia gratuita**. Entrega da S8.

---

# **12\. Segurança**

## **12.1. Sanitização e tratamento de dados**

* Toda entrada externa validada contra schema antes da carga.

* Escrita no BigQuery via cliente oficial e parâmetros — nunca concatenação de string em SQL.

* Conteúdo enviado ao Gemini limitado ao necessário; nenhuma credencial em prompt.

* Saída do Gemini validada contra schema JSON; resposta fora do schema é descartada.

* Normalização de encoding e códigos IBGE na camada stg, nunca na raw.

* Conversão DBC→DBF→CSV do DATASUS em container isolado.

## **12.2. Proteção de acesso e endpoints**

* Painel público somente leitura, sem endpoint de escrita exposto.

* Cloud Run Jobs sem endpoint HTTP público — acionados só por Scheduler com Service Account.

* Menor privilégio em todas as Service Accounts.

* Secret Manager para todas as chaves; rotação semestral.

* Nenhuma credencial no Sheets, no repositório público ou em variável de ambiente em texto plano. **Com repositório aberto, o scan de segredos no CI deixa de ser precaução e vira requisito.**

## **12.3. Conformidade de coleta**

* Verificação de robots.txt e termos registrada e datada por fonte no catálogo.

* Guarda em runtime (RF-71): coletor sobre fonte bloqueada falha por design.

* Rate limit auto-imposto por fonte, mesmo quando não exigido.

* User-agent identificando o projeto, a instituição e um canal de contato.

* Citação obrigatória da fonte primária em todo card e em todo export.

## **12.4. Code review e esteira**

* Branch main protegida; merge só via pull request.

* CI obrigatório: lint, testes e **scan de segredos**.

* Auto-revisão documentada por checklist, dado o executor único.

* Dependências revisadas trimestralmente.

## **12.5. Backup e recuperação**

| Ativo | Estratégia | Retenção | Imutabilidade |
| :---- | :---- | :---- | :---- |
| BigQuery (ds\_mart) | Snapshot diário | 30 dias | Dataset separado, escrita bloqueada |
| Cloud Storage (raw) | Versionamento \+ retention policy | 365 dias | Bucket com retention lock |
| Base Mestre (Sheets) | Export diário para Cloud Storage | 90 dias | Versionamento de objeto |
| Código | GitHub público \+ tags de release | Permanente | — |
| Configuração de infra | Script versionado | Permanente | — |

**Teste de restauração semestral obrigatório.**

## **12.6. LGPD**

* Base exclusivamente de dados agregados e públicos.

* Checklist de aprovação de indicador: “este dado permite identificar uma pessoa, isolado ou combinado?” Resposta afirmativa \= rejeitado.

* Ressalva registrada em TO-SEG-01 vale para toda a área de segurança pública.

* Nenhum dado pessoal do usuário do painel além de analytics agregado.

* Política de privacidade publicada, com identificação do responsável pelo tratamento e canal de contato — **exigência reforçada por o painel ser público e o responsável ser pessoa física vinculada à instituição.**

---

# **13\. Questões em aberto**

| \# | Questão | Prazo | Impacto |
| :---- | :---- | :---- | :---- |
| 1 | **Quem é o orientador PIBIEX?** | S1 | Gate 2 e governança |
| 2 | **Qual endereço de contato público do painel?** (não pode ser a conta-projeto — seção 2.3) | S2 | RR-05 |
| 3 | A Unitins tem Google Workspace disponível para projetos de extensão? | S2 | Viabiliza a opção C e resolve a questão 2 |
| 4 | A ATI libera os datasets por trás dos painéis Lab63? | S3 | Desbloqueia 4 fontes classe D |
| 5 | O transparencia.to.gov.br tem camada JSON? | S6 | Gate 1 |
| 6 | Domínio próprio ou URL do Looker Studio? | S8 | Identidade e permanência do link |
| 7 | O painel será listado em algum repositório institucional da Unitins? | S9 | Continuidade e visibilidade acadêmica |

**Resolvida na v4.1:** conta e projeto no Google Cloud — opção B, conta dedicada (seção 2.3).

---

# **Anexo A — Catálogo consolidado (40 fontes)**

| Classificação | Lote 1 | Lote 2 | Total | Esfera predominante |
| :---- | :---- | :---- | :---- | :---- |
| A — Ingestão automática | 11 | 5 | **16** | 100% federal |
| B — Ingestão com tratamento | 3 | 5 | **8** | 90% federal |
| C — Extração/parser | 1 | 0 | **1** | Estadual (DOE-TO) |
| D — Somente link para consulta | 15 | 0 | **15** | 100% estadual |
| **Total** | **30** | **10** | **40** |  |

## **Órgãos estaduais cobertos pela Tela Órgão (RF-40)**

SEPLAN · SEFAZ · CGE-TO · ATI-TO · SEDUC-TO · SSP-TO · SECTUR · AGETO · SEAGRO/CEASA · TCE-TO · Diário Oficial do Estado

Órgãos com dado exclusivamente classe D entregam os blocos 2 e 3 da Tela Órgão (catálogo de fontes e índice de maturidade), sem o bloco 1 de indicadores.

---

# **Anexo B — Catálogo em dois níveis**

### **catalogo\_fontes — 40 colunas mantidas**

ID · ÓRGÃO · INDICADOR · ÁREA · SISTEMA · O QUE REPRESENTA · LINK PÚBLICO · URL DA API · ENDPOINT · AUTENTICAÇÃO · FORMATO · CLASSE DE FORMATO · PERIODICIDADE EXATA · DEFASAGEM · ÚLTIMA ATUALIZAÇÃO · HISTÓRICO DISPONÍVEL · NÍVEL GEOGRÁFICO · GRANULARIDADE TEMPORAL · UNIDADE DE MEDIDA · RESPONSÁVEL PELO DADO · FONTE PRIMÁRIA/SECUNDÁRIA · TIPO DE FONTE · FONTE ABERTA EQUIVALENTE · PAINEL LAB63 RELACIONADO · POWER BI DATASET ID · POWER BI REPORT ID · ACESSO PÚBLICO SEM CADASTRO? · REUTILIZÁVEL? · API PÚBLICA? · DADOS REALMENTE ABERTOS? · QUADRANTE · ESCOPO · LICENÇA DE USO · RESTRIÇÃO ROBOTS/TERMOS · MÉTODO DE COLETA · STATUS DE VALIDAÇÃO · ~~NÍVEL DE CONFIABILIDADE~~ *(desativada no MVP)* · CLASSIFICAÇÃO · PRIORIDADE · OBSERVAÇÕES TÉCNICAS

### **catalogo\_indicadores — nova aba**

| Coluna | Descrição |
| :---- | :---- |
| id\_indicador | Slug único do indicador atômico |
| id\_fonte | FK para catalogo\_fontes.ID |
| nome\_exibicao | Rótulo do card |
| definicao\_cidadao | Texto do tooltip |
| unidade | **Uma só** — R$ / % / unidade / posição / nota / texto |
| sentido | maior\_melhor / menor\_melhor / neutro |
| tela | municipio / estado / orgao |
| ordem\_card | Posição no grid |
| icone | Referência do ícone |
| calculado | TRUE se derivado de outras fontes |
| formula | Obrigatória quando calculado \= TRUE |
| status | ativo / homologacao / descontinuado |

---

# **Anexo C — Modelo de dados (star schema)**

**CREATE** **TABLE** ds\_mart.fato\_indicador (  
&nbsp;&nbsp;id\_registro       STRING    **NOT** **NULL**,  *\-- hash(indicador+orgao+municipio+periodo)*  
&nbsp;&nbsp;id\_indicador      STRING    **NOT** **NULL**,  
&nbsp;&nbsp;id\_orgao          STRING,              *\-- null \= nível Estado*  
&nbsp;&nbsp;id\_municipio      STRING,              *\-- código IBGE 7 dígitos; null \= estadual*  
&nbsp;&nbsp;periodo\_ref       DATE      **NOT** **NULL**,  
&nbsp;&nbsp;periodicidade     STRING    **NOT** **NULL**,  
&nbsp;&nbsp;valor\_num         NUMERIC,  
&nbsp;&nbsp;valor\_texto       STRING,              *\-- CAPAG "A"*  
&nbsp;&nbsp;unidade           STRING,  
&nbsp;&nbsp;posicao\_ranking   INT64,               *\-- posição entre os 139 municípios*  
&nbsp;&nbsp;id\_fonte          STRING    **NOT** **NULL**,  
&nbsp;&nbsp;esfera\_fonte      STRING,              *\-- federal | estadual  (RF-12)*  
&nbsp;&nbsp;dt\_coleta         TIMESTAMP **NOT** **NULL**,  
&nbsp;&nbsp;dt\_publicacao\_org DATE,  
&nbsp;&nbsp;qualidade         STRING,              *\-- ok|estimado|defasado|suspeito|sem\_dado|falho*  
&nbsp;&nbsp;calculado         BOOL,  
&nbsp;&nbsp;gerado\_por\_ia     BOOL,  
&nbsp;&nbsp;hash\_origem       STRING  
)  
**PARTITION** **BY** periodo\_ref  
**CLUSTER** **BY** id\_indicador, id\_municipio;

**Dimensões:** dim\_indicador, dim\_orgao, dim\_municipio, dim\_fonte, dim\_tempo.

qualidade \= 'sem\_dado' é distinto de falho e de zero. Fontes declaratórias omitem entes que não responderam (RT-11); a diferença entre “não informou” e “informou zero” precisa chegar até a tela (RF-55).

---

# **Anexo D — Contrato do coletor**

*\# coletor\_base.py — contrato que todo coletor implementa*  
**from** abc **import** ABC, abstractmethod  
**import** hashlib

**class** ColetorBase(ABC):  
&nbsp;&nbsp;&nbsp;&nbsp;id\_fonte: str  
&nbsp;&nbsp;&nbsp;&nbsp;id\_indicador: str

&nbsp;&nbsp;&nbsp;&nbsp;@abstractmethod  
&nbsp;&nbsp;&nbsp;&nbsp;**def** extrair(self) \-\> bytes:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*"""Baixa o conteúdo bruto da origem."""*

&nbsp;&nbsp;&nbsp;&nbsp;@abstractmethod  
&nbsp;&nbsp;&nbsp;&nbsp;**def** transformar(self, bruto: bytes) \-\> list\[dict\]:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*"""Converte para o schema de fato\_indicador."""*

&nbsp;&nbsp;&nbsp;&nbsp;**def** executar(self):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.\_checar\_conformidade()     *\# robots.txt / termos — RF-71*  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bruto \= self.extrair()  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;h \= hashlib.sha256(bruto).hexdigest()

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**if** self.\_hash\_ja\_processado(h):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**return** {"status": "sem\_mudanca", "hash": h}

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.\_salvar\_raw(bruto, h)      *\# Cloud Storage (imutável)*  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;registros \= self.transformar(bruto)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.\_validar(registros)        *\# schema \+ faixa \+ nulos \+ cobertura*  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.\_carregar(registros, h)    *\# BigQuery MERGE (idempotente)*  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**return** {"status": "ok", "linhas": len(registros)}

&nbsp;&nbsp;&nbsp;&nbsp;**def** \_checar\_conformidade(self):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fonte \= self.\_ler\_catalogo(self.id\_fonte)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**if** fonte\["RESTRIÇÃO ROBOTS/TERMOS"\].startswith("Sim"):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**raise** PermissionError(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"{self.id\_fonte}: coleta bloqueada por robots.txt/termos registrados no catálogo"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)

&nbsp;&nbsp;&nbsp;&nbsp;**def** \_validar(self, registros: list\[dict\]):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**if** **not** registros:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**raise** ValueError(f"{self.id\_indicador}: zero registros")  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**for** r **in** registros:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**assert** r.get("periodo\_ref"), "periodo\_ref ausente"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**assert** r.get("valor\_num") **is** **not** None **or** r.get("valor\_texto")

Cada fonte nova \= uma subclasse (\~40 linhas). Padroniza logging, hash, validação, idempotência e conformidade de coleta.