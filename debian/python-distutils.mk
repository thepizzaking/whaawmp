# -*- mode: makefile; coding: utf-8 -*-
# Copyright © 2003 Colin Walters <walters@debian.org>
# Copyright © 2006 Marc Dequènes (Duck) <Duck@DuckCorp.org>
# Copyright © 2003,2006-2010 Jonas Smedegaard <dr@jones.dk>
# Description: manage Python modules using the 'distutils' build system
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

_cdbs_scripts_path ?= /usr/lib/cdbs
_cdbs_rules_path ?= /usr/share/cdbs/1/rules
_cdbs_class_path ?= /usr/share/cdbs/1/class

ifndef _cdbs_class_python_distutils
_cdbs_class_python_distutils = 1

include $(_cdbs_class_path)/python-module.mk$(_cdbs_makefile_suffix)

DEB_PYTHON_SETUP_CMD ?= setup.py
DEB_PYTHON_CLEAN_ARGS ?= -a
DEB_PYTHON_BUILD_ARGS ?= --build-base="$(CURDIR)/$(DEB_BUILDDIR)/build"
DEB_PYTHON_INSTALL_ARGS_ALL ?= --prefix=/usr --no-compile -O0

# DEB_PYTHON_MODULE_PACKAGE is deprecated.
# use DEB_PYTHON_MODULE_PACKAGES instead (since CDBS 0.4.54)
# (warn even when used as-is: plural form breaks use in build targets)
DEB_PYTHON_MODULE_PACKAGE = $(warning Use of DEB_PYTHON_MODULE_PACKAGE is deprecated, please use DEB_PYTHON_MODULE_PACKAGES instead)$(firstword $(filter-out %-doc %-dev %-common, $(DEB_PACKAGES)))

# prepare sanity checks
cdbs_python_packages_pre := $(cdbs_python_arch_packages)$(cdbs_python_indep_packages)
cdbs_python_pkgresolve_check = $(if $(call cdbs_streq,$(cdbs_python_arch_packages)$(cdbs_python_indep_packages),$(cdbs_python_packages_pre)),,$(warning WARNING: Redefining DEB_PYTHON_MODULE_PACKAGES late is currently unsupported: set DEB_PYTHON_MODULE_PACKAGES before including python-distutils.mk))
## TODO: Rephrase when DEB_PYTHON_MODULE_PACKAGES is only expanded inside rules
cdbs_python_pkg_check = $(if $(cdbs_python_arch_packages)$(cdbs_python_indep_packages),,$(warning WARNING: No Python packages found or declared - either rename binary packages or set DEB_PYTHON_MODULE_PACKAGES before including python-distutils.mk))

# Python-related dependencies according to Python policy, appendix A
CDBS_BUILD_DEPENDS_class_python-distutils ?= $(if $(cdbs_python_arch_packages),python-all-dev,python-dev (>= 2.3.5-7)$(cdbs_python_nondefault_version:%=, python%-dev))
CDBS_BUILD_DEPENDS += , $(CDBS_BUILD_DEPENDS_class_python-distutils)

# warn about wrong number of resolved Python packages
CDBS_BUILD_DEPENDS += $(cdbs_python_pkg_check)

# warn early about late changes to DEB_PYTHON_MODULES_PACKAGES
pre-build clean::
	$(cdbs_python_pkgresolve_check)

pre-build::
	mkdir -p debian/python-module-stampdir

# build stage
common-build-arch common-build-indep:: $(addprefix python-build-stamp-, $(cdbs_python_build_versions))

$(patsubst %,build/%,$(cdbs_python_indep_packages) $(cdbs_python_arch_packages)) :: build/% : debian/python-module-stampdir/%

$(patsubst %,debian/python-module-stampdir/%,$(cdbs_python_indep_packages)) :: debian/python-module-stampdir/%:
	cd $(DEB_SRCDIR) && python$(cdbs_python_nondefault_version) $(DEB_PYTHON_SETUP_CMD) build $(DEB_PYTHON_BUILD_ARGS)
	touch $@

