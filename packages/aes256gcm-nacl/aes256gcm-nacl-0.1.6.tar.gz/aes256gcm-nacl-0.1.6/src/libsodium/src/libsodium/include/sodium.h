
#ifndef sodium_H
#define sodium_H

#include "sodium/core.h"
#include "sodium/crypto_aead_aes256gcm.h"
#include "sodium/randombytes.h"
#ifdef __native_client__
# include "sodium/randombytes_nativeclient.h"
#endif
#include "sodium/randombytes_sysrandom.h"
#include "sodium/runtime.h"
#include "sodium/utils.h"
#include "sodium/version.h"

#endif
