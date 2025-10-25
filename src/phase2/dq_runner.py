#!/usr/bin/env python
import argparse, json, re, sys, hashlib, io, os
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

    # 未知列/必須列（行検証前に）
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

def _infer_dtype_and_meta(name:str, s:pd.Series, *, thr:float=0.6):
    """カラムごとの dtype/required/allowed/range を推定"""
    col = s.dropna()
    n = len(s)
    # bool（緩め）
    _lb = col.astype(str).str.lower()
    is_bool = (_lb.isin(["true","false","t","f","0","1","yes","no"]).mean() >= thr)
    if is_bool:
        return {"name":name,"dtype":"bool","required": float(s.isna().mean())==0.0}

    # 数値
    nums = pd.to_numeric(col, errors="coerce")
    rate_num = nums.notna().mean() if len(col)>0 else 0.0
    if rate_num >= thr:
        is_floatish = (nums.round(0) != nums).any()
        rng = {"min": float(nums.min()) if len(nums)>0 else None,
               "max": float(nums.max()) if len(nums)>0 else None}
        meta = {"name":name,"dtype": "float" if is_floatish else "int",
                "required": float(s.isna().mean())==0.0,
                "range": rng}
        return meta

    # 日付（代表パターン → 汎用）
    patterns = ["%Y-%m-%d","%Y/%m/%d","%Y-%m-%d %H:%M:%S","%Y/%m/%d %H:%M:%S", None]
    for fmt in patterns:
        parsed = pd.to_datetime(col, format=fmt, errors="coerce") if fmt else pd.to_datetime(col, errors="coerce", infer_datetime_format=True)
        rate_dt = parsed.notna().mean() if len(col)>0 else 0.0
        if rate_dt >= thr:
            meta = {"name":name,"dtype":"datetime","required": float(s.isna().mean())==0.0}
            if fmt: meta["datetime_format"] = fmt
            return meta

    # 文字列 + allowed 推定（低カーディナリティなら）
    nunique = int(col.astype(str).nunique())
    allow = None
    if n>0 and (nunique <= 50) and (nunique/ max(n,1) <= 0.2):
        allow = sorted(col.astype(str).unique().tolist())
    meta = {"name":name,"dtype":"string","required": float(s.isna().mean())==0.0}
    if allow is not None:
        meta["allowed"] = allow
    return meta

def _suggest_primary_keys(df:pd.DataFrame):
    cand = []
    # よくある "unique_id"+"ds"
    if set(["unique_id","ds"]).issubset(df.columns):
        if not df.duplicated(subset=["unique_id","ds"]).any():
            return ["unique_id","ds"]
    # 単独ユニーク
    for c in df.columns:
        if not df.duplicated(subset=[c]).any():
            cand.append([c])
    return cand[0] if cand else []

