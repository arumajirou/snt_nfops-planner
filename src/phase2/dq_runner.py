#!/usr/bin/env python
import argparse, json, re, sys, hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd

try:
    import pyarrow as pa, pyarrow.parquet as pq
except Exception:
    pa = pq = None

def _alias(dataset_name:str)->str:
    return f"{dataset_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def _sha256_of_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''): h.update(chunk)
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
        fmt = spec.get("datetime_format")
        return pd.to_datetime(s, format=fmt, errors="coerce")
    return s

def validate(df:pd.DataFrame, schema:dict, *, strict_columns:bool):
    errors = []
    cols = {c["name"]:c for c in schema["columns"]}

    # 未知列・必須列チェック（行検証の前に）
    if strict_columns:
        unknown = sorted(set(df.columns) - set(cols.keys()))
        for c in unknown:
            errors.append({"row":None,"col":c,"type":"unknown_column","msg":"not defined in schema"})
    for name,spec in cols.items():
        if spec.get("required", False) and name not in df.columns:
            errors.append({"row":None,"col":name,"type":"missing_column","msg":"required column absent"})
    if any(e["type"] in ("unknown_column","missing_column") for e in errors):
        return df, pd.DataFrame(errors)

    # 型変換
    casted = {name:_coerce_dtype(df[name],spec) for name,spec in cols.items() if name in df.columns}
    if casted: df = df.assign(**casted)

    # 行検証
    row_err = []
    for name,spec in cols.items():
        if name not in df.columns: continue
        s = df[name]
        if spec.get("required", False):
            m = s.isna() | (s.astype(str).str.len()==0)
            for i in df.index[m]: row_err.append({"row":int(i),"col":name,"type":"required","msg":"null/empty"})
        rgx = spec.get("regex")
        if rgx and s.dtype.name.startswith("string"):
            bad = ~s.fillna("").str.match(re.compile(rgx))
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"regex","msg":f"not match {rgx}"})
        allowed = spec.get("allowed")
        if allowed is not None:
            bad = ~s.isin(allowed); bad &= ~s.isna()
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"allowed","msg":f"must be in {allowed}"})
        rng = spec.get("range")
        if rng and pd.api.types.is_numeric_dtype(s):
            bad = (s < rng.get("min", float("-inf"))) | (s > rng.get("max", float("inf"))); bad &= ~s.isna()
            for i in df.index[bad]: row_err.append({"row":int(i),"col":name,"type":"range","msg":f"out of [{rng.get('min','-inf')},{rng.get('max','inf')}]"})

    pk = schema.get("primary_keys", [])
    if pk:
        dup = df.duplicated(subset=pk, keep=False)
        for i in df.index[dup]: row_err.append({"row":int(i),"col":",".join(pk),"type":"unique","msg":"duplicate key"})

    return df, pd.DataFrame(errors+row_err)

