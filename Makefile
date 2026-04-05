.PHONY: up down test-mock test-e2e test-alerts test

# Start the full monitoring stack
up:
	docker compose up -d --build

# Stop and remove the stack
down:
	docker compose down -v

# Run mock tests (no network required)
test-mock:
	python -m pytest tests/mock/ -v --tb=short

# Run promtool alert rule tests
test-alerts:
	promtool test rules tests/mock/test_alert_rules.yml

# Run end-to-end tests against live AP
test-e2e:
	python -m pytest tests/e2e/ -v --tb=short -s

# Run all tests (mock first, then e2e)
test: test-mock test-alerts test-e2e
