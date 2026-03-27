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

clean:
	rm -f vault_state.json backtest_report.csv backtest_chart.png *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true