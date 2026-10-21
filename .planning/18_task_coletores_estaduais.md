---
task: Coletores estaduais (transparencia.to.gov.br)
status: cortada
sprint: S7
eap: 1.2.7
---

# Coletores Estaduais (CORTADA VIA GATE 1)

## Motivo do Corte
Conforme decisão documentada no **Gate 1** (`docs/spike_transparencia_to.md`), a investigação técnica do portal `transparencia.to.gov.br` comprovou que o mesmo opera sobre a tecnologia Java **Vaadin 8.9.2** (com comunicação exclusiva via GWT/UIDL e estado mantido no servidor), sem exposição de API REST/JSON pública.

Respeitando a Lei 2 do projeto (respeito aos termos/robots e sem contornos invasivos) e o timebox do projeto, a coleta direta deste portal foi **CORTADA** do escopo do MVP.

## Alternativa Adotada
A execução fiscal e orçamentária estadual e municipal é provida pela integração com a **API do SICONFI (Tesouro Nacional)** (Task 15 / `bloco_recursos`), garantindo 100% de cobertura dos relatórios fiscais oficiais (DCA, RREO, RGF e CAPAG).
