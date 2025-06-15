def test_app_creation_and_init_coverage(testapp):
    """
    This test's only job is to make sure the app can be created.
    By simply asking for the 'testapp' fixture, we force it to run,
    which in turn executes all the code in your __init__.py.
    """
    # The test passes if the testapp was created without any errors.
    assert testapp is not None
