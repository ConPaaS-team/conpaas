
all: userguide.pdf installation.pdf internals.pdf installation.html userguide.html

%.pdf : %.tex
	pdflatex $<
	pdflatex $<

%.html : %.tex conpaasdoc.tex
	hyperlatex $<
	hyperlatex $<

clean:
	rm -f *.pdf *.out *.aux *.log *.toc *.html *~
