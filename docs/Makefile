BIN ?= asciidoctor
MAN_OPTS ?= --backend manpage
REVNUMBER := $(shell python3 -c "import tomli; content = tomli.load(open('../pyproject.toml', 'rb')); print(content['project']['version'])")

all: man ref

man: man/racksdb.1

man/%.1: man/%.adoc modules/usage/pages/%.adoc
	$(BIN) $(MAN_OPTS) --attribute mansource="RacksDB v$(REVNUMBER)" $<

ref: modules/db/partials/objects.adoc

modules/db/partials/objects.adoc: ../schema/racksdb.yml
	python3 utils/schema-objs.py > $@

SVGS := $(shell find . -name '*.svg')

.PHONY: optim
optim:
	$(foreach SVG,$(SVGS), \
	  python3 -m scour.scour $(SVG) $(SVG)_optim; mv $(SVG)_optim $(SVG); \
	)
