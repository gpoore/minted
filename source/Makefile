TEXFLAGS = -e '$$pdflatex=q/pdflatex %O -shell-escape %S/' -pdf
LATEXMK = latexmk

PACKAGE = minted.dtx \
		  minted.ins \
		  minted.pdf \
		  README \
		  Makefile

.PHONY: minted all doc dist clean cleanall

minted: minted.sty

doc: minted.pdf

all: minted doc

minted.sty: minted.ins minted.dtx
	tex minted.ins

minted.pdf: minted.sty minted.gls minted.dtx
	$(LATEXMK) $(TEXFLAGS) minted.dtx

minted.gls: minted.glo
	makeindex -s gglo.ist -o minted.gls minted.glo

minted.glo: minted.dtx minted.sty
	$(LATEXMK) $(TEXFLAGS) minted.dtx

dist: $(PACKAGE)
	@$(RM) minted.zip
	@zip minted-$(shell grep '^\\ProvidesPackage' < minted.sty | grep -o '\<v[[:digit:]]*\.[[:digit:]]*\>').zip $(PACKAGE)

clean:
	@$(RM) *.aux *.log *.out *.toc *.fdb_latexmk *.ilg *.glo *.gls *.lol

cleanall: clean
	@$(RM) minted.sty minted.zip
