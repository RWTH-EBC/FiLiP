from datetime import datetime, timezone


def transform_to_utc_datetime(dt: datetime) -> datetime:
    """
    Converts datetime object to utc datetime object with zone

    Args:
        dt:

    Returns:

    """
    return dt.astimezone(tz=timezone.utc)


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    """
    Converts datetime object to iso8601 notation with z-suffix

    Args:
        dt: datetime object

    Returns:
        String in iso 8601 notation with z-suffix
    """
    dt = transform_to_utc_datetime(dt)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'


