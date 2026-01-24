#!/usr/bin/env python3
"""
Image Studio Refactoring Validation Script

This script performs comprehensive validation of the refactored Image Studio API
to ensure all functionality is preserved and working correctly.

Usage:
    python validate_image_studio_refactor.py --base-url http://localhost:8000
    python validate_image_studio_refactor.py --environment staging

Validation Checks:
- Health endpoint functionality
- Status endpoint data accuracy
- Route count validation
- Feature flag configuration
- Basic endpoint availability
- Response format validation
"""

import argparse
import requests
import json
import sys
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details or {}
        }


class ImageStudioValidator:
    """Validates the refactored Image Studio API."""

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.timeout = 30

        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

        self.results: List[ValidationResult] = []

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting Image Studio refactoring validation...")
        print(f"📍 Target URL: {self.base_url}")
        print()

        # Run all validation checks
        checks = [
            self.validate_health_endpoint,
            self.validate_status_endpoint,
            self.validate_route_counts,
            self.validate_feature_flags,
            self.validate_module_endpoints,
            self.validate_response_formats,
            self.validate_error_handling
        ]

        all_passed = True
        for check in checks:
            result = check()
            self.results.append(result)
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.check_name}: {result.message}")
            if not result.passed:
                all_passed = False

        print()
        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        print(f"Total Checks: {total_count}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total_count - passed_count}")

        if all_passed:
            print("🎉 ALL VALIDATION CHECKS PASSED!")
            print("The refactored Image Studio API is ready for production.")
        else:
            print("❌ SOME VALIDATION CHECKS FAILED!")
            print("Please review the failed checks before proceeding.")

        return all_passed

    def validate_health_endpoint(self) -> ValidationResult:
        """Validate health endpoint functionality."""
        try:
            response = self.session.get(f"{self.base_url}/api/image-studio/health")
            response.raise_for_status()
            data = response.json()

            # Check required fields
            required_fields = ["status", "service", "version", "total_routes", "architecture"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return ValidationResult(
                    "Health Endpoint",
                    False,
                    f"Missing required fields: {missing_fields}",
                    {"received_fields": list(data.keys())}
                )

            # Check status
            if data["status"] not in ["healthy", "degraded"]:
                return ValidationResult(
                    "Health Endpoint",
                    False,
                    f"Invalid status: {data['status']}",
                    {"status": data["status"]}
                )

            # Check architecture
            if data.get("architecture") != "modular_routers":
                return ValidationResult(
                    "Health Endpoint",
                    False,
                    f"Invalid architecture: {data.get('architecture')}",
                    {"architecture": data.get("architecture")}
                )

            return ValidationResult(
                "Health Endpoint",
                True,
                "Health endpoint is functioning correctly",
                {"status": data["status"], "total_routes": data["total_routes"]}
            )

        except Exception as e:
            return ValidationResult(
                "Health Endpoint",
                False,
                f"Health endpoint error: {e}"
            )

    def validate_status_endpoint(self) -> ValidationResult:
        """Validate status endpoint functionality."""
        try:
            response = self.session.get(f"{self.base_url}/api/image-studio/status")
            response.raise_for_status()
            data = response.json()

            # Check required fields
            required_fields = ["service", "version", "status", "modules", "total_endpoints"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return ValidationResult(
                    "Status Endpoint",
                    False,
                    f"Missing required fields: {missing_fields}"
                )

            # Check modules structure
            modules = data.get("modules", {})
            expected_modules = ["generation", "editing", "advanced", "utilities"]

            for module in expected_modules:
                if module not in modules:
                    return ValidationResult(
                        "Status Endpoint",
                        False,
                        f"Missing module in status: {module}",
                        {"available_modules": list(modules.keys())}
                    )

            return ValidationResult(
                "Status Endpoint",
                True,
                "Status endpoint provides correct module information",
                {"total_endpoints": data["total_endpoints"], "modules": list(modules.keys())}
            )

        except Exception as e:
            return ValidationResult(
                "Status Endpoint",
                False,
                f"Status endpoint error: {e}"
            )

    def validate_route_counts(self) -> ValidationResult:
        """Validate that route counts match expectations."""
        try:
            response = self.session.get(f"{self.base_url}/api/image-studio/health")
            response.raise_for_status()
            health_data = response.json()

            routes_by_module = health_data.get("routes_by_module", {})
            expected_counts = {
                "generation": 6,
                "editing": 7,
                "advanced": 10,
                "utilities": 10
            }

            mismatches = []
            for module, expected_count in expected_counts.items():
                actual_count = routes_by_module.get(module, 0)
                if actual_count != expected_count:
                    mismatches.append(f"{module}: expected {expected_count}, got {actual_count}")

            if mismatches:
                return ValidationResult(
                    "Route Counts",
                    False,
                    f"Route count mismatches: {mismatches}",
                    {"routes_by_module": routes_by_module}
                )

            total_expected = sum(expected_counts.values())
            total_actual = health_data.get("total_routes", 0)

            # Account for main router routes
            if total_actual < total_expected:
                return ValidationResult(
                    "Route Counts",
                    False,
                    f"Total routes too low: expected at least {total_expected}, got {total_actual}"
                )

            return ValidationResult(
                "Route Counts",
                True,
                f"All route counts match expectations: {total_actual} total routes",
                {"routes_by_module": routes_by_module, "total_routes": total_actual}
            )

        except Exception as e:
            return ValidationResult(
                "Route Counts",
                False,
                f"Route count validation error: {e}"
            )

    def validate_feature_flags(self) -> ValidationResult:
        """Validate feature flag configuration."""
        try:
            response = self.session.get(f"{self.base_url}/api/image-studio/health")
            response.raise_for_status()
            data = response.json()

            feature_flags = data.get("feature_flags", {})
            expected_features = ["generation", "editing", "advanced", "utilities"]

            for feature in expected_features:
                if feature not in feature_flags:
                    return ValidationResult(
                        "Feature Flags",
                        False,
                        f"Missing feature flag: {feature}",
                        {"available_flags": list(feature_flags.keys())}
                    )

            return ValidationResult(
                "Feature Flags",
                True,
                "All feature flags are properly configured",
                {"feature_flags": feature_flags}
            )

        except Exception as e:
            return ValidationResult(
                "Feature Flags",
                False,
                f"Feature flag validation error: {e}"
            )

    def validate_module_endpoints(self) -> ValidationResult:
        """Validate that key endpoints from each module are accessible."""
        test_endpoints = [
            ("generation", "/api/image-studio/providers"),
            ("editing", "/api/image-studio/edit/operations"),
            ("advanced", "/api/image-studio/face-swap/models"),
            ("utilities", "/api/image-studio/compress/formats")
        ]

        failed_endpoints = []

        for module, endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code not in [200, 401, 403]:  # 401/403 are OK (auth required)
                    failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {e})")

        if failed_endpoints:
            return ValidationResult(
                "Module Endpoints",
                False,
                f"Failed to access endpoints: {failed_endpoints}"
            )

        return ValidationResult(
            "Module Endpoints",
            True,
            "All module endpoints are accessible",
            {"tested_endpoints": len(test_endpoints)}
        )

    def validate_response_formats(self) -> ValidationResult:
        """Validate response formats are consistent."""
        try:
            # Test health endpoint response structure
            response = self.session.get(f"{self.base_url}/api/image-studio/health")
            response.raise_for_status()
            data = response.json()

            # Check for consistent response structure
            if not isinstance(data.get("status"), str):
                return ValidationResult(
                    "Response Formats",
                    False,
                    "Health endpoint missing or invalid 'status' field"
                )

            if not isinstance(data.get("service"), str):
                return ValidationResult(
                    "Response Formats",
                    False,
                    "Health endpoint missing or invalid 'service' field"
                )

            return ValidationResult(
                "Response Formats",
                True,
                "Response formats are consistent and properly structured"
            )

        except Exception as e:
            return ValidationResult(
                "Response Formats",
                False,
                f"Response format validation error: {e}"
            )

    def validate_error_handling(self) -> ValidationResult:
        """Validate error handling works correctly."""
        try:
            # Test with invalid endpoint
            response = self.session.get(f"{self.base_url}/api/image-studio/invalid-endpoint")
            if response.status_code != 404:
                return ValidationResult(
                    "Error Handling",
                    False,
                    f"Invalid endpoint returned {response.status_code}, expected 404"
                )

            # Check error response format
            try:
                error_data = response.json()
                if "error" not in error_data or "message" not in error_data:
                    return ValidationResult(
                        "Error Handling",
                        False,
                        "Error response missing required fields",
                        {"error_response": error_data}
                    )
            except:
                return ValidationResult(
                    "Error Handling",
                    False,
                    "Error response is not valid JSON"
                )

            return ValidationResult(
                "Error Handling",
                True,
                "Error handling provides proper responses"
            )

        except Exception as e:
            return ValidationResult(
                "Error Handling",
                False,
                f"Error handling validation failed: {e}"
            )

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        return {
            "validation_summary": {
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "success_rate": f"{sum(1 for r in self.results if r.passed) / len(self.results) * 100:.1f}%"
            },
            "results": [r.to_dict() for r in self.results],
            "target_url": self.base_url,
            "validation_timestamp": json.dumps(None)  # Would be datetime.now() in real implementation
        }


def main():
    """Main validation script entry point."""
    parser = argparse.ArgumentParser(description="Image Studio Refactoring Validation")
    parser.add_argument("--base-url", help="Base URL for API validation")
    parser.add_argument("--environment", choices=["development", "staging", "production"],
                       help="Target environment (alternative to --base-url)")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--output", choices=["console", "json"], default="console",
                       help="Output format")

    args = parser.parse_args()

    # Determine base URL
    if args.base_url:
        base_url = args.base_url
    elif args.environment:
        base_urls = {
            "development": "http://localhost:8000",
            "staging": "https://api-staging.alwrity.com",
            "production": "https://api.alwrity.com"
        }
        base_url = base_urls.get(args.environment, "http://localhost:8000")
    else:
        print("❌ Must specify either --base-url or --environment")
        sys.exit(1)

    # Create validator
    validator = ImageStudioValidator(base_url, args.api_key)

    # Run validation
    success = validator.run_all_validations()

    # Output results
    if args.output == "json":
        report = validator.generate_report()
        print(json.dumps(report, indent=2))
    else:
        # Console output already handled in run_all_validations
        pass

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()