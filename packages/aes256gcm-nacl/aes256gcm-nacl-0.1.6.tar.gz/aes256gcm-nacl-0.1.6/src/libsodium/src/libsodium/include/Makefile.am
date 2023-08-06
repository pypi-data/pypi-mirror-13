
SODIUM_EXPORT = \
	sodium.h \
	sodium/core.h \
	sodium/crypto_aead_aes256gcm.h \
	sodium/crypto_int32.h \
	sodium/crypto_int64.h \
	sodium/crypto_uint16.h \
	sodium/crypto_uint32.h \
	sodium/crypto_uint64.h \
	sodium/crypto_uint8.h \
	sodium/export.h \
	sodium/randombytes.h \
	sodium/randombytes_sysrandom.h \
	sodium/runtime.h \
	sodium/utils.h

if NATIVECLIENT
SODIUM_EXPORT += \
	sodium/randombytes_nativeclient.h
endif

EXTRA_SRC = $(SODIUM_EXPORT) \
	sodium/version.h.in

nobase_include_HEADERS = $(SODIUM_EXPORT)

nobase_nodist_include_HEADERS = \
	sodium/version.h
