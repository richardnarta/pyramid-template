def test_landing_endpoint(testapp):
    # Action
    response = testapp.get(
        '/',
        status=200
    )

    # Assert
    assert response.json['project'] == 'B2B Setara Commodity API'
    assert response.json['owner'] == 'PT. Arga Bumi Indonesia'
    assert response.json['version'] == '2.0.0'
    assert response.json['docs'] == 'api-stg.b2bsetara.co.id/docs/'


def test_unregistered_endpoint(testapp):
    # Action
    response = testapp.get(
        '/unknown',
        status=404
    )

    # Assert
    assert response.json['error'] == True
    assert response.json['message'] == 'Endpoint not found: The path \'/unknown\' does not exist on this server.'
