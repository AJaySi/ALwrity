import os
import asyncio
from datetime import date, timedelta

import httpx


async def main() -> None:
  base_url = os.environ.get("ALWRITY_API_BASE_URL", "http://localhost:8000")
  token = os.environ.get("ALWRITY_API_TOKEN")

  today = date.today()
  start = today - timedelta(days=29)

  params = {
    "platforms": "gsc",
    "start_date": start.isoformat(),
    "end_date": today.isoformat(),
  }

  headers = {}
  if token:
    headers["Authorization"] = f"Bearer {token}"

  async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=60.0) as client:
    resp = await client.get("/api/analytics/data", params=params)
    print(f"Status: {resp.status_code}")
    try:
      data = resp.json()
    except Exception:
      print("Non‑JSON response body:")
      print(resp.text)
      return

    print("Raw JSON response:")
    print(data)

    summary = data.get("summary") or {}
    platforms = data.get("data") or {}
    gsc = platforms.get("gsc") or {}
    gsc_metrics = gsc.get("metrics") or {}

    print("\nSummary snapshot:")
    print(f"  total_clicks:      {summary.get('total_clicks')}")
    print(f"  total_impressions: {summary.get('total_impressions')}")
    print(f"  overall_ctr:       {summary.get('overall_ctr')}")

    print("\nGSC metrics snapshot:")
    print(f"  total_clicks:      {gsc_metrics.get('total_clicks')}")
    print(f"  total_impressions: {gsc_metrics.get('total_impressions')}")
    print(f"  avg_ctr:           {gsc_metrics.get('avg_ctr')}")
    print(f"  avg_position:      {gsc_metrics.get('avg_position')}")


if __name__ == "__main__":
  asyncio.run(main())
