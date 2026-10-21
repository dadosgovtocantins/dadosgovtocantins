-- DDL para Tabelas Externas do Catálogo em dois níveis no BigQuery
-- Reflete a planilha Google Sheets sem necessidade de redeploy (RF-83)

CREATE OR REPLACE EXTERNAL TABLE `ds_stg.ext_catalogo_fontes` (
  id STRING OPTIONS(description="ID único da fonte de dados (ex: TO-TER-01)"),
  orgao STRING OPTIONS(description="Órgão responsável pela publicação ou custódia do dado"),
  indicador STRING OPTIONS(description="Nome sintético da fonte/pesquisa original"),
  area STRING OPTIONS(description="Área temática (Saúde, Educação, Finanças, etc.)"),
  sistema STRING OPTIONS(description="Nome do sistema de origem (SIDRA, TabNet, SICONFI)"),
  o_que_representa STRING OPTIONS(description="Descrição concisa do conteúdo"),
  link_publico STRING OPTIONS(description="URL pública de consulta"),
  url_da_api STRING OPTIONS(description="Endpoint base da API, quando houver"),
  endpoint STRING OPTIONS(description="Caminho exato da rota ou parâmetro"),
  autenticacao STRING OPTIONS(description="Tipo de autenticação (Nenhuma, Token, OAuth)"),
  formato STRING OPTIONS(description="Formato bruto (JSON, CSV, HTML, PDF)"),
  classe_de_formato STRING OPTIONS(description="Classe estrutural (A, B, C, D)"),
  periodicidade_exata STRING OPTIONS(description="Frequência de atualização oficial"),
  defasagem STRING OPTIONS(description="Tempo médio de atraso na publicação"),
  ultima_atualizacao STRING OPTIONS(description="Data da última coleta ou atualização registrada"),
  historico_disponivel STRING OPTIONS(description="Anos/períodos cobertos pela fonte"),
  nivel_geografico STRING OPTIONS(description="Granularidade geográfica (Municipal, Estadual)"),
  granularidade_temporal STRING OPTIONS(description="Granularidade do tempo (Mensal, Anual)"),
  unidade_de_medida STRING OPTIONS(description="Unidade padrão da fonte"),
  responsavel_pelo_dado STRING OPTIONS(description="Entidade gestora do indicador"),
  fonte_primaria_secundaria STRING OPTIONS(description="Tipo de fonte (Primária ou Secundária)"),
  tipo_de_fonte STRING OPTIONS(description="Tipo da instituição (Federal, Estadual)"),
  fonte_aberta_equivalente STRING OPTIONS(description="Alternativa pública se restrito"),
  painel_lab63_relacionado STRING OPTIONS(description="ID/Link de painel Lab63 se houver"),
  power_bi_dataset_id STRING OPTIONS(description="ID de dataset PowerBI se houver"),
  power_bi_report_id STRING OPTIONS(description="ID de relatório PowerBI se houver"),
  acesso_publico_sem_cadastro STRING OPTIONS(description="Sim / Não"),
  reutilizavel STRING OPTIONS(description="Sim / Não"),
  api_publica STRING OPTIONS(description="Sim / Não"),
  dados_realmente_abertos STRING OPTIONS(description="Sim / Não"),
  quadrante STRING OPTIONS(description="Q1 (Ingerível) ou Q2 (Não ingerível)"),
  escopo STRING OPTIONS(description="Escopo do projeto (In / Out)"),
  licenca_de_uso STRING OPTIONS(description="Licença aplicável (Domínio Público, CC-BY, etc)"),
  restricao_robots_termos STRING OPTIONS(description="Verificação de robots.txt com data"),
  metodo_de_coleta STRING OPTIONS(description="API, Scraping, PySUS, Download Direct"),
  status_de_validacao STRING OPTIONS(description="Homologado / Pendente"),
  nivel_de_confiabilidade STRING OPTIONS(description="DESATIVADA-MVP: Preservada apenas para histórico"),
  classificacao STRING OPTIONS(description="Classe A, B, C ou D"),
  prioridade STRING OPTIONS(description="Prioridade de implementação (1 a 3)"),
  observacoes_tecnicas STRING OPTIONS(description="Notas de implementação")
)
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/placeholder_catalogo'],
  sheet_range = 'catalogo_fontes!A2:AN100',
  skip_leading_rows = 1
);

CREATE OR REPLACE EXTERNAL TABLE `ds_stg.ext_catalogo_indicadores` (
  id_indicador STRING OPTIONS(description="Slug único do indicador atômico (card)"),
  id_fonte STRING OPTIONS(description="Chave estrangeira apontando para ext_catalogo_fontes.id"),
  nome_exibicao STRING OPTIONS(description="Rótulo principal do card no painel"),
  definicao_cidadao STRING OPTIONS(description="Texto explicativo para tooltip cidadão"),
  unidade STRING OPTIONS(description="Unidade única exibida (R$, %, hab, nota)"),
  sentido STRING OPTIONS(description="maior_melhor, menor_melhor ou neutro"),
  tela STRING OPTIONS(description="municipio, estado ou orgao"),
  ordem_card INT64 OPTIONS(description="Ordem de exibição no grid da tela"),
  icone STRING OPTIONS(description="Identificador do ícone visual"),
  calculado BOOL OPTIONS(description="TRUE se derivado de cálculo entre fontes"),
  formula STRING OPTIONS(description="Fórmula matemática em linguagem clara (obrigatório se calculado=TRUE)"),
  status STRING OPTIONS(description="ativo, homologacao ou descontinuado")
)
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/placeholder_catalogo'],
  sheet_range = 'catalogo_indicadores!A2:L100',
  skip_leading_rows = 1
);
