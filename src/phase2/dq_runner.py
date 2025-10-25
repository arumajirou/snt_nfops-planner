#!/usr/bin/env python
import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
import pandas as pd

def _alias(dataset_name:str)->str:
    ts=datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{dataset_name}_{ts}"

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

def validate(df:pd.DataFrame, schema:dict):
    errors = []
    cols = {c["name"]:c for c in schema["columns"]}
    # 必須列
    for name,spec in cols.items():
        if spec.get("required", False) and name not in df.columns:
            errors.append({"row":None,"col":name,"type":"missing_column","msg":"required column absent"})
    if errors: return df, pd.DataFrame(errors)

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
            idx = df.index[mask]
            for i in idx: row_err.append({"row":int(i),"col":name,"type":"required","msg":"null/empty"})
        # regex
        rgx = spec.get("regex")
        if rgx and s.dtype.name.startswith("string"):
            bad = ~s.fillna("").str.match(re.compile(rgx))
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"regex","msg":f"not match {rgx}"})
        # allowed
        allowed = spec.get("allowed")
        if allowed:
            bad = ~s.isin(allowed)
            bad &= ~s.isna()
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"allowed","msg":f"must be in {allowed}"})
        # range
        rng = spec.get("range")
        if rng and pd.api.types.is_numeric_dtype(s):
            bad = (s < rng.get("min", -float("inf"))) | (s > rng.get("max", float("inf")))
            bad &= ~s.isna()
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"range","msg":f"out of [{rng.get('min','-inf')},{rng.get('max','inf')}]"})

    # 一意制約
    pk = schema.get("primary_keys", [])
    if pk:
        dup_mask = df.duplicated(subset=pk, keep=False)
        for i in df.index[dup_mask]:
            row_err.append({"row":int(i),"col":",".join(pk),"type":"unique","msg":"duplicate key"})

    return df, pd.DataFrame(row_err)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV file path")
    ap.add_argument("--schema", required=True, help="Schema JSON path")
    ap.add_argument("--outdir", default=None, help="output dir (default: outputs/phase2/<alias>)")
    ap.add_argument("--profile", action="store_true", help="emit data_profiling.html if ydata_profiling available")
    ap.add_argument("--fail-on-invalid", action="store_true", help="exit 1 when invalid rows exist")
    args = ap.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    alias = _alias(schema.get("dataset_name","dataset"))
    outdir = Path(args.outdir) if args.outdir else Path("outputs/phase2")/alias
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df_validated, err = validate(df, schema)

    # invalid_rows（元行＋エラー集約）
    if not err.empty:
        # 同じrowのメッセージを集約
        agg = err.groupby("row").apply(lambda g: "; ".join(f"{r.col}:{r.type}" for r in g.itertuples(index=False))).rename("errors")
        invalid = df_validated.loc[agg.index].copy()
        invalid["__errors__"] = agg.values
        invalid.to_parquet(outdir/"invalid_rows.parquet", index=False)
    else:
        # 空でも出力しておくと下流が楽
        pd.DataFrame(columns=list(df.columns)+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)

    # summary.json
    summary = {
        "dataset_name": schema.get("dataset_name","dataset"),
        "n_rows": int(len(df)),
        "n_cols": int(len(df.columns)),
        "n_invalid_rows": int(err["row"].nunique() if not err.empty else 0),
        "checks": (err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records")
                   if not err.empty else []),
        "created_at": datetime.utcnow().isoformat()+"Z",
        "schema_path": str(Path(args.schema).resolve()),
        "input_path": str(Path(args.input).resolve()),
        "output_dir": str(outdir.resolve())
    }
    Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # profiling（任意）
    if args.profile:
        try:
            from ydata_profiling import ProfileReport
            pr = ProfileReport(df_validated, title=f"Data Profiling - {alias}", minimal=True)
            pr.to_file(outdir/"data_profiling.html")
        except Exception as e:
            Path(outdir/"data_profiling.html").write_text(f"profiling failed: {e}")

    # 終了コード（品質ゲート）
    if args.fail_on_invalid and summary["n_invalid_rows"]>0:
        sys.exit(1)

if __name__=="__main__":
    main()
