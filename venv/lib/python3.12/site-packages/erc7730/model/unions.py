from typing import Any

from erc7730.common.properties import has_any_property


def field_discriminator(v: Any) -> str | None:
    """
    Discriminator function for the Field union type.

    :param v: deserialized raw data
    :return: the discriminator tag
    """
    if has_any_property(v, "$ref"):
        return "reference"
    if has_any_property(v, "fields"):
        return "nested_fields"
    if has_any_property(v, "label"):
        return "field_description"
    return None


def field_parameters_discriminator(v: Any) -> str | None:
    """
    Discriminator function for the FieldParameters union type.

    :param v: deserialized raw data
    :return: the discriminator tag
    """
    if has_any_property(v, "tokenPath", "token", "nativeCurrencyAddress"):
        return "token_amount"
    if has_any_property(v, "encoding"):
        return "date"
    if has_any_property(v, "collectionPath", "collection"):
        return "nft_name"
    if has_any_property(v, "base"):
        return "unit"
    if has_any_property(v, "$ref", "ref", "enumId"):
        return "enum"
    if has_any_property(v, "calleePath", "callee", "selector"):
        return "call_data"
    if has_any_property(v, "sources", "types"):
        return "address_name"
    return None