def _emit_schema_template(input_path:Path, out_path:str, encoding:str, dataset_name:str, infer_rows:int=10000):
    df, used = _read_with_encoding_auto(input_path, encoding=encoding, nrows=infer_rows)
    cols=[]
    for name in df.columns:
        meta = _infer_dtype_and_meta(name, df[name], thr=0.6)
        cols.append(meta)
    pk = _suggest_primary_keys(df)
    schema = {"dataset_name": dataset_name or input_path.stem, "primary_keys": pk, "columns": cols}
    text = json.dumps(schema, ensure_ascii=False, indent=2)
    if out_path == "-":
        sys.stdout.write(text)
    else:
        op = Path(out_path); op.parent.mkdir(parents=True, exist_ok=True); op.write_text(text, encoding="utf-8")
    return used

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="CSV path (.csv[.gz|.bz2|.zip])")
    ap.add_argument("--schema", help="Schema JSON path")
    ap.add_argument("--outdir", default=None, help="Output dir (default: outputs/phase2/<alias>)")
    ap.add_argument("--profile", action="store_true", help="Emit data_profiling.html (lightweight)")
    ap.add_argument("--fail-on-invalid", dest="fail_on_invalid", action="store_true", help="Exit 1 when invalid rows exist")
    ap.add_argument("--strict-columns", action="store_true", help="Fail when unknown columns exist")
    ap.add_argument("--encoding", default="utf-8", help="CSV encoding or 'auto'")
    ap.add_argument("--chunksize", type=int, default=0, help="Row chunksize for streaming validation (0=disabled)")
    ap.add_argument("--invalid-cap", dest="invalid_cap", type=int, default=10000, help="Max invalid rows to save")
    ap.add_argument("--invalid-rate-threshold", dest="invalid_rate_threshold", type=float, default=None, help="Exit nonzero if invalid_rate >= threshold")
    # 新機能
    ap.add_argument("--emit-schema-template", dest="emit_schema_template", default=None, help="Write inferred schema JSON path or '-' for stdout, then exit")
    ap.add_argument("--dataset-name", dest="dataset_name", default=None, help="dataset_name for schema template")
    ap.add_argument("--infer-rows", dest="infer_rows", type=int, default=10000, help="Rows to sample for schema inference")
    ap.add_argument("--mlflow", action="store_true", help="(optional) Log metrics/artifacts to MLflow if available")
    args = ap.parse_args()

    # 1) 雛形生成
    if args.emit_schema_template:
        if not args.input:
            print("[dq] --emit-schema-template には --input が必要です。", file=sys.stderr); sys.exit(2)
        ip = Path(args.input)
        if not ip.exists():
            print(f"[dq] 入力ファイルが見つかりません: {ip}", file=sys.stderr); sys.exit(2)
        used = _emit_schema_template(ip, args.emit_schema_template, args.encoding, args.dataset_name or (ip.stem if ip else "dataset"), args.infer_rows)
        return 0

    # 2) 入力/スキーマ存在チェック
    if not args.input or not args.schema:
        print("[dq] 必須引数 --input と --schema を指定してください。", file=sys.stderr); sys.exit(2)
    input_path = Path(args.input)
    schema_path = Path(args.schema)
    if not input_path.exists():
        print(f"[dq] 入力ファイルが見つかりません: {input_path}", file=sys.stderr); sys.exit(2)
    if not schema_path.exists():
        print(f"[dq] スキーマが見つかりません: {schema_path}", file=sys.stderr); sys.exit(2)

    schema_text = schema_path.read_text(encoding="utf-8")
    schema = json.loads(schema_text)
    schema_hash = _sha256_of_text(schema_text)
    dataset_name = schema.get("dataset_name", args.dataset_name or "dataset")
    alias = _alias(dataset_name)
    outdir = Path(args.outdir) if args.outdir else Path("outputs/phase2")/alias
    outdir.mkdir(parents=True, exist_ok=True)

    # 列の体裁だけ先行チェック
    header_df, used_enc = _read_with_encoding_auto(input_path, nrows=0, encoding=args.encoding)
    _, early_err = validate(header_df, schema, strict_columns=args.strict_columns)
    if early_err is not None and not early_err.empty:
        early_err.to_csv(outdir/"schema_errors.csv", index=False)
        n_rows = int(pd.read_csv(input_path, encoding=used_enc, usecols=[0]).shape[0]) if header_df is not None else 0
        summary = {
            "dataset_name": dataset_name, "n_rows": n_rows, "n_cols": int(len(header_df.columns)),
            "n_invalid_rows": 0, "invalid_rate": 0.0,
            "checks": early_err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records"),
            "created_at": datetime.utcnow().isoformat()+"Z", "schema_path": str(schema_path.resolve()), "schema_hash": schema_hash,
            "input_path": str(input_path.resolve()), "content_hash": _sha256_of_file(input_path),
            "output_dir": str(outdir.resolve()), "strict_columns": bool(args.strict_columns),
            "encoding_used": used_enc, "note":"column-level errors only", "invalid_capped": False
        }
        Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0

    # --- 本検証：チャンク or 一括 ---
    n_rows = 0
    n_invalid_rows = 0
    invalid_rate = 0.0
    invalid_capped = False

    if args.chunksize and args.chunksize > 0:
        writer = None
        checks = {}
        first_cols = None
        sample_df = None
        invalid_saved = 0

        for chunk in pd.read_csv(input_path, encoding=used_enc, chunksize=args.chunksize):
            if first_cols is None: first_cols = list(chunk.columns)
            if sample_df is None: sample_df = chunk.head(min(len(chunk), 50000))
            vdf, err = validate(chunk, schema, strict_columns=False)
            n_rows += int(len(chunk))
            if err is not None and not err.empty and "row" in err:
                for k, cnt in err["type"].value_counts().items():
                    checks[k] = checks.get(k, 0) + int(cnt)
                if pq is not None and invalid_saved < args.invalid_cap:
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
        if writer is not None: writer.close()
        if invalid_saved == 0:
            if pq is not None:
                pq.write_table(pa.Table.from_pandas(pd.DataFrame(columns=(first_cols or [])+["__errors__"])), outdir/"invalid_rows.parquet")
            else:
                pd.DataFrame(columns=(first_cols or [])+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)

        n_invalid_rows = int(invalid_saved)
        invalid_capped = bool(invalid_saved >= args.invalid_cap)
        invalid_rate = float(n_invalid_rows/n_rows) if n_rows>0 else 0.0

        if args.profile and sample_df is not None:
            try:
                from ydata_profiling import ProfileReport
                ProfileReport(sample_df, title=f"Data Profiling (sample) - {alias}", minimal=True).to_file(outdir/"data_profiling.html")
            except Exception as e:
                Path(outdir/"data_profiling.html").write_text(f"profiling failed: {e}", encoding="utf-8")

        checks_list = [{"name":k,"violations":int(v)} for k,v in sorted(checks.items())]
        summary = {
            "dataset_name": dataset_name, "n_rows": int(n_rows), "n_cols": int(len(first_cols or [])),
            "n_invalid_rows": int(n_invalid_rows), "invalid_rate": invalid_rate, "invalid_capped": invalid_capped,
            "checks": checks_list, "created_at": datetime.utcnow().isoformat()+"Z",
            "schema_path": str(schema_path.resolve()), "schema_hash": schema_hash,
            "input_path": str(input_path.resolve()), "content_hash": _sha256_of_file(input_path),
            "output_dir": str(outdir.resolve()), "strict_columns": bool(args.strict_columns),
            "encoding_used": used_enc, "chunksize": int(args.chunksize), "invalid_cap": int(args.invalid_cap)
        }
        Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    else:
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
            n_invalid_rows = int(len(invalid))
        else:
            pd.DataFrame(columns=list(df.columns)+["__errors__"]).to_parquet(outdir/"invalid_rows.parquet", index=False)
            n_invalid_rows = 0
        n_rows = int(len(df))
        invalid_rate = float(n_invalid_rows/n_rows) if n_rows>0 else 0.0
        summary = {
            "dataset_name": dataset_name, "n_rows": n_rows, "n_cols": int(len(df.columns)),
            "n_invalid_rows": n_invalid_rows, "invalid_rate": invalid_rate, "invalid_capped": False,
            "checks": (err["type"].value_counts().rename_axis("name").reset_index(name="violations").to_dict(orient="records")
                       if err is not None and not err.empty else []),
            "created_at": datetime.utcnow().isoformat()+"Z", "schema_path": str(schema_path.resolve()),
            "schema_hash": schema_hash, "input_path": str(input_path.resolve()),
            "content_hash": _sha256_of_file(input_path), "output_dir": str(outdir.resolve()),
            "strict_columns": bool(args.strict_columns), "encoding_used": used_enc
        }
        Path(outdir/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # MLflow（任意）
    if args.mlflow:
        try:
            import mlflow
            mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME","phase2_dq"))
            with mlflow.start_run(run_name=alias):
                mlflow.log_param("dataset_name", dataset_name)
                mlflow.log_param("schema_hash", schema_hash)
                mlflow.log_param("input_path", str(input_path))
                mlflow.log_metric("n_rows", n_rows)
                mlflow.log_metric("n_invalid_rows", n_invalid_rows)
                mlflow.log_metric("invalid_rate", invalid_rate)
                mlflow.log_artifact(outdir/"summary.json", artifact_path="dq")
                ip = outdir/"invalid_rows.parquet"
                if ip.exists(): mlflow.log_artifact(ip, artifact_path="dq")
                hp = outdir/"data_profiling.html"
                if hp.exists(): mlflow.log_artifact(hp, artifact_path="dq")
        except Exception as e:
            Path(outdir/"mlflow.log.txt").write_text(f"mlflow skipped or failed: {e}", encoding="utf-8")

    # ゲート
    if (args.fail_on_invalid and n_invalid_rows>0) or \
       (args.invalid_rate_threshold is not None and invalid_rate >= args.invalid_rate_threshold):
        sys.exit(1)
    return 0

if __name__=="__main__":
    sys.exit(main())
