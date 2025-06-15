def includeme(config):
    """
    Activates middleware for the application.
    """
    config.add_tween('.cors.cors_tween_factory')

    config.add_tween(
        '.rate_limiter.rate_limiter_tween_factory',
        under='pyramid_tm.tm_tween_factory'
    )

    config.include('.security')