$(patsubst %,debian/python-module-stampdir/%,$(cdbs_python_arch_packages)) :: debian/python-module-stampdir/%:
	set -e; for buildver in $(cdbs_python_build_versions); do \
		cd $(CURDIR) && cd $(DEB_SRCDIR) && $(call cdbs_python_binary,python$$buildver) $(DEB_PYTHON_SETUP_CMD) build $(DEB_PYTHON_BUILD_ARGS); \
	done
	touch $@


# install stage
$(patsubst %,install/%,$(cdbs_python_indep_packages)) :: install/%: python-install-py
	cd $(DEB_SRCDIR) && python$(cdbs_python_nondefault_version) $(DEB_PYTHON_SETUP_CMD) install --root=$(cdbs_python_destdir) \
		--install-purelib=/usr/lib/python$(or $(cdbs_python_nondefault_version),$(cdbs_python_current_version))/dist-packages/ $(DEB_PYTHON_INSTALL_ARGS_ALL)

$(patsubst %,install/%,$(cdbs_python_arch_packages)) :: install/%: $(addprefix python-install-, $(cdbs_python_build_versions))
	set -e; for buildver in $(cdbs_python_build_versions); do \
		cd $(CURDIR) && cd $(DEB_SRCDIR) && $(call cdbs_python_binary,python$$buildver) $(DEB_PYTHON_SETUP_CMD) install \
		--root=$(cdbs_python_destdir) --install-purelib=/usr/lib/python$$buildver/dist-packages/ \
		--install-platlib=/usr/lib/python$$buildver/dist-packages/ $(DEB_PYTHON_INSTALL_ARGS_ALL); \
	done

# Deprecated targets.  You should use above targets instead.
$(addprefix python-build-stamp-, $(cdbs_python_build_versions)):
python-install-py $(addprefix python-install-, $(cdbs_python_build_versions)):


# clean stage
clean:: $(patsubst %,python-module-clean/%,$(cdbs_python_indep_packages) $(cdbs_python_arch_packages)) $(addprefix python-clean-, $(cdbs_python_build_versions))

$(patsubst %,python-module-clean/%,$(cdbs_python_indep_packages)) :: python-module-clean/%:
	-cd $(DEB_SRCDIR) && python$(cdbs_python_nondefault_version) $(DEB_PYTHON_SETUP_CMD) clean $(DEB_PYTHON_CLEAN_ARGS)

$(patsubst %,python-module-clean/%,$(cdbs_python_arch_packages)) :: python-module-clean/%:
	-for buildver in $(cdbs_python_build_versions); do \
		cd $(CURDIR) && cd $(DEB_SRCDIR) && $(call cdbs_python_binary,python$$buildver) $(DEB_PYTHON_SETUP_CMD) clean $(DEB_PYTHON_CLEAN_ARGS); \
	done

# Deprecated targets.  You should use above targets instead.
$(addprefix python-clean-, $(cdbs_python_build_versions)):

# cleanup stamp dir
# (dh_clean choke on dirs named stamp, so need to happen before clean::)
clean:: clean-python-distutils
clean-python-distutils::
	rm -rf debian/python-module-stampdir

# Calling setup.py clean may create .pyc files, so we need a final cleanup
# pass here.
# Also clean up .egg-info files generated by setuptools
clean::
	find . -name '*.pyc' -exec rm '{}' ';'
	find . -prune -name '*.egg-info' -exec rm -rf '{}' ';'

.PHONY: $(patsubst %,debian/python-module-stampdir/%,$(cdbs_python_indep_packages) $(cdbs_python_arch_packages))
.PHONY: $(patsubst %,python-module-clean/%,$(cdbs_python_indep_packages) $(cdbs_python_arch_packages))
endif
