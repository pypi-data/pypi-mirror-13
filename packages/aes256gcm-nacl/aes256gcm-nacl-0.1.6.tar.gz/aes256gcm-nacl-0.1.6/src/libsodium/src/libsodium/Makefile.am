lib_LTLIBRARIES = \
	libsodium.la

libsodium_la_SOURCES = \
	randombytes/randombytes.c \
	sodium/core.c \
	sodium/runtime.c \
	sodium/utils.c \
	sodium/version.c

if !EMSCRIPTEN

if NATIVECLIENT
libsodium_la_SOURCES += \
	randombytes/nativeclient/randombytes_nativeclient.c
else
libsodium_la_SOURCES += \
    randombytes/sysrandom/randombytes_sysrandom.c
endif

endif

libsodium_la_LDFLAGS = \
	$(AM_LDFLAGS) \
	-export-dynamic \
	-no-undefined \
	$(LIBTOOL_EXTRA_FLAGS)

libsodium_la_CPPFLAGS = \
	$(LTDLINCL) \
	-I$(srcdir)/include/sodium \
	-I$(builddir)/include/sodium

if HAVE_LD_OUTPUT_DEF
libsodium_la_LDFLAGS += -Wl,--output-def,libsodium-$(DLL_VERSION).def
defexecdir = $(bindir)
defexec_DATA = libsodium-$(DLL_VERSION).def
CLEANFILES = $(defexec_DATA)
libsodium-$(DLL_VERSION).def: libsodium.la
endif

SUBDIRS = \
	include

libsodium_la_LIBADD = libaesni.la
noinst_LTLIBRARIES =  libaesni.la

libaesni_la_LDFLAGS = $(libsodium_la_LDFLAGS)
libaesni_la_CPPFLAGS = $(libsodium_la_CPPFLAGS) \
	@CFLAGS_SSSE3@ @CFLAGS_AESNI@ @CFLAGS_PCLMUL@
libaesni_la_SOURCES = \
	crypto_aead/aes256gcm/aesni/aead_aes256gcm_aesni.c

