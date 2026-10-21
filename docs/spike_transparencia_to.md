# Spike: Inspeção de Coletabilidade — transparencia.to.gov.br (Gate 1)

**Data da Inspeção:** 25 de Setembro de 2026  
**Responsável:** Equipe DADOS GOV  
**Timebox Utilizado:** 2h (Limite: 12h)  

---

## 1. Veredito Executivo do Gate 1

> **VEREDITO: NÃO COLETÁVEL NO MVP**  
> *Motivo:* O portal `transparencia.to.gov.br` é construído sobre o framework Java **Vaadin 8.9.2** (com comunicação baseada em GWT/UIDL e Atmosphere push). O portal **não expõe APIs REST/JSON públicas** ou dados estruturados consumíveis via HTTP tradicional. Qualquer requisição (incluindo `/robots.txt`) é interceptada pelo servlet do Vaadin e retorna a página bootstrap da Single Page Application (SPA).

---

## 2. Evidências Técnicas e Diagnóstico

### 2.1 Análise de `robots.txt` e Termos de Uso
- **Requisição:** `curl -sL https://transparencia.to.gov.br/robots.txt`
- **Resultado:** O servidor retorna `HTTP 200 OK` com `Content-Type: text/html;charset=utf-8` contendo o bootstrap de inicialização do Vaadin (`VAADIN/vaadinBootstrap.js?v=8.9.2`).
- **Conclusão de Conformidade (§12.3):** Não há arquivo `robots.txt` estático exposto. O acesso automatizado via API direta é inviabilizado pela arquitetura do framework.

### 2.2 Inspeção de Arquitetura de Comunicação (XHR / GWT UIDL)
- **Framework:** Vaadin 8.9.2 (Atmosphere 2.4.30.vaadin1 + GWT Stats)
- **Engine Client-Side:** `com.logus.portal.MyAppWidgetset`
- **Protocolo de Comunicação:** GWT RPC / UIDL (User Interface Definition Language) enviado via solicitações `POST` com sincronização de estados de componentes da UI mantidos no lado do servidor (`JSESSIONID`).
- **Endpoint Principal de Chamada:** `./?v-uiId=0` (envio de payloads codificados em formato UIDL proprietary).

### 2.3 Teste de Reprodutibilidade fora do Navegador
```bash
$ curl -sL https://transparencia.to.gov.br/robots.txt
<!doctype html>
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link rel="shortcut icon" type="image/vnd.microsoft.icon" href="./VAADIN/themes/tocantins-theme/favicon.ico">
  ...
 </head>
 <body scroll="auto" class="v-generated-body">
  <div id="ROOT-2521314" class="v-app tocantins-theme portalui"></div>
  <script type="text/javascript" src="./VAADIN/vaadinBootstrap.js?v=8.9.2"></script>
  <script type="text/javascript">
    vaadin.initApplication("ROOT-2521314",{
        "versionInfo": {"vaadinVersion": "8.9.2", "atmosphereVersion": "2.4.30.vaadin1"},
        "widgetset": "com.logus.portal.MyAppWidgetset"
    });
  </script>
 </body>
</html>
```

---

## 3. Cobertura Alternativa via SICONFI (Tesouro Nacional)

Com o veredito de não-coletabilidade direta do portal estadual no MVP, a cobertura fiscal e orçamentária do Estado do Tocantins é assegurada via **SICONFI** (Sistema de Informações Contábeis e Fiscais do Setor Público Brasileiro — API pública do Tesouro Nacional):

- **O que fica coberto via SICONFI:**
  - **DCA (Declaração de Contas Anuais):** Balanço patrimonial, orçamentário e financeiro do Estado do Tocantins e de todos os 139 municípios.
  - **RREO (Relatório Resumido de Execução Orçamentária):** Receitas e despesas por função/subfunção a cada bimestre.
  - **RGF (Relatório de Gestão Fiscal):** Despesa com pessoal, dívida consolidada e garantias a cada quadrimestre/semestre.
  - **CAPAG:** Indicadores de capacidade de pagamento municipal e estadual.

- **O que se perde no MVP (Recorte Não Coberto):**
  - Detalhamento de notas de empenho/liquidação individualizadas por credor/CPF/CNPJ em tempo real (diário).

---

## 4. Impacto no Backlog e Escopo do Projetos

Conforme regra estabelecida no PRD e na spec da Task 09:

1. **Task 18 (`coletores_estaduais`):** Alterada para status **`cortada`** com a devida justificativa técnica registrada.
2. **Task 19 (`indice_maturidade`):** Ajustada para calcular o índice de maturidade de dados abertos avaliando a presença/formato dos dados reutilizáveis (Grau A/B) vs apenas links (Grau D).
3. **Task 20 (`tela_orgao`):** Focada na entrega dos Blocos 2 e 3 (Catálogo de Fontes por Órgão + Maturidade de Dados Abertos).
4. **ROADMAP.md:** Atualizado com a decisão formal do Gate 1.
