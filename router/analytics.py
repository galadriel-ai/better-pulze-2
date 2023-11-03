import enum

import segment.analytics as segment_analytics

import settings

SEGMENT_WRITE_KEY = settings.SEGMENT_WRITE_KEY
segment_analytics.write_key = SEGMENT_WRITE_KEY


class TrackingEventType(enum.Enum):
    REGISTER = 1
    API_REQUEST = 2


def track(event_type: TrackingEventType, user_id: str, email: str, **kwargs):
    """Should be the entry point to all tracking."""
    if not settings.SEGMENT_WRITE_KEY:
        return

    switcher = {
        TrackingEventType.REGISTER: _track_register,
        TrackingEventType.API_REQUEST: _track_api_call,
    }

    func = switcher.get(event_type)
    if func is None:
        return

    try:
        func(user_id, email, **kwargs)
    except Exception as e:
        # Same reason to hide exception as above
        pass


def _track_register(
        user_id: str, email: str, **kwargs
):
    segment_analytics.track(
        user_id=user_id or email,
        event="Sign up",
    )


def _track_api_call(
        user_id: str, email: str, **kwargs
):
    segment_analytics.track(
        user_id=user_id or email,
        event="API call",
    )
