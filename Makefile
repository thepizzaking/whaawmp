PREFIX ?= /usr/local
DESTDIR ?=

all: compile compile-po
	@echo "Done"
	@echo "Type: 'make install' now"

compile:
	python -m compileall src

compile-po:
	./po/potool.py compile

make-install-dirs:
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	mkdir -p $(DESTDIR)$(PREFIX)/share
	mkdir -p $(DESTDIR)$(PREFIX)/share/applications
	mkdir -p $(DESTDIR)$(PREFIX)/share/thumbnailers
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp/images
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp/src
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp/src/common
	mkdir -p $(DESTDIR)$(PREFIX)/share/whaawmp/src/gui
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale

install: make-install-dirs
	install -m 644 whaawmp.desktop $(DESTDIR)$(PREFIX)/share/applications
	install -m 644 images/*.png $(DESTDIR)$(PREFIX)/share/whaawmp/images
	install -m 644 src/*.py $(DESTDIR)$(PREFIX)/share/whaawmp/src
	install -m 644 src/*.pyc $(DESTDIR)$(PREFIX)/share/whaawmp/src
	install -m 644 src/common/*.py $(DESTDIR)$(PREFIX)/share/whaawmp/src/common
	install -m 644 src/common/*.pyc $(DESTDIR)$(PREFIX)/share/whaawmp/src/common
	install -m 644 src/gui/*.py $(DESTDIR)$(PREFIX)/share/whaawmp/src/gui
	install -m 644 src/gui/*.pyc $(DESTDIR)$(PREFIX)/share/whaawmp/src/gui
	install -m 644 src/gui/*.glade $(DESTDIR)$(PREFIX)/share/whaawmp/src/gui
	install -m 755 whaawmp $(DESTDIR)$(PREFIX)/share/whaawmp
	install -m 644 whaaw-thumbnailer.desktop $(DESTDIR)$(PREFIX)/share/thumbnailers
	install -m 755 whaaw-thumbnailer $(DESTDIR)$(PREFIX)/share/whaawmp
	for x in `find po -name whaawmp.mo`; do \
	 install -D -m 644 $$x \
	 `echo $$x | sed "s|^po|$(DESTDIR)$(PREFIX)/share/locale|"`; \
	 done
	cd $(DESTDIR)$(PREFIX)/bin && \
	 echo -e \
	  "#!/bin/sh\n" \
	  "exec $(PREFIX)/share/whaawmp/whaawmp \"\$$@\"" \
	  > whaawmp && \
	 chmod 755 whaawmp && \
	 echo -e \
	  "#!/bin/sh\n" \
	  "exec $(PREFIX)/share/whaawmp/whaaw-thumbnailer \"\$$@\"" \
	  > whaaw-thumbnailer && \
	 chmod 755 whaaw-thumbnailer

uninstall:
	rm -r $(DESTDIR)$(PREFIX)/share/whaawmp
	rm $(DESTDIR)$(PREFIX)/share/applications/whaawmp.desktop
	rm $(DESTDIR)$(PREFIX)/bin/whaawmp
	rm $(DESTDIR)$(PREFIX)/share/thumbnailers/whaaw-thumbnailer.desktop
	rm $(DESTDIR)$(PREFIX)/bin/whaaw-thumbnailer
