"""
Version 1 of the data model for Ledger specific calldata descriptor (also referred to as "generic parser" descriptor).

See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol

This data model is exposed in the public API and used by client applications to interact with the Ethereum application
using the generic parser protocol.

The version 1 of the protocol comes with the following limitations:
 - Constant/literal values are not supported
 - Nested array fields are only partially supported
 - Recursive invocations using fields with "calldata" format are not supported
"""
