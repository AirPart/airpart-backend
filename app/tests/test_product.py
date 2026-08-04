from unittest.mock import patch

# ==============================================================================
# POST /product/search
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_search_product_success(mock_prod_service, client, mock_product_data):
    """Test searching products with valid query return matching products"""
    mock_prod_service.search.return_value = [mock_product_data]

    payload = {"query": "VALVE ASSEMBLY.734-2061.SN-99823.EA.734-2061ALT.Airbus"}

    response = client.post("/product/search", json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["message"] == "search products successfully"
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["part_number"] == "734-2061"


def test_search_product_missing_query(client):
    """Test search fails with 400 when query is missing or empty"""
    response = client.post("/product/search", json={})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
