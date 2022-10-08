BIN ?= asciidoctor
MAN_OPTS ?= --backend manpage
REVNUMBER := $(shell python3 -c 'exec(open("../racksdb/version.py").read()); print(__version__)')

all: man

man: man/racksdb.1

man/%.1: man/%.adoc modules/usage/pages/%.adoc
	$(BIN) $(MAN_OPTS) --attribute mansource="RacksDB v$(REVNUMBER)" $<

SVGS := $(shell find . -name '*.svg')

.PHONY: optim
optim:
	$(foreach SVG,$(SVGS), \
	  python3 -m scour.scour $(SVG) $(SVG)_optim; mv $(SVG)_optim $(SVG); \
	)
