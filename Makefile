.PHONY: test dq.sample dq.chunk dq.ge

test:
\tpytest -q

dq.sample:
\tbin/dq --input tests/data/sample.csv --schema schema/example_schema.json --profile --strict-columns

dq.ge:
\tbin/gx-run || true
\tbin/dq --input tests/data/sample.csv --schema schema/example_schema.json --strict-columns

dq.chunk:
\tCHUNK?=200000; CAP?=50000; RATE?=0.05; \\
\tbin/dq --input tests/data/sample.csv --schema schema/example_schema.json --chunksize $$CHUNK --invalid-cap $$CAP --invalid-rate-threshold $$RATE
