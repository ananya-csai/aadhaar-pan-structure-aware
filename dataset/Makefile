PY=PYTHONPATH=src python3
OUT?=data/v1
CFG?=configs/dataset_v1.yaml

.PHONY: help test dataset report all clean sample
help:
	@echo "make test      - run all unit tests (no images produced)"
	@echo "make dataset   - regenerate the full corpus into $(OUT)"
	@echo "make report    - statistics, leakage audits and paper figures"
	@echo "make all       - test + dataset + report"
	@echo "make sample    - a 6-person corpus into data/sample, for a quick look"
	@echo "make clean     - delete generated data"

test:
	$(PY) tests/test_verhoeff.py
	$(PY) tests/test_validators.py
	$(PY) tests/test_generators.py

dataset:
	$(PY) -m idforge.build --config $(CFG) --out $(OUT)

report:
	$(PY) -m idforge.report --out $(OUT)

sample:
	$(PY) -m idforge.build --out data/sample --n-persons 6
	$(PY) -m idforge.report --out data/sample

all: test dataset report

clean:
	rm -rf data/v1 data/sample
