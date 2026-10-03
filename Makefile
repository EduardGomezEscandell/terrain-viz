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
	[ -f compile_commands.json ] || ln -s build/compile_commands.json compile_commands.json

.PHONY: dependencies
dependencies: install-apt-dependencies install-uv install-python-dependencies

.PHONY: clear
clear:
	rm -rf .venv                 || true
	rm -rf elevation.egg-info    || true
	rm -rf out                   || true
	rm -rf build                 || true
	rm -rf compile_commands.json || true

.PHONY: run
run:
	uv run display