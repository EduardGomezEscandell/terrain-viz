install-apt-dependencies:
		DEBIAN_FRONTEND=noninteractive \
		    sudo apt update \
		    && sudo apt install -y $(shell cat apt-dependencies.txt)

install-uv:
		sudo snap install astral-uv --classic

install-python-dependencies:
		uv sync

dependencies: install-apt-dependencies install-uv install-python-dependencies

run:
	uv run display