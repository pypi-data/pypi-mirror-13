# Copyright 2013 Donald Stufft and individual contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

from zerodbext.bindings.crypto_aead_aes256gcm import (
    crypto_aead_aes256gcm_ABYTES, crypto_aead_aes256gcm_KEYBYTES,
    crypto_aead_aes256gcm_NPUBBYTES, crypto_aead_aes256gcm_decrypt,
    crypto_aead_aes256gcm_encrypt, crypto_aead_aes256gcm_is_available,
)

from zerodbext.bindings.sodium_core import sodium_init


__all__ = [
    "crypto_aead_aes256gcm_ABYTES",
    "crypto_aead_aes256gcm_decrypt",
    "crypto_aead_aes256gcm_encrypt",
    "crypto_aead_aes256gcm_is_available",
    "crypto_aead_aes256gcm_KEYBYTES",
    "crypto_aead_aes256gcm_NPUBBYTES",

    "sodium_init",
]

# Initialize Sodium
sodium_init()
