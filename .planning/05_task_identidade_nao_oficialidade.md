---
task: Identidade visual própria e regras de não-oficialidade
status: concluída
sprint: S2
eap: 1.1.7
---

# Identidade visual e não-oficialidade

## Objetivo
Definir a identidade visual própria do projeto e aplicar as regras que impedem o
painel de ser lido como canal oficial do Governo do Tocantins.

## Por quê
RR-05 é o risco de maior probabilidade **e** maior impacto do projeto: um painel
público com dados de governo, sem vínculo com o governo, é lido como oficial por
padrão. O benchmark de Mato Grosso usa brasão do Estado e foto do governador —
replicar isso aqui induziria a erro sobre a origem do produto e poderia
configurar uso indevido de símbolo oficial. Esta task é o que torna o painel
publicável; sem ela, o Gate 2 não passa.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `docs/identidade.md` | criar — paleta, tipografia, uso da marca, o que é proibido |
| `docs/textos_legais.md` | criar — aviso de não-oficialidade, licença, privacidade |
| Figma | criar — protótipo dos 3 tipos de card + cabeçalho/rodapé |
| `assets/` | criar — marca do projeto, Unitins, PIBIEX |

## Critérios de aceite
- [ ] Paleta própria documentada em tokens, **sem** a paleta institucional do
      Governo do TO; contraste WCAG AA verificado (4.5:1 texto, 3:1 elementos de
      UI) em todos os pares de cor — tabela de contraste no `identidade.md`
- [ ] **Zero** brasão, marca, símbolo oficial do Estado ou foto de agente público
      em qualquer tela (RNF-S08) — checklist visual das telas, item a item
- [ ] Aviso de não-oficialidade visível em **100%** das telas, em cabeçalho ou
      rodapé, com texto fechado e aprovado: projeto acadêmico de extensão da
      Unitins, não é canal oficial do Governo do Tocantins, dados reproduzidos de
      fontes públicas com indicação de origem (RF-10)
- [ ] Marca do projeto + Unitins + PIBIEX presentes e legíveis
- [ ] Endereço de contato público definido e **diferente** do
      e-mail da conta-projeto, sem a partícula "gov" (questão 2 do PRD)
- [ ] Rascunho da página "Sobre" com vínculo PIBIEX, metodologia, licença e canal
      de correção (RF-13)
- [ ] Texto da página de metodologia com o critério A–D e Q1/Q2 (RF-14)
- [ ] Aviso legível em mobile (≥ 360px) — não escondido atrás de menu
- [ ] Protótipo aprovado pelo orientador — registro por e-mail

## Fora de escopo
- Implementar as telas no Looker (tasks 12, 13, 17, 20)
- Domínio próprio (questão 6, S8)
- Certificação de acessibilidade AA auditada (v2, PRD §7.2 item 16)

## Plano
- [ ] 1. Definir paleta, tipografia e tokens; verificar contraste
- [ ] 2. Escrever `docs/textos_legais.md` com o aviso fechado
- [ ] 3. Desenhar cabeçalho, rodapé e os 3 tipos de card no Figma
- [ ] 4. Definir o endereço de contato público (depende das questões 2 e 3)
- [ ] 5. Rascunhar Sobre e metodologia
- [ ] 6. Checklist de não-oficialidade tela a tela
- [ ] 7. Aprovação do orientador

## Segurança
Gate S1–S21 — nesta task o risco é **institucional, não técnico**:
**S1 segredos** (nenhum e-mail interno ou ID exposto em asset ou metadado),
**S11 headers/HTTPS** (N/A aqui, entra na task 22 com a publicação).
Trava dedicada de RR-05/RNF-S08: o checklist de não-oficialidade é condição de
fechamento e é reexecutado na task 24 antes do go-live.

## Verificação
```bash
# Checklist manual, com evidência em docs/identidade.md:
# 1. Abrir cada tela do protótipo e confirmar presença do aviso
# 2. Buscar por brasão/foto/paleta institucional — resultado deve ser zero
# 3. Rodar os pares de cor no verificador de contraste e colar a tabela
```

## Decisões tomadas
<preenchido durante a execução>
