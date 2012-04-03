
all: userguide.pdf adminguide.pdf newservice.pdf

%.pdf : %.tex
	pdflatex $<
	pdflatex $<

clean:
	rm -f *.pdf *.out *.aux *.log *~