def _read_with_encoding_auto(path:Path, **kw):
    enc = kw.pop("encoding", "utf-8")
    tried = []
    for e in ([enc] if enc!="auto" else ["utf-8","cp932","shift_jis","euc-jp"]):
        try:
            return pd.read_csv(path, encoding=e, **kw), e
        except Exception as ex:
            tried.append((e, str(ex)))
    raise RuntimeError(f"CSV decoding failed. tried={tried}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV path (.csv[.gz|.bz2|.zip])")
    ap.add_argument("--schema", required=True, help="Schema JSON path")
    ap.add_argument("--outdir", default=None, help="Output dir (default: outputs/phase2/<alias>)")
    ap.add_argument("--profile", action="store_true", help="Emit data_profiling.html (lightweight)")
    ap.add_argument("--fail-on-invalid", action="store_true", help="Exit 1 when invalid rows exist")
    ap.add_argument("--strict-columns", action="store_true", help="Fail when unknown columns exist")
    ap.add_argument("--encoding", default="utf-8", help="CSV encoding or 'auto'")
    ap.add_argument("--chunksize", type=int, default=0, help="Row chunksize for streaming validation (0=disabled)")
    ap.add_argument("--invalid-cap", type=int, default=10000, help="Max invalid rows to save")
    ap.add_argument("--invalid-rate-threshold", type=float, default=None, help="Exit nonzero if invalid_rate >= threshold")
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

    # 列の体裁チェック用にヘッダだけ読む
    header_df, used_enc = _read_with_encoding_auto(input_path, nrows=0, encoding=args.encoding)
    _, early_err = validate(header_df, schema, strict_columns=args.strict_columns)
    if early_err is not None and not early_err.empty:
        early_err.to_csv(outdir/"schema_errors.csv", index=False)
        # 行単位検証は継続せず summary を出す
        n_rows = int(pd.read_csv(input_path, encoding=used_enc, usecols=[0]).shape[0]) if header_df is not None else 0
        summary = {
            "dataset_name": dataset_name, "n_rows": n_rows, "n_cols": int(len(header_df.columns)),
            "n_invalid_rows": 0, "invalid_rate": 0.0, "checks": early_err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records"),
            "created_at": datetime.utcnow().isoformat()+"Z", "schema_path": str(schema_path.resolve()), "schema_hash": schema_hash,
            "input_path": str(input_path.resolve()), "content_hash": _sha256_of_file(input_path),
            "output_dir": str(outdir.resolve()), "strict_columns": bool(args.strict_columns), "encoding_used": used_enc, "note":"column-level errors only"
        }
        Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        # 列崩壊時は終了（品質ゲート対象なら非ゼロ）
        if args.fail_on_invalid:  # 常にFalse（列エラーで即終了させたい場合は拡張可）
            sys.exit(1)
        return

    # チャンク or 一括
    if args.chunksize and args.chunksize > 0:
        if pq is None:
            Path(outdir/"data_profiling.html").write_text("profiling skipped: pyarrow not available", encoding="utf-8")
        writer = None
        total_rows = 0
        invalid_saved = 0
        checks = {}
        first_cols = None
        sample_df = None


        # 実際のチャンク読み（上の防御は破棄して本読み）
        for chunk in pd.read_csv(input_path, encoding=used_enc, chunksize=args.chunksize):
            if first_cols is None: first_cols = list(chunk.columns)
            if sample_df is None: sample_df = chunk.head(min(len(chunk), 50000))
            vdf, err = validate(chunk, schema, strict_columns=False)
            total_rows += int(len(chunk))

            if err is not None and not err.empty and "row" in err:
                # 集計
                for k, cnt in err["type"].value_counts().items():
                    checks[k] = checks.get(k, 0) + int(cnt)
                # invalid抽出（チャンク内rowはローカルindex）
                if invalid_saved < args.invalid-cap and pq is not None:
                    agg = err.dropna(subset=["row"]).groupby("row").apply(
                        lambda g: "; ".join(f"{r.col}:{r.type}" for r in g.itertuples(index=False)),
                        include_groups=False
                    ).rename("errors")
                    invalid = vdf.loc[agg.index].copy()
                    invalid["__errors__"] = agg.values
                    table = pa.Table.from_pandas(invalid, preserve_index=False)
                    if writer is None:
                        writer = pq.ParquetWriter(outdir/"invalid_rows.parquet", table.schema)
                    writer.write_table(table)
                    invalid_saved += len(invalid)

        if writer is not None:
            writer.close()
        else:
            # invalidが無い場合でも空を出力
            if pq is not None:
                pq.write_table(pa.Table.from_pandas(pd.DataFrame(columns=(first_cols or [])+["__errors__"])), outdir/"invalid_rows.parquet")
            else:
                pd.DataFrame(columns=(first_cols or [])+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)

        n_invalid_rows = invalid_saved  # 近似（保存上限に達した場合は下限推定）
        invalid_rate = float(n_invalid_rows/total_rows) if total_rows>0 else 0.0

        # プロファイル（サンプル）
        if args.profile and sample_df is not None:
            try:
                from ydata_profiling import ProfileReport
                ProfileReport(sample_df, title=f"Data Profiling (sample) - {alias}", minimal=True).to_file(outdir/"data_profiling.html")
            except Exception as e:
                Path(outdir/"data_profiling.html").write_text(f"profiling failed: {e}", encoding="utf-8")

        checks_list = [{"name":k,"violations":int(v)} for k,v in sorted(checks.items())]
        summary = {
            "dataset_name": dataset_name, "n_rows": int(total_rows), "n_cols": int(len(first_cols or [])),
            "n_invalid_rows": int(n_invalid_rows), "invalid_rate": invalid_rate, "checks": checks_list,
            "created_at": datetime.utcnow().isoformat()+"Z",
            "schema_path": str(schema_path.resolve()), "schema_hash": schema_hash,
            "input_path": str(input_path.resolve()), "content_hash": _sha256_of_file(input_path),
            "output_dir": str(outdir.resolve()), "strict_columns": bool(args.strict_columns),
            "encoding_used": used_enc, "chunksize": int(args.chunksize), "invalid_cap": int(args.invalid_cap)
        }
        Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        # ゲート
        if (args.fail_on_invalid and summary["n_invalid_rows"]>0) or \
           (args.invalid_rate_threshold is not None and invalid_rate >= args.invalid_rate_threshold):
            sys.exit(1)
        return

    # 一括モード
    df, used_enc = _read_with_encoding_auto(input_path, encoding=args.encoding)
    vdf, err = validate(df, schema, strict_columns=args.strict_columns)

    if err is not None and not err.empty and "row" in err:
        agg = err.dropna(subset=["row"]).groupby("row").apply(
            lambda g: "; ".join(f"{r.col}:{r.type}" for r in g.itertuples(index=False)),
            include_groups=False
        ).rename("errors")
        invalid = vdf.loc[agg.index].copy()
        invalid["__errors__"] = agg.values
        invalid.to_parquet(outdir/"invalid_rows.parquet", index=False)
    else:
        pd.DataFrame(columns=list(df.columns)+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)

    n_rows = int(len(df))
    n_invalid_rows = int(err["row"].nunique()) if err is not None and "row" in err and not err.empty else 0
    invalid_rate = float(n_invalid_rows/n_rows) if n_rows>0 else 0.0

    summary = {
        "dataset_name": dataset_name, "n_rows": n_rows, "n_cols": int(len(df.columns)),
        "n_invalid_rows": n_invalid_rows, "invalid_rate": invalid_rate,
        "checks": (err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records")
                   if err is not None and not err.empty else []),
        "created_at": datetime.utcnow().isoformat()+"Z", "schema_path": str(schema_path.resolve()),
        "schema_hash": schema_hash, "input_path": str(input_path.resolve()),
        "content_hash": _sha256_of_file(input_path), "output_dir": str(outdir.resolve()),
        "strict_columns": bool(args.strict_columns), "encoding_used": used_enc
    }
    Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    if (args.fail_on_invalid and n_invalid_rows>0) or \
       (args.invalid_rate_threshold is not None and invalid_rate >= args.invalid_rate_threshold):
        sys.exit(1)

if __name__=="__main__":
    main()
