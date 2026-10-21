-- Checks de Integridade e Consistência do Catálogo em dois níveis
-- Execução esperada: 0 LINHAS retornadas em todas as verificações.

-- 1. IDs duplicados em catalogo_fontes
SELECT id, COUNT(*) AS qtd
FROM `ds_stg.ext_catalogo_fontes`
GROUP BY id
HAVING qtd > 1;

-- 2. Integridade Referencial (FK): id_fonte em indicadores que não existe em fontes
SELECT i.id_indicador, i.id_fonte
FROM `ds_stg.ext_catalogo_indicadores` i
LEFT JOIN `ds_stg.ext_catalogo_fontes` f ON i.id_fonte = f.id
WHERE f.id IS NULL;

-- 3. Valores inválidos nos domínios restritos
SELECT id_indicador, sentido, tela, status
FROM `ds_stg.ext_catalogo_indicadores`
WHERE sentido NOT IN ('maior_melhor', 'menor_melhor', 'neutro')
   OR tela NOT IN ('municipio', 'estado', 'orgao')
   OR status NOT IN ('ativo', 'homologacao', 'descontinuado');

-- 4. Indicador marcado como calculado=TRUE mas sem fórmula preenchida
SELECT id_indicador, calculado, formula
FROM `ds_stg.ext_catalogo_indicadores`
WHERE calculado IS TRUE AND (formula IS NULL OR TRIM(formula) = '');

-- 5. Fontes de alta prioridade (Classe A ou B) sem nenhum indicador cadastrado
SELECT f.id, f.classificacao
FROM `ds_stg.ext_catalogo_fontes` f
LEFT JOIN `ds_stg.ext_catalogo_indicadores` i ON f.id = i.id_fonte
WHERE f.classificacao IN ('A', 'B') AND i.id_indicador IS NULL;

-- 6. Fontes com restrição robots/termos não preenchida
SELECT id, restricao_robots_termos
FROM `ds_stg.ext_catalogo_fontes`
WHERE restricao_robots_termos IS NULL OR TRIM(restricao_robots_termos) = '';
