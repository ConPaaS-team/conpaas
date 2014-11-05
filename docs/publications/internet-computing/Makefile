# Makefile for large latex project.
#
#

MASTER = paper

# Source files
SOURCES = $(wildcard graphs/*.tex)
#GRAPHS = $(wildcard graphs/*.ps)
FIGURES = $(wildcard figs/*.eps figs/*.pdf)
REFS = $(wildcard *.bib)

# Commands

# Define PREFIX for special locations
ifeq (Darwin,$(shell uname -s))
PREFIX=/opt/local/bin/
else
# Otherwise, assume in PATH already
PREFIX=
endif

BIBTEX=$(PREFIX)bibtex -terse -min-crossrefs=1000
LATEX=$(PREFIX)latex -output-format=dvi
PDFLATEX=$(PREFIX)latex -output-format=pdf
DVIPS=$(PREFIX)dvips
PERL=perl
SPELL=aspell -t -d en_GB -c

# MAKEGLOSSARY=makeindex
# $(MAKEGLOSSARY) -s $*.ist -t $*.glg -o $*.gls main.glo

# Add pdf and others to list of suffixes
.SUFFIXES: .pdf .ps .dvi
.PHONY : default dvi ps pdf all force clean show pdfview spell

# Default phony targets
default: pdf
dvi : $(MASTER).dvi
ps : $(MASTER).ps
pdf : $(MASTER).pdf
all: pdf

# Command to bibtex sources as needed. The initial conditional checks
# to see whether any bibdata files were referenced. Then,
#    1) The bibdata references are extracted and separated by "perl";
#    2) Using "xargs" each bibdata is compared against the $(MASTER).bbl with
#       "test" to see if any are newer (or if the $(MASTER).bbl doesn't 
#       exist yet; and
#    3) If any bibdata exists and is newer or if there were any
#       undefined references, "bibtex" and "latex" are
#       executed to update the .bbl file.
# The gigantic if statement thus attempts to run bibtex only if the
# .bib sources are changed (case 1) or new references are added (case
# 2).
define bibtex-as-needed 
{ MAIN=$(basename $@) ; \
  if { grep -q "bibdata" $$MAIN.aux ; } ; then \
     for bibdata in `$(PERL) -ane ' if ( /bibdata\{([^}]+)\}/ ) { foreach $$bib (split(",",$$1)) { chomp($$bib); print "$$bib\n" ; } }' $$MAIN.aux` ; do \
	if ( ! test -r $$MAIN.bbl ) || ( test $$MAIN.bbl -nt $$bibdata.bib ) ; then \
           $(BIBTEX) $$MAIN ; break ; \
        fi ; \
     done ; \
     $(LATEX_COMMAND) $$MAIN ; \
  elif { grep -qi "there were undefined references" $$MAIN.log ; } \
       || { grep -qi 'citation.*undefined' $$MAIN.log ; } ; then \
    $(BIBTEX) $$MAIN ; \
    $(LATEX_COMMAND) $$MAIN ; \
  fi ; }
endef

# Command to re-run latex as needed. We only want to re-run latex if
# it may help---not because there was simply an error! At present, we
# re-run to update cross-references only.
# 
define latex-as-needed
{	while grep -qi "rerun to get cross-references right" $(basename $@).log ; do \
  $(LATEX_COMMAND) $(basename $@) ; done ; }
endef

#
#  Rulez!
#
%.ps:%.dvi
	$(DVIPS) -Ppdf -G0 $< -o $@

# In this rule, we initially run latex to update the .aux file, then
# fix things up as needed.
%.dvi : LATEX_COMMAND=$(LATEX)
$(MASTER).dvi : $(SOURCES) $(GRAPHS) $(REFS) $(FIGURES) Makefile
	@$(LATEX_COMMAND) $(basename $@)
	@$(bibtex-as-needed)
	@$(latex-as-needed)

# In this rule, we initially run latex to update the .aux file, then
# fix things up as needed.
%.pdf : LATEX_COMMAND=$(PDFLATEX)
$(MASTER).pdf : $(SOURCES) $(GRAPHS) $(REFS) $(FIGURES) Makefile
	@$(LATEX_COMMAND) $(basename $@)
	$(bibtex-as-needed)
	@$(latex-as-needed)

%.tpm: %.ps
	ps2pdf -dMaxSubsetPct=100 -dSubsetFonts=true -dEmbedAllFonts=true $<
	thumbpdf --modes ps2pdf $*

clean:
	-rm -f *.log *.ps *.dvi *.pdf *.aux *.bbl *.blg *.tpm *.out

show:
	@case "`uname -s`" in Darwin) open $(MASTER).pdf & ;; *) xpdf $(MASTER).pdf & ;; esac

force: clean
	$(MAKE)

pdfview: pdf
	evince $(MASTER).pdf &

spell:
	for file in $(SOURCES) ; do $(SPELL) $$file ; done


count: pdf
	pdftotext $(MASTER).pdf - | wc 

