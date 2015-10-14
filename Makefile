PREFIX ?= "/usr/local"
BINDIR ?= "bin"
BINNAME ?= "stlbdr"

install:
	cp stlbdr.py ${PREFIX}/${BINDIR}/${BINNAME}

uninstall:
	${PREFIX}/${BINDIR}/${BINNAME} -v | grep "statusline-builder" && rm ${PREFIX}/${BINDIR}/${BINNAME}
