.PHONY: test dq.sample dq.ge dq.chunk-gate dq.chunk-smoke dq.any

# 可変パラメータ（make ... DATA=... SCHEMA=... で上書きOK）
DATA   ?= tests/data/sample.csv
SCHEMA ?= schema/example_schema.json
CHUNK  ?= 200000
CAP    ?= 50000
RATE   ?= 0.05
DQ_ARGS ?=

# 共通コマンド
DQ_CHUNK_CMD = bin/dq --input $(DATA) --schema $(SCHEMA) \
  --chunksize $(CHUNK) --invalid-cap $(CAP) --invalid-rate-threshold $(RATE)

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

# スモーク（常に成功＆静か）
dq.chunk-smoke:
	-@$(MAKE) --no-print-directory -s dq.chunk-gate \
	  DATA="$(DATA)" SCHEMA="$(SCHEMA)" CHUNK="$(CHUNK)" CAP="$(CAP)" RATE="$(RATE)"
	@echo "[smoke] chunk path exercised (DATA=$(DATA), RATE=$(RATE)) — failures ignored"

# 任意引数を追加して実行（例: make dq.any DQ_ARGS="--profile --strict-columns"）
dq.any:
	bin/dq --input $(DATA) --schema $(SCHEMA) $(DQ_ARGS)
