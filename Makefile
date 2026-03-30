.PHONY: install lint test run-mock run-live plot clean

install:
	pip install -r requirements.txt -r requirements-dev.txt

lint:
	ruff check . --fix
	python -m mypy --strict --follow-imports=skip demo_automated_vault.py

test:
	pytest tests/test_vault.py -v

run-mock:
	python demo_automated_vault.py

run-live:
	python demo_automated_vault.py --live

plot:
	python plot_backtest.py

# ==================== CLEAN (Python-powered for Cross-Platform safety) ====================

# Manual Windows Reset (Run this in PowerShell if 'make clean' isn't used):
# Set-Content -Path vault_state.json -Value '{"has_eth": false, "last_buy_price": 0.0, "total_profit": 0.0, "cycles_held": 0}' -Encoding Ascii; Remove-Item backtest_report.csv, backtest_chart.png, *.pyc -Force -ErrorAction SilentlyContinue

clean:
	@echo "Cleaning up project files..."
	@python -c "import os, glob, json; \
		data = {'has_eth': False, 'last_buy_price': 0.0, 'total_profit': 0.0, 'cycles_held': 0}; \
		open('vault_state.json', 'w').write(json.dumps(data)); \
		[os.remove(f) for f in ['backtest_report.csv', 'backtest_chart.png'] if os.path.exists(f)]; \
		[os.remove(f) for f in glob.glob('*.pyc')];"
	@python -c "import shutil, os; \
		[shutil.rmtree(p) for p in ['.pytest_cache', '__pycache__'] if os.path.exists(p)]" || true