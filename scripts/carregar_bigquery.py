"""
Carrega no BigQuery (modo Sandbox) os dados REAIS das 9 fontes implementadas (Task 31).

Sandbox: sem DML (INSERT/MERGE) e com expiração de 60 dias. Por isso a carga é por arquivo,
substituindo o conteúdo da tabela (WRITE_TRUNCATE), e a expiração de cada tabela é renovada a
cada carga. Rode ao menos a cada 60 dias, senão as tabelas expiram.

Uso (da raiz do projeto; tabelas criadas antes com src/sql/aplicar_ddl.sh):
    python scripts/carregar_bigquery.py --ambiente dev       # ~20 min (TO-REC-02)

Credencial: token da conta ativa do gcloud (só em memória, nada gravado em arquivo).
Fonte com erro: a tabela dela NÃO é carregada (fica a carga anterior) e o script devolve 1.
"""

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from scripts.exportar_painel import FONTES, IMPLEMENTADOS, TITULARES, instanciar  # noqa: E402

PROJETO = "project-6f15f3eb-e07f-48fc-ba7"
LOCAL = "southamerica-east1"
MAX_BYTES = 100_000_000  # toda consulta tem teto (o BigQuery cobra no mínimo ~10 MB por tabela)
VALIDADE = timedelta(days=59)  # Sandbox: expiração precisa ser menor que 60 dias
DDL = RAIZ / "src" / "sql" / "ddl"
MESES = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro"


def ler_structs(arquivo: Path) -> list[dict[str, Any]]:
    """Linhas do INSERT ... UNNEST([STRUCT(...)]) do DDL: fonte única dos valores fixos."""
    linhas = []
    for corpo in re.findall(r"STRUCT\((.*)\),?$", arquivo.read_text("utf-8"), re.M):
        par = re.findall(r"('(?:[^']|'(?=[^,]*'\s+AS))*'|TRUE|FALSE)\s+AS\s+(\w+)", corpo)
        linhas.append({c: (v == "TRUE") if v in ("TRUE", "FALSE") else v[1:-1] for v, c in par})
    return linhas


def coletar(id_fonte: str) -> dict[str, Any]:
    """Extrai, transforma e valida uma fonte; o hash do bruto vai em hash_origem (RF-62)."""
    coletor = instanciar(id_fonte)
    try:
        bruto = coletor.extrair()
        registros = coletor.transformar(bruto)
        coletor.validar(registros)
    except Exception as e:
        return {"erro": f"{type(e).__name__}: {e}"[:300]}
    h = hashlib.sha256(bruto).hexdigest()
    return {"registros": [{**r, "hash_origem": h} for r in registros], "coletor": coletor}


def _tempo(periodos: set[str]) -> list[dict[str, Any]]:
    linhas = []
    for p in sorted(periodos):
        d = date.fromisoformat(p)
        linhas.append(
            {
                "data_ref": p,
                "ano": d.year,
                "trimestre": (d.month - 1) // 3 + 1,
                "mes": d.month,
                "nome_mes": MESES.split()[d.month - 1],
                "semestre": 1 if d.month <= 6 else 2,
            }
        )
    return linhas


def _fonte(id_fonte: str, coletor: Any) -> dict[str, Any]:
    meta = getattr(coletor, "metadata_fonte", {}) or {}
    return {
        "id_fonte": id_fonte,
        "id_orgao": getattr(coletor, "id_orgao", None)
        or ("TSE" if id_fonte == TITULARES else "STN"),
        "indicador_fonte": coletor.id_indicador,
        "link_publico": None,
        "esfera": "federal",
        "classificacao": "A",  # API pública estruturada (régua da Base Mestre)
        "quadrante": "Q1",
        "restricao_robots_termos": meta.get("RESTRIÇÃO ROBOTS/TERMOS", "Não restritivo"),
    }


