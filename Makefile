PREFIX ?= /usr/local

get-args:
	args=
	if [ -n $(DESTDIR) ]; then args="$(args) --root=$(DESTDIR)"; fi
	if [ -n $(PREFIX) ]; then args="$(args) --prefix=$(PREFIX)"; fi
	echo $(args)

all: get-args
	./make.py --root=$(DESTDIR) --prefix=$(PREFIX)

install: get-args
	./make.py install --root=$(DESTDIR) --prefix=$(PREFIX)
