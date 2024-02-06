BIN ?= asciidoctor
MAN_OPTS ?= --backend manpage
REVNUMBER := $(shell python3 -c "import tomli; content = tomli.load(open('../pyproject.toml', 'rb')); print(content['project']['version'])")

all: man ref drawing-ref openapi

man: man/racksdb.1 man/racksdb-web.1

man/%.1: man/%.adoc modules/usage/pages/%.adoc
	$(BIN) $(MAN_OPTS) --attribute mansource="RacksDB v$(REVNUMBER)" $<

ref: modules/db/partials/objects.adoc

modules/db/partials/objects.adoc: ../schemas/racksdb.yml
	python3 utils/schema-objs.py > $@

drawing-ref: modules/usage/partials/drawing-objects.adoc

modules/usage/partials/drawing-objects.adoc: ../schemas/drawings.yml
	python3 utils/drawings-schema-objs.py > $@

openapi: modules/usage/attachments/openapi.yml

modules/usage/attachments/openapi.yml: ../schemas/racksdb.yml ../schemas/drawings.yml
	python3 utils/gen-openapi.py > $@

SVGS := $(shell find . -name '*.svg')

.PHONY: optim
optim:
	$(foreach SVG,$(SVGS), \
	  python3 -m scour.scour $(SVG) $(SVG)_optim; mv $(SVG)_optim $(SVG); \
	)