def montar_tabelas(coletas: dict[str, dict[str, Any]], catalogo: dict) -> dict[str, list | None]:
    """Linhas de cada tabela. None = não carregar (alguma fonte da tabela falhou: fica a carga anterior)."""
    ok = {f: c for f, c in coletas.items() if "registros" in c}
    fato_ok = all(f in ok for f in IMPLEMENTADOS)
    fato = [r for f in IMPLEMENTADOS if f in ok for r in ok[f]["registros"]]
    nomes = {
        i["ind"]: i
        for b in catalogo["estado"]["blocos"] + catalogo["municipio"]["blocos"]
        for i in b["itens"]
        if i.get("ind")
    }
    indicadores = []
    for f in IMPLEMENTADOS:
        if f in ok:
            r0, ind = ok[f]["registros"][0], ok[f]["coletor"].id_indicador
            cat = nomes.get(ind, {})
            indicadores.append(
                {
                    "id_indicador": ind,
                    "id_fonte": f,
                    "nome_exibicao": cat.get("titulo", ind),
                    "unidade": r0.get("unidade") or "",
                    "sentido": cat.get("sentido", "neutro"),
                    "tela": "municipio"
                    if any(r["id_municipio"] for r in ok[f]["registros"])
                    else "estado",
                    "calculado": False,
                    "status": "ativo",
                }
            )
    return {
        "dim_municipio": ler_structs(DDL / "dim_municipio.sql"),
        "dim_orgao": ler_structs(DDL / "dim_orgao.sql"),
        "fato_indicador": fato if fato_ok else None,
        "dim_tempo": _tempo({r["periodo_ref"] for r in fato}) if fato_ok else None,
        "dim_indicador": indicadores if fato_ok else None,
        "dim_fonte": [_fonte(f, c["coletor"]) for f, c in ok.items()]
        if len(ok) == len(FONTES)
        else None,
        "dim_titular": ok[TITULARES]["registros"] if TITULARES in ok else None,
    }


def carregar(cliente: Any, ambiente: str, tabelas: dict[str, list | None]) -> dict[str, int | None]:
    """Substitui o conteúdo de cada tabela (load job, sem DML) e renova a expiração do Sandbox."""
    from google.cloud import bigquery

    carregadas = {}
    for nome, linhas in tabelas.items():
        if linhas is None:
            carregadas[nome] = None
            continue
        ref = f"{cliente.project}.{ambiente}_mart.{nome}"
        tabela = cliente.get_table(ref)
        campos = {c.name for c in tabela.schema}
        # NUMERIC aceita até 9 casas; R$ / 1000 em float gera "lixo" (41355.172170000005) e o load recusa
        numericos = {c.name for c in tabela.schema if c.field_type in ("NUMERIC", "BIGNUMERIC")}
        config = bigquery.LoadJobConfig(
            schema=tabela.schema, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        corpo = [
            {
                k: round(v, 9) if k in numericos and isinstance(v, float) else v
                for k, v in r.items()
                if k in campos
            }
            for r in linhas
        ]
        cliente.load_table_from_json(corpo, tabela, job_config=config).result()
        tabela = cliente.get_table(ref)  # recarregada: a carga muda o etag (senão 412)
        tabela.expires = datetime.now(UTC) + VALIDADE
        cliente.update_table(tabela, ["expires"])
        carregadas[nome] = len(corpo)
    return carregadas


def cliente_gcloud(projeto: str):  # pragma: no cover - depende do gcloud logado
    from google.cloud import bigquery
    from google.oauth2.credentials import Credentials

    token = subprocess.run(
        ["gcloud", "auth", "print-access-token"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout.strip()
    return bigquery.Client(project=projeto, location=LOCAL, credentials=Credentials(token))


def main(argv: list[str] | None = None, cliente: Any = None) -> int:
    ap = argparse.ArgumentParser(description="Carrega os dados reais no BigQuery (Sandbox).")
    ap.add_argument("--ambiente", choices=["dev", "hml", "ds"], default="dev")
    ap.add_argument("--projeto", default=PROJETO)
    args = ap.parse_args(argv)

    import json

    catalogo = json.loads(
        (RAIZ / "src" / "ui" / "data" / "painel_indicadores.json").read_text("utf-8")
    )
    coletas = {}
    for f in FONTES:
        print(f"[{datetime.now():%H:%M:%S}] coletando {f}...", flush=True)
        coletas[f] = coletar(f)
        print(
            "    "
            + (
                coletas[f]["erro"]
                if "erro" in coletas[f]
                else f"ok: {len(coletas[f]['registros'])}"
            )
        )
    tabelas = montar_tabelas(coletas, catalogo)
    resultado = carregar(cliente or cliente_gcloud(args.projeto), args.ambiente, tabelas)
    for nome, n in resultado.items():
        print(
            f"  {args.ambiente}_mart.{nome}: "
            + ("NÃO carregada (fonte com erro)" if n is None else f"{n} linhas")
        )
    print(
        f"Expiração renovada para {(datetime.now(UTC) + VALIDADE):%d/%m/%Y}: rode de novo antes disso."
    )
    return 1 if None in resultado.values() else 0


if __name__ == "__main__":
    sys.exit(main())
