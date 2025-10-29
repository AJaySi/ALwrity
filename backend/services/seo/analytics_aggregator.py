"""
Analytics Aggregator Service

Combines and normalizes data from multiple platforms (GSC, Bing, etc.)
for the SEO dashboard. Provides unified metrics and timeseries data.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from utils.logger_utils import get_service_logger

logger = get_service_logger("analytics_aggregator")

class AnalyticsAggregator:
    """Aggregates analytics data from multiple platforms."""
    
    def __init__(self):
        """Initialize the analytics aggregator."""
        pass
    
    def combine_metrics(self, gsc_data: Dict[str, Any], bing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine metrics from GSC and Bing data.
        
        Args:
            gsc_data: GSC analytics data
            bing_data: Bing analytics data
            
        Returns:
            Combined metrics dictionary
        """
        try:
            # Extract metrics from each platform
            gsc_metrics = self._extract_gsc_metrics(gsc_data)
            bing_metrics = self._extract_bing_metrics(bing_data)
            
            # Combine the metrics
            combined = {
                "clicks": gsc_metrics.get("clicks", 0) + bing_metrics.get("clicks", 0),
                "impressions": gsc_metrics.get("impressions", 0) + bing_metrics.get("impressions", 0),
                "ctr": self._calculate_combined_ctr(gsc_metrics, bing_metrics),
                "position": self._calculate_combined_position(gsc_metrics, bing_metrics),
                "queries": gsc_metrics.get("queries", 0) + bing_metrics.get("queries", 0),
                "pages": gsc_metrics.get("pages", 0) + bing_metrics.get("pages", 0),
                "countries": self._combine_countries(gsc_metrics.get("countries", []), bing_metrics.get("countries", [])),
                "devices": self._combine_devices(gsc_metrics.get("devices", []), bing_metrics.get("devices", [])),
                "sources": {
                    "gsc": gsc_metrics,
                    "bing": bing_metrics
                }
            }
            
            logger.debug(f"Combined metrics: {combined}")
            return combined
            
        except Exception as e:
            logger.error(f"Error combining metrics: {e}")
            return {
                "clicks": 0,
                "impressions": 0,
                "ctr": 0.0,
                "position": 0.0,
                "queries": 0,
                "pages": 0,
                "countries": [],
                "devices": [],
                "sources": {"gsc": {}, "bing": {}}
            }
    
    def normalize_timeseries(self, gsc_daily: List[Dict[str, Any]], bing_daily: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize timeseries data from GSC and Bing to aligned date series.
        
        Args:
            gsc_daily: GSC daily data
            bing_daily: Bing daily data
            
        Returns:
            Normalized timeseries data
        """
        try:
            # Convert to date-indexed dictionaries
            gsc_by_date = {item["date"]: item for item in gsc_daily}
            bing_by_date = {item["date"]: item for item in bing_daily}
            
            # Get all unique dates
            all_dates = set(gsc_by_date.keys()) | set(bing_by_date.keys())
            sorted_dates = sorted(all_dates)
            
            # Create normalized timeseries
            timeseries = []
            for date in sorted_dates:
                gsc_item = gsc_by_date.get(date, {})
                bing_item = bing_by_date.get(date, {})
                
                normalized_item = {
                    "date": date,
                    "clicks": gsc_item.get("clicks", 0) + bing_item.get("clicks", 0),
                    "impressions": gsc_item.get("impressions", 0) + bing_item.get("impressions", 0),
                    "ctr": self._calculate_daily_ctr(gsc_item, bing_item),
                    "position": self._calculate_daily_position(gsc_item, bing_item),
                    "gsc_clicks": gsc_item.get("clicks", 0),
                    "gsc_impressions": gsc_item.get("impressions", 0),
                    "bing_clicks": bing_item.get("clicks", 0),
                    "bing_impressions": bing_item.get("impressions", 0)
                }
                
                timeseries.append(normalized_item)
            
            logger.debug(f"Normalized timeseries with {len(timeseries)} data points")
            return timeseries
            
        except Exception as e:
            logger.error(f"Error normalizing timeseries: {e}")
            return []
    
    def top_queries_combined(self, gsc_data: Dict[str, Any], bing_data: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top queries combined from GSC and Bing data.
        
        Args:
            gsc_data: GSC data
            bing_data: Bing data
            limit: Maximum number of queries to return
            
        Returns:
            List of top queries with source tags
        """
        try:
            # Extract queries from each platform
            gsc_queries = self._extract_gsc_queries(gsc_data)
            bing_queries = self._extract_bing_queries(bing_data)
            
            # Combine and deduplicate queries
            query_map = {}
            
            # Add GSC queries
            for query in gsc_queries:
                query_text = query.get("query", "").lower()
                if query_text in query_map:
                    # Merge data from both sources
                    existing = query_map[query_text]
                    existing["gsc_clicks"] = query.get("clicks", 0)
                    existing["gsc_impressions"] = query.get("impressions", 0)
                    existing["gsc_ctr"] = query.get("ctr", 0)
                    existing["gsc_position"] = query.get("position", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + query.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + query.get("impressions", 0)
                    existing["sources"].append("gsc")
                else:
                    query_map[query_text] = {
                        "query": query.get("query", ""),
                        "gsc_clicks": query.get("clicks", 0),
                        "gsc_impressions": query.get("impressions", 0),
                        "gsc_ctr": query.get("ctr", 0),
                        "gsc_position": query.get("position", 0),
                        "bing_clicks": 0,
                        "bing_impressions": 0,
                        "bing_ctr": 0,
                        "bing_position": 0,
                        "total_clicks": query.get("clicks", 0),
                        "total_impressions": query.get("impressions", 0),
                        "sources": ["gsc"]
                    }
            
            # Add Bing queries
            for query in bing_queries:
                query_text = query.get("query", "").lower()
                if query_text in query_map:
                    # Merge data from both sources
                    existing = query_map[query_text]
                    existing["bing_clicks"] = query.get("clicks", 0)
                    existing["bing_impressions"] = query.get("impressions", 0)
                    existing["bing_ctr"] = query.get("ctr", 0)
                    existing["bing_position"] = query.get("position", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + query.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + query.get("impressions", 0)
                    existing["sources"].append("bing")
                else:
                    query_map[query_text] = {
                        "query": query.get("query", ""),
                        "gsc_clicks": 0,
                        "gsc_impressions": 0,
                        "gsc_ctr": 0,
                        "gsc_position": 0,
                        "bing_clicks": query.get("clicks", 0),
                        "bing_impressions": query.get("impressions", 0),
                        "bing_ctr": query.get("ctr", 0),
                        "bing_position": query.get("position", 0),
                        "total_clicks": query.get("clicks", 0),
                        "total_impressions": query.get("impressions", 0),
                        "sources": ["bing"]
                    }
            
            # Sort by total clicks and return top N
            sorted_queries = sorted(
                query_map.values(),
                key=lambda x: x["total_clicks"],
                reverse=True
            )
            
            logger.debug(f"Combined {len(sorted_queries)} unique queries, returning top {limit}")
            return sorted_queries[:limit]
            
        except Exception as e:
            logger.error(f"Error combining top queries: {e}")
            return []
    
    def _extract_gsc_metrics(self, gsc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from GSC data."""
        try:
            if "error" in gsc_data:
                return {}
            
            data = gsc_data.get("data", {})
            return {
                "clicks": data.get("clicks", 0),
                "impressions": data.get("impressions", 0),
                "ctr": data.get("ctr", 0.0),
                "position": data.get("position", 0.0),
                "queries": len(data.get("queries", [])),
                "pages": len(data.get("pages", [])),
                "countries": data.get("countries", []),
                "devices": data.get("devices", [])
            }
        except Exception as e:
            logger.error(f"Error extracting GSC metrics: {e}")
            return {}
    
    def _extract_bing_metrics(self, bing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from Bing data."""
        try:
            if "error" in bing_data:
                return {}
            
            data = bing_data.get("data", {})
            return {
                "clicks": data.get("clicks", 0),
                "impressions": data.get("impressions", 0),
                "ctr": data.get("ctr", 0.0),
                "position": data.get("position", 0.0),
                "queries": len(data.get("queries", [])),
                "pages": len(data.get("pages", [])),
                "countries": data.get("countries", []),
                "devices": data.get("devices", [])
            }
        except Exception as e:
            logger.error(f"Error extracting Bing metrics: {e}")
            return {}
    
    def _extract_gsc_queries(self, gsc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract queries from GSC data."""
        try:
            if "error" in gsc_data:
                return []
            
            data = gsc_data.get("data", {})
            return data.get("queries", [])
        except Exception as e:
            logger.error(f"Error extracting GSC queries: {e}")
            return []
    
    def _extract_bing_queries(self, bing_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract queries from Bing data."""
        try:
            if "error" in bing_data:
                return []
            
            data = bing_data.get("data", {})
            return data.get("queries", [])
        except Exception as e:
            logger.error(f"Error extracting Bing queries: {e}")
            return []
    
    def _calculate_combined_ctr(self, gsc_metrics: Dict[str, Any], bing_metrics: Dict[str, Any]) -> float:
        """Calculate combined CTR from GSC and Bing metrics."""
        try:
            total_clicks = gsc_metrics.get("clicks", 0) + bing_metrics.get("clicks", 0)
            total_impressions = gsc_metrics.get("impressions", 0) + bing_metrics.get("impressions", 0)
            
            if total_impressions > 0:
                return total_clicks / total_impressions
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating combined CTR: {e}")
            return 0.0
    
    def _calculate_combined_position(self, gsc_metrics: Dict[str, Any], bing_metrics: Dict[str, Any]) -> float:
        """Calculate combined average position from GSC and Bing metrics."""
        try:
            gsc_position = gsc_metrics.get("position", 0)
            bing_position = bing_metrics.get("position", 0)
            
            # Weight by impressions if available
            gsc_impressions = gsc_metrics.get("impressions", 0)
            bing_impressions = bing_metrics.get("impressions", 0)
            total_impressions = gsc_impressions + bing_impressions
            
            if total_impressions > 0:
                return (gsc_position * gsc_impressions + bing_position * bing_impressions) / total_impressions
            elif gsc_position > 0 and bing_position > 0:
                return (gsc_position + bing_position) / 2
            elif gsc_position > 0:
                return gsc_position
            elif bing_position > 0:
                return bing_position
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating combined position: {e}")
            return 0.0
    
    def _calculate_daily_ctr(self, gsc_item: Dict[str, Any], bing_item: Dict[str, Any]) -> float:
        """Calculate CTR for a single day."""
        try:
            total_clicks = gsc_item.get("clicks", 0) + bing_item.get("clicks", 0)
            total_impressions = gsc_item.get("impressions", 0) + bing_item.get("impressions", 0)
            
            if total_impressions > 0:
                return total_clicks / total_impressions
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating daily CTR: {e}")
            return 0.0
    
    def _calculate_daily_position(self, gsc_item: Dict[str, Any], bing_item: Dict[str, Any]) -> float:
        """Calculate average position for a single day."""
        try:
            gsc_position = gsc_item.get("position", 0)
            bing_position = bing_item.get("position", 0)
            
            if gsc_position > 0 and bing_position > 0:
                return (gsc_position + bing_position) / 2
            elif gsc_position > 0:
                return gsc_position
            elif bing_position > 0:
                return bing_position
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating daily position: {e}")
            return 0.0
    
    def _combine_countries(self, gsc_countries: List[Dict[str, Any]], bing_countries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine country data from GSC and Bing."""
        try:
            country_map = {}
            
            # Add GSC countries
            for country in gsc_countries:
                country_code = country.get("country", "")
                if country_code in country_map:
                    existing = country_map[country_code]
                    existing["gsc_clicks"] = country.get("clicks", 0)
                    existing["gsc_impressions"] = country.get("impressions", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + country.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + country.get("impressions", 0)
                else:
                    country_map[country_code] = {
                        "country": country_code,
                        "gsc_clicks": country.get("clicks", 0),
                        "gsc_impressions": country.get("impressions", 0),
                        "bing_clicks": 0,
                        "bing_impressions": 0,
                        "total_clicks": country.get("clicks", 0),
                        "total_impressions": country.get("impressions", 0)
                    }
            
            # Add Bing countries
            for country in bing_countries:
                country_code = country.get("country", "")
                if country_code in country_map:
                    existing = country_map[country_code]
                    existing["bing_clicks"] = country.get("clicks", 0)
                    existing["bing_impressions"] = country.get("impressions", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + country.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + country.get("impressions", 0)
                else:
                    country_map[country_code] = {
                        "country": country_code,
                        "gsc_clicks": 0,
                        "gsc_impressions": 0,
                        "bing_clicks": country.get("clicks", 0),
                        "bing_impressions": country.get("impressions", 0),
                        "total_clicks": country.get("clicks", 0),
                        "total_impressions": country.get("impressions", 0)
                    }
            
            # Sort by total clicks
            return sorted(country_map.values(), key=lambda x: x["total_clicks"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error combining countries: {e}")
            return []
    
    def _combine_devices(self, gsc_devices: List[Dict[str, Any]], bing_devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine device data from GSC and Bing."""
        try:
            device_map = {}
            
            # Add GSC devices
            for device in gsc_devices:
                device_type = device.get("device", "")
                if device_type in device_map:
                    existing = device_map[device_type]
                    existing["gsc_clicks"] = device.get("clicks", 0)
                    existing["gsc_impressions"] = device.get("impressions", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + device.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + device.get("impressions", 0)
                else:
                    device_map[device_type] = {
                        "device": device_type,
                        "gsc_clicks": device.get("clicks", 0),
                        "gsc_impressions": device.get("impressions", 0),
                        "bing_clicks": 0,
                        "bing_impressions": 0,
                        "total_clicks": device.get("clicks", 0),
                        "total_impressions": device.get("impressions", 0)
                    }
            
            # Add Bing devices
            for device in bing_devices:
                device_type = device.get("device", "")
                if device_type in device_map:
                    existing = device_map[device_type]
                    existing["bing_clicks"] = device.get("clicks", 0)
                    existing["bing_impressions"] = device.get("impressions", 0)
                    existing["total_clicks"] = existing.get("total_clicks", 0) + device.get("clicks", 0)
                    existing["total_impressions"] = existing.get("total_impressions", 0) + device.get("impressions", 0)
                else:
                    device_map[device_type] = {
                        "device": device_type,
                        "gsc_clicks": 0,
                        "gsc_impressions": 0,
                        "bing_clicks": device.get("clicks", 0),
                        "bing_impressions": device.get("impressions", 0),
                        "total_clicks": device.get("clicks", 0),
                        "total_impressions": device.get("impressions", 0)
                    }
            
            # Sort by total clicks
            return sorted(device_map.values(), key=lambda x: x["total_clicks"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error combining devices: {e}")
            return []