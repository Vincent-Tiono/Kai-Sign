"""
Version 1 of the conversion to Ledger specific calldata descriptor (also referred to as "generic parser" descriptor).

See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol

The version 1 of the protocol comes with the following limitations:
 - Nested array fields are only partially supported
 - Recursive invocations using fields with "calldata" format are not supported
"""
