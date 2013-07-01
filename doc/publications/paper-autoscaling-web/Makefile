PRJ=socc2013

STYS := $(shell find . $(COMMON) -name '*.sty')
BIBS := $(shell find . $(COMMON) -name '*.bib')
TEXS := $(shell find . $(COMMON) -name '*.tex')
JPGS := $(shell find . $(COMMON) -name '*.jpg')


$(PRJ).pdf:$(TEXS) $(BIBS) $(STYS) $(JPGS) Makefile
	pdflatex $(PRJ).tex || (rm $(PRJ).pdf && false)
	bibtex   $(PRJ).aux 
	pdflatex $(PRJ).tex 
	pdflatex $(PRJ).tex 

pdfview: $(PRJ).pdf
	evince $(PRJ).pdf &

clean:
	rm -f $(PRJ).pdf *.out *.blg *.bbl *.lof *.lot *.toc *.idx *.nav *.snm *.aux *.ist *.log *.par *.cov *.acn *.acr *.alg *.glg *.gls *.glo *.xdy *.alg
