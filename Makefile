.PHONY: test dq.sample dq.chunk dq.ge

# parameters
CHUNK ?= 200000
CAP   ?= 50000
RATE  ?= 0.05

test:
	pytest -q

dq.sample:
	bin/dq --input tests/data/sample.csv --schema schema/example_schema.json --profile --strict-columns

dq.ge:
	bin/gx-run || true
	bin/dq --input tests/data/sample.csv --schema schema/example_schema.json --strict-columns

dq.chunk:
	bin/dq --input tests/data/sample.csv --schema schema/example_schema.json --chunksize $(CHUNK) --invalid-cap $(CAP) --invalid-rate-threshold $(RATE)
