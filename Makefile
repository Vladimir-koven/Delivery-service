# ===============================
# Настройки проекта
# ===============================
PY_SRCS=src
RADON_MIN_MI=65

.PHONY: help install lint fmt type security cc mi hal raw check fix clean

help:
	@echo "Available targets:"
	@echo "  install   - install dependencies"
	@echo "  lint      - ruff check --fix"
	@echo "  fmt       - ruff format"
	@echo "  type      - mypy"
	@echo "  security  - bandit"
	@echo "  cc        - radon cyclomatic complexity + gate"
	@echo "  mi        - radon maintainability index + gate"
	@echo "  hal       - radon Halstead"
	@echo "  raw       - radon raw metrics"
	@echo "  check     - run all checks (no fixes)"
	@echo "  fix       - auto-fix (lint + fmt)"
	@echo "  clean     - remove caches"

install:
	poetry install

# ===============================
# Ruff
# ===============================
lint:
	poetry run ruff check $(PY_SRCS) --fix

fmt:
	poetry run ruff format $(PY_SRCS)

# ===============================
# Mypy
# ===============================
type:
	poetry run mypy $(PY_SRCS)

# ===============================
# Bandit
# ===============================
security:
	poetry run bandit -c pyproject.toml -r $(PY_SRCS) -ll

# ===============================
# Radon
# ===============================
cc:
	poetry run radon cc -s -a $(PY_SRCS)
	@poetry run python -c "import subprocess,sys; out=subprocess.run(['radon','cc','-s','$(PY_SRCS)'],capture_output=True,text=True).stdout; bad=[l for l in out.splitlines() if ' E ' in l or ' F ' in l]; (print('[FAIL] Radon CC: E/F found'), sys.exit(1)) if bad else print('[OK] Radon CC: no E/F')"

mi:
	poetry run radon mi -s $(PY_SRCS)
	@poetry run python -c "import subprocess,re,sys; out=subprocess.run(['radon','mi','-s','$(PY_SRCS)'],capture_output=True,text=True).stdout; bad=[l for l in out.splitlines() if (m:=re.search(r'([0-9]+(?:\.[0-9]+)?)', l.split(' - ')[-1])) and float(m.group(1)) < $(RADON_MIN_MI)]; (print('[FAIL] Radon MI: < $(RADON_MIN_MI)'), sys.exit(1)) if bad else print('[OK] Radon MI: all >= $(RADON_MIN_MI)')"

hal:
	poetry run radon hal $(PY_SRCS)

raw:
	poetry run radon raw $(PY_SRCS)

# ===============================
# Комплексные цели
# ===============================
check:
	poetry run ruff check $(PY_SRCS)
	poetry run ruff format --check $(PY_SRCS)
	poetry run mypy $(PY_SRCS)
	poetry run bandit -c pyproject.toml -r $(PY_SRCS) -ll

fix: lint fmt

clean:
	poetry run python -c "import shutil,pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	poetry run python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.ruff_cache','.mypy_cache']]"