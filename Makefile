PREFIX ?= /usr/local
DESTDIR ?=

all: compile 
	@echo "Done"
	@echo "Type: 'make install' now"

compile:
	python -m compileall src

make-install-dirs:
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	mkdir -p $(DESTDIR)$(PREFIX)/share
	mkdir -p $(DESTDIR)$(PREFIX)/share/applications
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp/src

install: make-install-dirs
	install -m 644 src/*.py $(DESTDIR)$(PREFIX)/share/whaawmp/src
	install -m 644 src/*.pyc $(DESTDIR)$(PREFIX)/share/whaawmp/src
	install -m 644 src/*.glade $(DESTDIR)$(PREFIX)/share/whaawmp/src
	install -m 644 whaawmp.desktop $(DESTDIR)$(PREFIX)/share/applications
	install -m 755 whaawmp $(DESTDIR)$(PREFIX)/share/whaawmp
	cd $(DESTDIR)$(PREFIX)/bin && \
	 echo -e \
	  "#!/bin/sh\n" \
	  "exec $(PREFIX)/share/whaawmp/whaawmp \"\$$@\"" \
	  > whaawmp && \
	 chmod 755 whaawmp

uninstall:
	rm -r $(DESTDIR)$(PREFIX)/share/whaawmp
	rm $(DESTDIR)$(PREFIX)/share/applications/whaawmp.desktop
	rm $(DESTDIR)$(PREFIX)/bin/whaawmp
