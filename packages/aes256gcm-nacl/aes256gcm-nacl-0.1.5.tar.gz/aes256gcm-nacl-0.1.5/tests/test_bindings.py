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

from binascii import hexlify

import pytest

from zerodbext.aead import bindings as c
from nacl.exceptions import CryptoError


def tohex(b):
    return hexlify(b).decode("ascii")


def test_aes256gcm():
    key = b"\x00" * c.crypto_aead_aes256gcm_KEYBYTES
    msg = b"message"
    nonce = b"\x01" * c.crypto_aead_aes256gcm_NPUBBYTES
    if c.crypto_aead_aes256gcm_is_available():
        ciphertext = c.crypto_aead_aes256gcm_encrypt(msg, nonce, key, None, 0)
        cipher = ciphertext[0:len(msg)]
        tag = ciphertext[len(msg):]
        msg2 = c.crypto_aead_aes256gcm_decrypt(
            cipher, tag, nonce,
            key, None, 0)
        assert msg2[:] == msg

        with pytest.raises(CryptoError):
            c.crypto_aead_aes256gcm_decrypt(
                msg + b"!",
                tag,
                nonce,
                key,
                None,
                0
            )
