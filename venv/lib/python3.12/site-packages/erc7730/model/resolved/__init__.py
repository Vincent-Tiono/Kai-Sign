"""
Package implementing an object model for ERC-7730 resolved descriptors.

This model represents descriptors after resolution phase:
    - URLs have been fetched
    - Contract addresses have been normalized to lowercase
    - References have been inlined
    - Constants have been inlined
    - Field definitions have been inlined
    - Nested fields have been flattened where possible
    - Selectors have been converted to 4 bytes form
"""
