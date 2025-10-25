.PHONY: help test dq.sample dq.ge dq.chunk-gate dq.chunk-smoke dq.any dq.template dq.scan preproc.run

# ------- 可変パラメータ（.env で上書き可） -------
-include .env

DATA      ?= tests/data/sample.csv
SCHEMA    ?= schema/example_schema.json
CHUNK     ?= 200000
CAP       ?= 50000
RATE      ?= 0.05
DQ_ARGS   ?=
INFER_ROWS?= 10000
DSNAME    ?= sample_timeseries

# Phase3 前処理用
Y_COL     ?= y
UID_COL   ?= unique_id
DS_COL    ?= ds
TRANSFORM ?= log1p
SCALER    ?= standard
OUTDIR_P3 ?= outputs/phase3/$(shell date +%Y%m%d-%H%M%S)

# ------- 共通コマンド -------
DQ_CHUNK_CMD = bin/dq --input $(DATA) --schema $(SCHEMA) \
  --chunksize $(CHUNK) --invalid-cap $(CAP) --invalid-rate-threshold $(RATE)

# ------- ヘルプ -------
help:
	@echo "DATA=$(DATA)"; echo "SCHEMA=$(SCHEMA)"; echo "CHUNK=$(CHUNK) CAP=$(CAP) RATE=$(RATE)"
	@echo "Targets: test | dq.sample | dq.ge | dq.chunk-gate | dq.chunk-smoke | dq.any | dq.template | dq.scan | preproc.run"

# ------- 基本 -------
test:
	pytest -q

dq.sample:
	bin/dq --input $(DATA) --schema $(SCHEMA) --profile --strict-columns

dq.ge:
	bin/gx-run || true
	bin/dq --input $(DATA) --schema $(SCHEMA) --strict-columns

# 厳格ゲート（失敗で落とす）
dq.chunk-gate:
	@$(DQ_CHUNK_CMD)

# スモーク：存在チェック→無ければ静かに skip／あれば実行（失敗は無視）
dq.chunk-smoke:
	@{ test -f "$(DATA)"   || { echo "[smoke] skip: DATA not found: $(DATA)";   exit 0; }; \
	   test -f "$(SCHEMA)" || { echo "[smoke] skip: SCHEMA not found: $(SCHEMA)"; exit 0; }; }
	-@$(MAKE) --no-print-directory -s dq.chunk-gate \
	   DATA="$(DATA)" SCHEMA="$(SCHEMA)" CHUNK="$(CHUNK)" CAP="$(CAP)" RATE="$(RATE)"
	@echo "[smoke] chunk path exercised (DATA=$(DATA), RATE=$(RATE)) — failures ignored"

# 任意引数（例: make dq.any DQ_ARGS="--profile --strict-columns"）
dq.any:
	bin/dq --input $(DATA) --schema $(SCHEMA) $(DQ_ARGS)

# 雛形生成（標準出力 or ファイル： make dq.template DQ_ARGS="--emit-schema-template schema/inferred.json"）
dq.template:
	bin/dq --input $(DATA) --emit-schema-template - --dataset-name $(DSNAME) --infer-rows $(INFER_ROWS) $(DQ_ARGS)

# 1 ショット: 雛形→一括 DQ（推奨は手修正だが、スモークや PoC 用に）
dq.scan:
	@tmp=$$(mktemp); \
	 bin/dq --input $(DATA) --emit-schema-template $$tmp --dataset-name $(DSNAME) --infer-rows $(INFER_ROWS); \
	 bin/dq --input $(DATA) --schema $$tmp --strict-columns || true; \
	 echo "[scan] schema -> $$tmp"

# Phase3 前処理（山括弧不要・OUTDIR 自動）
preproc.run:
	python src/phase3/preproc_runner.py \
	  --input $(DATA) --schema $(SCHEMA) \
	  --y-col $(Y_COL) --unique-id $(UID_COL) --ds-col $(DS_COL) \
	  --transform $(TRANSFORM) --scaler $(SCALER) \
	  --outdir $(OUTDIR_P3)
