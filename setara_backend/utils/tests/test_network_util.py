import requests
from unittest.mock import MagicMock
from setara_backend.utils import get_location_from_ip


class TestGetLocationFromIp:
    """Test suite for the get_location_from_ip function."""

    def test_get_location_success(self, mocker):
        """
        Tests the happy path: the API call is successful.
        """
        # Setup
        ip_address = "8.8.8.8"
        expected_city = "Mountain View"
        expected_loc = "37.4220,-122.0840"
        mock_api_response_data = {
            "city": expected_city,
            "loc": expected_loc
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status.return_value = None

        mock_requests_get = mocker.patch(
            'requests.get', return_value=mock_response)

        # Action
        result = get_location_from_ip(ip_address)

        # Assert
        assert result['city'] == expected_city
        assert result['loc'] == expected_loc
        mock_requests_get.assert_called_once_with(
            f"https://ipinfo.io/{ip_address}/json")

    def test_get_location_api_error(self, mocker):
        """
        Tests the failure path: raise_for_status() raises an error.
        """
        # Setup
        ip_address = "127.0.0.1"

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error: Not Found"
        )

        mock_requests_get = mocker.patch(
            'requests.get', return_value=mock_response)

        # Action
        result = get_location_from_ip(ip_address)

        # Assert
        assert result['city'] is None
        assert result['loc'] is None
        mock_requests_get.assert_called_once()

    def test_get_location_network_exception(self, mocker):
        """
        Tests the exception path: a network error occurs during the request.
        (This test was already correct and needs no changes).
        """
        # Setup
        ip_address = "10.0.0.1"
        mocker.patch(
            'requests.get',
            side_effect=requests.exceptions.RequestException(
                "Simulated network error")
        )

        # Action
        result = get_location_from_ip(ip_address)

        # Assert
        assert result['city'] is None
        assert result['loc'] is None
