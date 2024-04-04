BIN ?= asciidoctor
MAN_OPTS ?= --backend manpage
REVNUMBER := $(shell python3 -c "import tomli; content = tomli.load(open('../pyproject.toml', 'rb')); print(content['project']['version'])")

SVGS := $(shell find . -name '*.svg')

.PHONY: optim
optim:
	$(foreach SVG,$(SVGS), \
	  python3 -m scour.scour $(SVG) $(SVG)_optim; mv $(SVG)_optim $(SVG); \
	)
