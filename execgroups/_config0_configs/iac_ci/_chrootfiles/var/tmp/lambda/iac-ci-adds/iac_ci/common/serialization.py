#!/usr/bin/env python

import json
import base64

try:
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers import algorithms
    from cryptography.hazmat.primitives.ciphers import modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.fernet import Fernet
except Exception:
    print("could not import cryptography")

def b64_encode(obj):
    """
    Encode an object or string to base64.

    Args:
        obj: Input object to encode. Can be a dictionary or any object that can be JSON serialized,
             or a string.

    Returns:
        str: ASCII-encoded base64 string.

    Notes:
        - If input is a dictionary, it is first converted to JSON string
        - For non-string/dict inputs, attempts JSON serialization
        - Converts input to ASCII bytes before base64 encoding
    """
    if isinstance(obj,dict):
        obj = json.dumps(obj)
    elif not isinstance(obj,str):
        try:
            obj = json.dumps(obj)
        except Exception:
            print("warning: could not json dump object for b64")

    _bytes = obj.encode('ascii')
    base64_bytes = base64.b64encode(_bytes)

    # decode the b64 binary in a b64 string
    return base64_bytes.decode('ascii')

def b64_decode(token):
    """
    Decode a base64 string back to its original form.

    Args:
        token (str): Base64 encoded string to decode.

    Returns:
        Union[dict, str]: Decoded data, either as:
            - JSON-parsed dictionary/object if valid JSON
            - ASCII string if decodable as ASCII
            - UTF-8 string as fallback

    Notes:
        - Attempts multiple decode strategies in order:
            1. JSON decode from ASCII
            2. Plain ASCII decode
            3. Default string decode
            4. UTF-8 decode as final fallback
        - Returns None for each failed decode attempt before trying next method
    """
    base64_bytes = token.encode('ascii')
    _bytes = base64.b64decode(base64_bytes)

    try:
        _results = json.loads(_bytes.decode('ascii'))
    except Exception:
        _results = None

    if _results:
        return _results

    try:
        _results = _bytes.decode('ascii')
    except Exception:
        _results = None

    if _results:
        return _results

    try:
        _results = _bytes.decode()
    except Exception:
        _results = None

    if _results:
        return _results

    _results = _bytes.decode("utf-8")

    return _results
