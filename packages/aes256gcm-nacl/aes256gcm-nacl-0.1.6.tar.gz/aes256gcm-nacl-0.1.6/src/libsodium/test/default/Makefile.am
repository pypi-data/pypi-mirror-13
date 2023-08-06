
EXTRA_DIST = \
	cmptest.h \
	wintest.bat \
	pre.js.inc \
	aead_aes256gcm.exp \
	sodium_version.exp 

DISTCLEANFILES = \
	aead_aes256gcm.res \
	sodium_version.res 

if NATIVECLIENT
CLEANFILES = \
	aead_aes256gcm.final \
	sodium_version.final \
	aead_aes256gcm.nexe \
	sodium_version.nexe 
endif

AM_CPPFLAGS = \
	-DTEST_SRCDIR=\"@srcdir@\" \
	-I$(top_srcdir)/src/libsodium/include \
	-I$(top_srcdir)/src/libsodium/include/sodium \
	-I$(top_builddir)/src/libsodium/include \
	-I$(top_builddir)/src/libsodium/include/sodium \
	-I$(top_srcdir)/test/quirks

AM_LDFLAGS = @TEST_LDFLAGS@

TESTS_TARGETS = \
	aead_aes256gcm \
	sodium_version 


check_PROGRAMS = $(TESTS_TARGETS)

TESTS = $(TESTS_TARGETS)

TESTS_LDADD = \
	${top_builddir}/src/libsodium/libsodium.la

aead_aes256gcm_SOURCE                 = cmptest.h aead_aes256gcm.c
aead_aes256gcm_LDADD                  = $(TESTS_LDADD)

sodium_version_SOURCE     = cmptest.h sodium_version.c
sodium_version_LDADD      = $(TESTS_LDADD)

verify: check
