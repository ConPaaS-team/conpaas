
all: userguide.pdf adminguide.pdf

%.pdf : %.tex
	pdflatex $<
	pdflatex $<

clean:
	rm -f *.pdf *.out *.aux *.log *~
