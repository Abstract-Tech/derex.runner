# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -W
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = derex.runner
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile apidoc

apidoc:
	rm -rf derex.*.rst modules.rst


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile apidoc
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
