"""
This module patches the erc7730 library to use in-memory caching instead of file caching.
This makes it compatible with Vercel's serverless functions which have a read-only filesystem.
"""

import httpx
from functools import wraps
from erc7730.generate.generate import generate_descriptor as original_generate_descriptor
from erc7730.common.client import _client
import inspect
from hishel import CacheTransport, MemoryStorage
from erc7730.common.client import HTTPTransport, GithubTransport, EtherscanTransport, FileTransport, Client


# Create an in-memory cache to replace the file-based cache
memory_storage = MemoryStorage()

# Dictionary to store cached ABIs
abi_cache = {}


def patched_client():
    """
    Create a new HTTP client with in-memory caching instead of file caching.
    This version is compatible with serverless environments like Vercel.
    """
    http_transport = HTTPTransport()
    http_transport = GithubTransport(http_transport)
    http_transport = EtherscanTransport(http_transport)
    http_transport = CacheTransport(transport=http_transport, storage=memory_storage)
    file_transport = FileTransport()
    transports = {"https://": http_transport, "file://": file_transport}
    return Client(mounts=transports, timeout=10)


# Patch the _client function
def patch_client():
    from erc7730.common import client
    client._client = patched_client


def generate_descriptor(*args, **kwargs):
    """
    Wrapper around the original generate_descriptor function that applies the patch.
    """
    # Apply the patch to use in-memory caching
    patch_client()
    
    # Call the original function
    return original_generate_descriptor(*args, **kwargs)