#!/usr/bin/env python
import argparse, json, re, sys, hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd

def _alias(dataset_name:str)->str:
    ts=datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{dataset_name}_{ts}"

def _sha256_of_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def _sha256_of_text(txt:str)->str:
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()

def _coerce_dtype(s:pd.Series, spec:dict):
    dt = spec["dtype"]
    if dt=="string": return s.astype("string")
    if dt=="int":    return pd.to_numeric(s, errors="coerce").astype("Int64")
    if dt=="float":  return pd.to_numeric(s, errors="coerce").astype("Float64")
    if dt=="bool":   return s.astype("boolean")
    if dt=="datetime":
        fmt = spec.get("datetime_format", None)
        return pd.to_datetime(s, format=fmt, errors="coerce")
    return s

def validate(df:pd.DataFrame, schema:dict, *, strict_columns:bool):
    errors = []
    cols = {c["name"]:c for c in schema["columns"]}

    # 列厳格チェック（未知列）
    if strict_columns:
        unknown = sorted(set(df.columns) - set(cols.keys()))
        for c in unknown:
            errors.append({"row":None,"col":c,"type":"unknown_column","msg":"not defined in schema"})

    # 必須列の存在
    for name,spec in cols.items():
        if spec.get("required", False) and name not in df.columns:
            errors.append({"row":None,"col":name,"type":"missing_column","msg":"required column absent"})

    if any(e["type"] in ("unknown_column","missing_column") for e in errors):
        # 列の体裁が崩れている場合は以降の行チェックをせず返す
        return df, pd.DataFrame(errors)

    # 型変換
    casted = {}
    for name,spec in cols.items():
        if name in df.columns:
            casted[name] = _coerce_dtype(df[name], spec)
    df = df.assign(**casted)

    # 行単位チェック
    row_err = []
    for name,spec in cols.items():
        if name not in df.columns: continue
        s = df[name]
        # required
        if spec.get("required", False):
            mask = s.isna() | (s.astype(str).str.len()==0)
            for i in df.index[mask]:
                row_err.append({"row":int(i),"col":name,"type":"required","msg":"null/empty"})
        # regex
        rgx = spec.get("regex")
        if rgx and s.dtype.name.startswith("string"):
            bad = ~s.fillna("").str.match(re.compile(rgx))
            for i in df.index[bad]:
                row_err.append({"row":int(i),"col":name,"type":"regex","msg":f"not match {rgx}"})
        # allowed
        allowed = spec.get("allowed")
        if allowed:
            bad = ~s.isin(allowed)
            bad &= ~s.isna()
            for i in df.index[bad]:
                row_err.append({"row":int(i),"col":name,"type":"allowed","msg":f"must be in {allowed}"})
        # range
        rng = spec.get("range")
        if rng and pd.api.types.is_numeric_dtype(s):
            bad = (s < rng.get("min", -float("inf"))) | (s > rng.get("max", float("inf")))
            bad &= ~s.isna()
            for i in df.index[bad]:
                row_err.append({"row":int(i),"col":name,"type":"range","msg":f"out of [{rng.get('min','-inf')},{rng.get('max','inf')}]"})

    # 一意制約
    pk = schema.get("primary_keys", [])
    if pk:
        dup_mask = df.duplicated(subset=pk, keep=False)
        for i in df.index[dup_mask]:
            row_err.append({"row":int(i),"col":",".join(pk),"type":"unique","msg":"duplicate key"})

    # まとめ
    all_err = pd.DataFrame(errors + row_err)
    return df, all_err

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV file path (supports .csv, .csv.gz, .csv.bz2, .csv.zip)")
    ap.add_argument("--schema", required=True, help="Schema JSON path")
    ap.add_argument("--outdir", default=None, help="output dir (default: outputs/phase2/<alias>)")
    ap.add_argument("--profile", action="store_true", help="emit data_profiling.html (lightweight)")
    ap.add_argument("--fail-on-invalid", action="store_true", help="exit 1 when invalid rows exist")
    ap.add_argument("--strict-columns", action="store_true", help="fail when unknown columns exist")
    ap.add_argument("--encoding", default="utf-8", help="CSV encoding (default: utf-8)")
    args = ap.parse_args()

    schema_path = Path(args.schema)
    schema_text = schema_path.read_text(encoding="utf-8")
    schema = json.loads(schema_text)
    schema_hash = _sha256_of_text(schema_text)

    dataset_name = schema.get("dataset_name","dataset")
    alias = _alias(dataset_name)
    outdir = Path(args.outdir) if args.outdir else Path("outputs/phase2")/alias
    outdir.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input)
    # pandasは拡張子でcompressionを自動判定する
    df = pd.read_csv(input_path, encoding=args.encoding)

    df_validated, err = validate(df, schema, strict_columns=args.strict_columns)

    # invalid_rows（元行＋エラー集約）
    if err is not None and not err.empty and "row" in err:
        # 同じrowのメッセージを集約
        agg = err.dropna(subset=["row"]).groupby("row").apply(
            lambda g: "; ".join(f"{r.col}:{r.type}" for r in g.itertuples(index=False))
        ).rename("errors")
        invalid = df_validated.loc[agg.index].copy()
        invalid["__errors__"] = agg.values
        invalid.to_parquet(outdir/"invalid_rows.parquet", index=False)
    else:
        # 空ファイルを出しておく
        pd.DataFrame(columns=list(df.columns)+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)

    # サマリ
    n_rows = int(len(df))
    n_invalid_rows = int(err["row"].nunique()) if err is not None and "row" in err and not err.empty else 0
    invalid_rate = float(n_invalid_rows / n_rows) if n_rows > 0 else 0.0
    content_hash = _sha256_of_file(input_path)

    summary = {
        "dataset_name": dataset_name,
        "n_rows": n_rows,
        "n_cols": int(len(df.columns)),
        "n_invalid_rows": n_invalid_rows,
        "invalid_rate": invalid_rate,
        "checks": (err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records")
                   if err is not None and not err.empty else []),
        "created_at": datetime.utcnow().isoformat()+"Z",
        "schema_path": str(schema_path.resolve()),
        "schema_hash": schema_hash,
        "input_path": str(input_path.resolve()),
        "content_hash": content_hash,
        "output_dir": str(outdir.resolve()),
        "strict_columns": bool(args.strict_columns)
    }
    Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # profiling（任意）
    if args.profile:
        try:
            from ydata_profiling import ProfileReport
            pr = ProfileReport(df_validated, title=f"Data Profiling - {alias}", minimal=True)
            pr.to_file(outdir/"data_profiling.html")
        except Exception as e:
            Path(outdir/"data_profiling.html").write_text(f"profiling failed: {e}", encoding="utf-8")

    # 終了コード（品質ゲート）
    if args.fail_on_invalid and n_invalid_rows>0:
        sys.exit(1)

if __name__=="__main__":
    main()
