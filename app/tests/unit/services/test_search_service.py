"""Unit tests for SearchAPI."""

from app.services.products.search import SearchAPI

# ==============================================================================
# parse_search
# ==============================================================================


def test_parse_search_returns_six_parts_for_complete_query():
    search_api = SearchAPI("DESC.PN-001.SN-001.PCS.ALT-001.AirPart")

    result = search_api.parse_search()

    assert result == [
        "DESC",
        "PN-001",
        "SN-001",
        "PCS",
        "ALT-001",
        "AirPart",
    ]


def test_parse_search_pads_missing_parts_with_empty_strings():
    search_api = SearchAPI("DESC.PN-001")

    result = search_api.parse_search()

    assert result == [
        "DESC",
        "PN-001",
        "",
        "",
        "",
        "",
    ]


def test_parse_search_ignores_extra_parts_after_six_items():
    search_api = SearchAPI("DESC.PN-001.SN-001.PCS.ALT-001.AirPart.EXTRA")

    result = search_api.parse_search()

    assert result == [
        "DESC",
        "PN-001",
        "SN-001",
        "PCS",
        "ALT-001",
        "AirPart",
    ]


def test_parse_search_returns_empty_parts_for_empty_query():
    search_api = SearchAPI("")

    result = search_api.parse_search()

    assert result == [
        "",
        "",
        "",
        "",
        "",
        "",
    ]


# ==============================================================================
# normalize
# ==============================================================================


def test_normalize_strips_spaces():
    search_api = SearchAPI("")

    result = search_api.normalize("  PN-001  ")

    assert result == "PN-001"


def test_normalize_returns_empty_string_for_none():
    search_api = SearchAPI("")

    result = search_api.normalize(None)

    assert result == ""


def test_normalize_returns_empty_string_for_empty_value():
    search_api = SearchAPI("")

    result = search_api.normalize("")

    assert result == ""


# ==============================================================================
# product_matches
# ==============================================================================


def test_product_matches_returns_true_when_all_non_empty_filters_match():
    search_api = SearchAPI("")

    product = {
        "description": "Engine Part",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "unit": "PCS",
        "alternate": "ALT-001",
        "company": "AirPart",
    }

    filters = {
        "description": "Engine Part",
        "part_number": "PN-001",
        "serial_number": "",
        "unit": "",
        "alternate": "",
        "company": "AirPart",
    }

    result = search_api.product_matches(product, filters)

    assert result is True


def test_product_matches_ignores_empty_filters():
    search_api = SearchAPI("")

    product = {
        "description": "Engine Part",
        "part_number": "PN-001",
    }

    filters = {
        "description": "",
        "part_number": "PN-001",
        "serial_number": "",
    }

    result = search_api.product_matches(product, filters)

    assert result is True


def test_product_matches_returns_false_when_filter_does_not_match():
    search_api = SearchAPI("")

    product = {
        "description": "Engine Part",
        "part_number": "PN-001",
    }

    filters = {
        "description": "Engine Part",
        "part_number": "PN-999",
    }

    result = search_api.product_matches(product, filters)

    assert result is False


def test_product_matches_returns_false_when_product_key_is_missing():
    search_api = SearchAPI("")

    product = {
        "description": "Engine Part",
    }

    filters = {
        "part_number": "PN-001",
    }

    result = search_api.product_matches(product, filters)

    assert result is False


# ==============================================================================
# search_products
# ==============================================================================


def test_search_products_returns_matching_products_by_description():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "unit": "PCS",
            "alternate": "ALT-001",
            "company": "AirPart",
        },
        {
            "id": "prod-2",
            "description": "Wing Part",
            "part_number": "PN-002",
            "serial_number": "SN-002",
            "unit": "PCS",
            "alternate": "ALT-002",
            "company": "AirPart",
        },
    ]

    search_api = SearchAPI("Engine Part")

    result = search_api.search_products(products)

    assert result == [products[0]]


def test_search_products_returns_matching_products_by_part_number():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "unit": "PCS",
            "alternate": "ALT-001",
            "company": "AirPart",
        },
        {
            "id": "prod-2",
            "description": "Wing Part",
            "part_number": "PN-002",
            "serial_number": "SN-002",
            "unit": "PCS",
            "alternate": "ALT-002",
            "company": "AirPart",
        },
    ]

    search_api = SearchAPI(".PN-002")

    result = search_api.search_products(products)

    assert result == [products[1]]


def test_search_products_returns_matching_products_by_multiple_filters():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "unit": "PCS",
            "alternate": "ALT-001",
            "company": "AirPart",
        },
        {
            "id": "prod-2",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-999",
            "unit": "PCS",
            "alternate": "ALT-001",
            "company": "OtherCompany",
        },
    ]

    search_api = SearchAPI("Engine Part.PN-001.SN-001.PCS.ALT-001.AirPart")

    result = search_api.search_products(products)

    assert result == [products[0]]


def test_search_products_returns_empty_list_when_no_product_matches():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "unit": "PCS",
            "alternate": "ALT-001",
            "company": "AirPart",
        },
    ]

    search_api = SearchAPI("Wing Part")

    result = search_api.search_products(products)

    assert result == []


def test_search_products_returns_all_products_when_query_is_empty():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
        },
        {
            "id": "prod-2",
            "description": "Wing Part",
            "part_number": "PN-002",
        },
    ]

    search_api = SearchAPI("")

    result = search_api.search_products(products)

    assert result == products


def test_search_products_is_exact_match_and_case_sensitive():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
        },
    ]

    search_api = SearchAPI("engine part")

    result = search_api.search_products(products)

    assert result == []


def test_search_products_strips_query_spaces_before_matching():
    products = [
        {
            "id": "prod-1",
            "description": "Engine Part",
            "part_number": "PN-001",
        },
    ]

    search_api = SearchAPI("  Engine Part  ")

    result = search_api.search_products(products)

    assert result == [products[0]]
