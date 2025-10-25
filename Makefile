# --- optional overrides from .env ---
-include .env
export DATA SCHEMA CHUNK CAP RATE DQ_ARGS
.DEFAULT_GOAL := dq.help
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
	@echo "Recipes: dq.profile dq.strict dq.profile-strict dq.mlflow dq.mlflow-strict dq.profile-mlflow dq.all"

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

.PHONY: dq.profile dq.strict dq.profile-strict dq.mlflow dq.mlflow-strict dq.profile-mlflow dq.all

# 定形レシピ: dq.any に DQ_ARGS を合成して呼ぶ
dq.profile:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--profile $(DQ_ARGS)"

dq.strict:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--strict-columns $(DQ_ARGS)"

dq.profile-strict:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--profile --strict-columns $(DQ_ARGS)"

dq.mlflow:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--mlflow $(DQ_ARGS)"

dq.mlflow-strict:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--mlflow --strict-columns $(DQ_ARGS)"

dq.profile-mlflow:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--profile --mlflow $(DQ_ARGS)"

dq.all:
	$(MAKE) dq.any DATA="$(DATA)" SCHEMA="$(SCHEMA)" DQ_ARGS="--profile --strict-columns --mlflow $(DQ_ARGS)"

.PHONY: dq.profile-smoke dq.strict-smoke dq.profile-strict-smoke dq.mlflow-smoke dq.mlflow-strict-smoke dq.profile-mlflow-smoke dq.all-smoke dq.schema-template dq.cmd dq.help

# smoke variants: 失敗を無視して静かに通電確認（CI向け）
dq.profile-smoke:
	-@$(MAKE) --no-print-directory -s dq.profile DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.strict-smoke:
	-@$(MAKE) --no-print-directory -s dq.strict DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.profile-strict-smoke:
	-@$(MAKE) --no-print-directory -s dq.profile-strict DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.mlflow-smoke:
	-@$(MAKE) --no-print-directory -s dq.mlflow DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.mlflow-strict-smoke:
	-@$(MAKE) --no-print-directory -s dq.mlflow-strict DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.profile-mlflow-smoke:
	-@$(MAKE) --no-print-directory -s dq.profile-mlflow DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

dq.all-smoke:
	-@$(MAKE) --no-print-directory -s dq.all DATA="$(DATA)" SCHEMA="$(SCHEMA)" || true

# スキーマ雛形生成（DATA から自動で dataset_name を推定）
DATASET_NAME ?= $(notdir $(basename $(DATA)))
TEMPLATE_OUT ?= -
dq.schema-template:
	bin/dq --input $(DATA) --emit-schema-template $(TEMPLATE_OUT) --dataset-name $(DATASET_NAME)

# デバッグ: 解決後コマンドだけ表示
dq.cmd:
	@echo "$(DQ_CHUNK_CMD)"
	@echo "dq.any → bin/dq --input $(DATA) --schema $(SCHEMA) $(DQ_ARGS)"

# 使い方ダンプ

# ---- quick pattern recipes (override only 1 param) ----
# 例: make dq.cap-120000  / make dq.rate-0.15  / make dq.chunk-400000
dq.cap-%:
	@$(MAKE) dq.chunk-gate CAP=$* DATA="$(DATA)" SCHEMA="$(SCHEMA)" RATE="$(RATE)" CHUNK="$(CHUNK)"

dq.rate-%:
	@$(MAKE) dq.chunk-gate RATE=$* DATA="$(DATA)" SCHEMA="$(SCHEMA)" CAP="$(CAP)" CHUNK="$(CHUNK)"

dq.chunk-%:
	@$(MAKE) dq.chunk-gate CHUNK=$* DATA="$(DATA)" SCHEMA="$(SCHEMA)" CAP="$(CAP)" RATE="$(RATE)"

# ---- cleanup ----
.PHONY: dq.clean
dq.clean:
	rm -rf outputs/phase2/* outputs/phase3/* || true

# ---- help に追記（見やすく整列）----
dq.help:
	@echo "DATA=$(DATA)  SCHEMA=$(SCHEMA)"
	@echo "CHUNK=$(CHUNK)  CAP=$(CAP)  RATE=$(RATE)"
	@echo "Recipes : dq.profile dq.strict dq.profile-strict dq.mlflow dq.mlflow-strict dq.profile-mlflow dq.all"
	@echo "Smokes  : dq.profile-smoke dq.strict-smoke dq.profile-strict-smoke dq.mlflow-smoke dq.mlflow-strict-smoke dq.profile-mlflow-smoke dq.all-smoke"
	@echo "Patterns: dq.cap-<N> dq.rate-<R> dq.chunk-<N>"
	@echo "Other   : dq.any dq.chunk-gate dq.chunk-smoke dq.schema-template dq.cmd dq.clean dq.help"
