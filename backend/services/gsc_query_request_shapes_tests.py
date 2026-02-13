from services.gsc_service import GSCService


class MinimalGSCService(GSCService):
    def __init__(self):
        # Skip DB/table init for pure request-shape tests.
        pass


def test_build_query_request_uses_documented_bounds_and_type():
    svc = MinimalGSCService()

    req = svc._build_search_analytics_request(
        start_date="2026-01-01",
        end_date="2026-01-31",
        dimensions=["query"],
        row_limit=100000,
        start_row=-10,
    )

    assert req["startDate"] == "2026-01-01"
    assert req["endDate"] == "2026-01-31"
    assert req["type"] == "web"
    assert req["dimensions"] == ["query"]
    assert req["startRow"] == 0
    assert req["rowLimit"] == 25000


def test_build_overall_request_omits_dimensions_for_aggregate_totals():
    svc = MinimalGSCService()

    req = svc._build_search_analytics_request(
        start_date="2026-01-01",
        end_date="2026-01-31",
        dimensions=None,
        row_limit=1,
    )

    assert "dimensions" not in req
    assert req["rowLimit"] == 1
    assert req["type"] == "web"
