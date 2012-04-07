
all: userguide.pdf installation.pdf internals.pdf

%.pdf : %.tex
	pdflatex $<
	pdflatex $<

clean:
	rm -f *.pdf *.out *.aux *.log *~
