IMAGE_NAME = polaris_scan_env
DOCKERFILE = Dockerfile.dev
PWD        = $(shell pwd)

# La uso per eseguire un comando dentro il container e poi lo distrugge
DOCKER_RUN = docker run --rm -v $(PWD):/app -w /app $(IMAGE_NAME)

.PHONY: help build run rebuild clean tests_all tests_itc tests_riscv clean_polaris_objects

.DEFAULT_GOAL := build

## help: Mostra tutti i comandi disponibili con una breve descrizione
help:
	@echo "Comandi disponibili nel Makefile:"
	@echo ""
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' |  sed -e 's/^/ /'

# ==========================================
# DOCKER TARGETS
# ==========================================

## build: Builda l'immagine Docker (default)
build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .

## run: Entra nel container in modalità interattiva (bash) con la repo montata
run:
	docker run -it --rm -v $(PWD):/app -w /app $(IMAGE_NAME) bash

## rebuild: Forza il rebuild dell'immagine Docker da zero (senza cache)
rebuild:
	docker build --no-cache -t $(IMAGE_NAME) -f $(DOCKERFILE) .

## clean: Rimuove l'immagine Docker
clean:
	docker rmi $(IMAGE_NAME) 2>/dev/null || true


# ==========================================
# TESTS (Eseguiti dentro Docker)
# ==========================================

## tests_all: Esegue polaris su tutti i .tcl in Benchmarks/ e verifica l'esito
tests_all:
	$(DOCKER_RUN) pytest test/test_benchmarks.py -v --tb=short

## tests_itc: Esegue solo i benchmark ITC99
tests_itc:
	$(DOCKER_RUN) pytest test/test_benchmarks.py -v --tb=short -k "ITC99"

## tests_riscv: Esegue solo i benchmark RISCV
tests_riscv:
	$(DOCKER_RUN) pytest test/test_benchmarks.py -v --tb=short -k "RISCV"

## test_bXX: Esegue un singolo benchmark ITC99 (es. make test_b01)
test_b%:
	$(DOCKER_RUN) pytest test/test_benchmarks.py -v --tb=short -k "b$*"


# ==========================================
# CLEANUP TARGETS
# ==========================================

## clean_polaris_objects: remove all the generated files (verilog, bench, log, test, vec)
clean_polaris_objects:
	find -type f -name "*chain.v" -delete
	find -type f -name "*.rpt" -delete
