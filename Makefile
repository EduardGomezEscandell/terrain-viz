PYTHON := .venv/bin/python3

.PHONY: install-apt-dependencies
install-apt-dependencies:
	DEBIAN_FRONTEND=noninteractive \
		sudo apt update \
		&& sudo apt install -y $(shell cat apt-dependencies.txt)

.PHONY: install-uv
install-uv:
	sudo snap install astral-uv --classic

.PHONY: install-python-dependencies
install-python-dependencies:
	uv sync --reinstall-package elevation

.PHONY: dependencies
dependencies: install-apt-dependencies install-uv install-python-dependencies

.PHONY: clear
clear:
	rm -rf .venv              || true
	rm -rf elevation.egg-info || true
	rm -rf out                || true

.PHONY: run
run:
	uv run display