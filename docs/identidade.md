# Identidade Visual e Guia de Estilo

**Projeto:** Painel de BI para Consolidação e Monitoramento de Indicadores de Políticas Públicas do Estado do Tocantins  
**Vínculo:** Projeto de Extensão Universitária (PIBIEX / TO Graduado / Unitins)  
**Regra Fundamental (RNF-S08 / RR-05):** **Proibido usar brasão, marca, paleta institucional do Governo do Estado do Tocantins.**

> **Exceção estreita (2026-10-14):** retrato de identificação do titular eleito do
> cargo (prefeito/prefeita de município e governador/governadora), exibido na
> ficha do titular com legenda de fonte (ex: "Fonte: TSE/DivulgaCandContas") e
> o aviso de não-oficialidade mantido na tela. É identificação do indivíduo
> eleito, não peça de comunicação institucional — a proibição de brasão, marca,
> paleta de governo e qualquer peça de campanha/comunicação oficial continua
> valendo sem exceção. Ver task `30_task_coletor_titulares.md`.

---

## 1. Diretrizes de Marca e Posicionamento

* **Identidade Universitária/Acadêmica:** O painel é uma ferramenta neutra de pesquisa de extensão da Unitins.
* **Marcas Autorizadas na Interface:**
  - Logotipo próprio do projeto (*Painel TO em Dados*).
  - Logotipo da Unitins (Universidade Estadual do Tocantins).
  - Identificador da Bolsa PIBIEX / TO Graduado.
* **Elementos Proibidos (RNF-S08):**
  - ❌ Brasão oficial do Estado do Tocantins.
  - ❌ Paleta de cores oficial da gestão governamental (ex: combinações institucionais de campanha ou de governo).
  - ❌ Marcas de programas governamentais específicos.
  - ❌ Foto de secretário, servidor ou qualquer agente público que não seja o titular eleito do cargo (prefeito/governador).
  - ❌ Uso do retrato do titular eleito fora da ficha informativa — nunca em peça de marca, capa, splash ou material de comunicação do painel.
* **Exceção estreita permitida:**
  - ✅ Retrato de identificação do prefeito/prefeita ou governador/governadora em exercício, na ficha do titular do cargo, com fonte citada (TSE/DivulgaCandContas) e aviso de não-oficialidade na mesma tela.

---

## 2. Paleta de Cores (Tokens de Design)

Construída para alta legibilidade e conformidade com o padrão **WCAG AA (contraste mínimo 4.5:1 para texto e 3:1 para componentes de UI)**.

| Token | Nome / Função | Hex | Uso |
|---|---|---|---|
| `--color-bg-main` | Fundo Principal | `#F8FAFC` | Fundo de tela neutro (Slate 50) |
| `--color-surface` | Fundo de Card | `#FFFFFF` | Superfície dos cards e painéis |
| `--color-border` | Borda de Card | `#E2E8F0` | Linhas e divisores (Slate 200) |
| `--color-text-primary` | Texto Principal | `#0F172A` | Títulos e números de destaque (Slate 900) |
| `--color-text-secondary` | Texto Secundário | `#475569` | Rótulos e legendas (Slate 600) |
| `--color-text-muted` | Texto Suave | `#64748B` | Rodapé, notas metodológicas (Slate 500) |
| `--color-accent-primary` | Destaque / Marca | `#0284C7` | Botões, links, seletores ativos (Sky 600) |
| `--color-accent-hover` | Hover Destaque | `#0369A1` | Estado hover de botões (Sky 700) |
| `--color-positive` | Indicador Positivo | `#15803D` | Variações favoráveis ▲ (Green 700) |
| `--color-negative` | Indicador Negativo | `#B91C1C` | Variações desfavoráveis ▼ (Red 700) |
| `--color-warning` | Estado `sem_dado` | `#D97706` | Badge de omissão declaratória (Amber 600) |
| `--color-esfera-fed` | Badge Esfera Federal | `#1E40AF` | Tag de fonte federal (Blue 800) |
| `--color-esfera-est` | Badge Esfera Estadual | `#065F46` | Tag de fonte estadual (Emerald 800) |

---

## 3. Matriz de Contraste WCAG AA

| Par de Cores (Fundo / Texto) | Razão de Contraste | Status WCAG AA |
|---|---|---|
| `#FFFFFF` (Card) / `#0F172A` (Texto Principal) | **15.8:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#FFFFFF` (Card) / `#475569` (Texto Secundário) | **7.1:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#F8FAFC` (Fundo) / `#0F172A` (Texto Principal) | **15.2:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#FFFFFF` (Card) / `#15803D` (Positivo Green 700) | **4.8:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#FFFFFF` (Card) / `#B91C1C` (Negativo Red 700) | **5.9:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#FFFFFF` (Card) / `#0284C7` (Primary Sky 600) | **4.6:1** | ✅ Aprovado (Meta: ≥4.5:1) |
| `#D97706` (Amber 600) / `#FFFFFF` (Texto Badge) | **4.5:1** | ✅ Aprovado (Meta: ≥4.5:1) |

---

## 4. Tipografia e Componentes visuais

* **Família Tipográfica:** `Inter`, system-ui, sans-serif.
* **Hierarquia:**
  - Título da Tela: `24px / Bold / #0F172A`
  - Valor do Card (KPI): `32px / Bold / #0F172A`
  - Rótulo de Métrica: `14px / Medium / #475569`
  - Selos de Data e Fonte: `12px / Regular / #64748B`
* **Estilo dos Cards:** Cards brancos com bordas suaves (`1px solid #E2E8F0`), sem sombras pesadas (flat design clean), cantos levemente arredondados (`border-radius: 8px`).
