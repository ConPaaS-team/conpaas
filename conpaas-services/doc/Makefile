
all: userguide.pdf installation.pdf internals.pdf installation.html userguide.html smallclean

%.pdf : %.tex
	pdflatex $<
	pdflatex $<

%.html : %.tex conpaasdoc.tex
	hyperlatex $<
	hyperlatex $<

smallclean:
	rm -f *.out *.aux *.log *.toc *~

clean: smallclean
	rm -f *.pdf *.html

