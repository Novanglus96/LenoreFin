def apply_patch(instance, payload, exclude: set[str] = None):
    """
    Apply only explicitly set fields from the payload to the Django model instance.
    Optionally, exclude certain fields from being updated.
    """
    exclude = exclude or set()

    for field in payload.__fields_set__:
        if field in exclude:
            continue
        setattr(instance, field, getattr(payload, field))
