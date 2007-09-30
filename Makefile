PREFIX ?= /usr/local
DESTDIR ?=


all:
	./make.py --root=$DESTDIR --prefix=$PREFIX

install:
	./make.py install --root=$DESTDIR --prefix=$PREFIX
