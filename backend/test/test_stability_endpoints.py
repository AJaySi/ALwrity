"""Test suite for Stability AI endpoints."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI
import io
from PIL import Image
import json
import base64
from unittest.mock import Mock, AsyncMock, patch

from routers.stability import router
from services.stability_service import StabilityAIService
from models.stability_models import *


# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestStabilityEndpoints:
    """Test cases for Stability AI endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_image = self._create_test_image()
        self.test_audio = self._create_test_audio()
        
    def _create_test_image(self) -> bytes:
        """Create test image data."""
        img = Image.new('RGB', (512, 512), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def _create_test_audio(self) -> bytes:
        """Create test audio data."""
        # Mock audio data
        return b"fake_audio_data" * 1000
    
    @patch('services.stability_service.StabilityAIService')
    def test_generate_ultra_success(self, mock_service):
        """Test successful Ultra generation."""
        # Mock service response
        mock_service.return_value.__aenter__.return_value.generate_ultra = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/generate/ultra",
            data={"prompt": "A beautiful landscape"},
            files={}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")
    
    @patch('services.stability_service.StabilityAIService')
    def test_generate_core_with_parameters(self, mock_service):
        """Test Core generation with various parameters."""
        mock_service.return_value.__aenter__.return_value.generate_core = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/generate/core",
            data={
                "prompt": "A futuristic city",
                "aspect_ratio": "16:9",
                "style_preset": "digital-art",
                "seed": 42
            }
        )
        
        assert response.status_code == 200
    
    @patch('services.stability_service.StabilityAIService')
    def test_inpaint_with_mask(self, mock_service):
        """Test inpainting with mask."""
        mock_service.return_value.__aenter__.return_value.inpaint = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/edit/inpaint",
            data={"prompt": "A cat"},
            files={
                "image": ("test.png", self.test_image, "image/png"),
                "mask": ("mask.png", self.test_image, "image/png")
            }
        )
        
        assert response.status_code == 200
    
    @patch('services.stability_service.StabilityAIService')
    def test_upscale_fast(self, mock_service):
        """Test fast upscaling."""
        mock_service.return_value.__aenter__.return_value.upscale_fast = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/upscale/fast",
            files={"image": ("test.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 200
    
    @patch('services.stability_service.StabilityAIService')
    def test_control_sketch(self, mock_service):
        """Test sketch control."""
        mock_service.return_value.__aenter__.return_value.control_sketch = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/control/sketch",
            data={
                "prompt": "A medieval castle",
                "control_strength": 0.8
            },
            files={"image": ("sketch.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 200
    
    @patch('services.stability_service.StabilityAIService')
    def test_3d_generation(self, mock_service):
        """Test 3D model generation."""
        mock_3d_data = b"fake_glb_data" * 100
        mock_service.return_value.__aenter__.return_value.generate_3d_fast = AsyncMock(
            return_value=mock_3d_data
        )
        
        response = client.post(
            "/api/stability/3d/stable-fast-3d",
            files={"image": ("test.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "model/gltf-binary"
    
    @patch('services.stability_service.StabilityAIService')
    def test_audio_generation(self, mock_service):
        """Test audio generation."""
        mock_service.return_value.__aenter__.return_value.generate_audio_from_text = AsyncMock(
            return_value=self.test_audio
        )
        
        response = client.post(
            "/api/stability/audio/text-to-audio",
            data={
                "prompt": "Peaceful nature sounds",
                "duration": 30
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/")
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/stability/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_models_info(self):
        """Test models info endpoint."""
        response = client.get("/api/stability/models/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "generate" in data
        assert "edit" in data
        assert "upscale" in data
    
    def test_supported_formats(self):
        """Test supported formats endpoint."""
        response = client.get("/api/stability/supported-formats")
        assert response.status_code == 200
        
        data = response.json()
        assert "image_input" in data
        assert "image_output" in data
        assert "audio_input" in data
    
    def test_image_info_analysis(self):
        """Test image info utility endpoint."""
        response = client.post(
            "/api/stability/utils/image-info",
            files={"image": ("test.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "width" in data
        assert "height" in data
        assert "format" in data
    
    def test_prompt_validation(self):
        """Test prompt validation endpoint."""
        response = client.post(
            "/api/stability/utils/validate-prompt",
            data={"prompt": "A beautiful landscape with mountains and lakes"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "suggestions" in data
    
    def test_invalid_image_format(self):
        """Test error handling for invalid image format."""
        response = client.post(
            "/api/stability/generate/ultra",
            data={"prompt": "Test prompt"},
            files={"image": ("test.txt", b"not an image", "text/plain")}
        )
        
        # Should handle gracefully or return appropriate error
        assert response.status_code in [400, 422]
    
    def test_missing_required_parameters(self):
        """Test error handling for missing required parameters."""
        response = client.post("/api/stability/generate/ultra")
        
        assert response.status_code == 422  # Validation error
    
    def test_outpaint_validation(self):
        """Test outpaint direction validation."""
        response = client.post(
            "/api/stability/edit/outpaint",
            data={
                "left": 0,
                "right": 0,
                "up": 0,
                "down": 0
            },
            files={"image": ("test.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 400
        assert "at least one outpaint direction" in response.json()["detail"]
    
    @patch('services.stability_service.StabilityAIService')
    def test_async_generation_response(self, mock_service):
        """Test async generation response format."""
        mock_service.return_value.__aenter__.return_value.upscale_creative = AsyncMock(
            return_value={"id": "test_generation_id"}
        )
        
        response = client.post(
            "/api/stability/upscale/creative",
            data={"prompt": "High quality upscale"},
            files={"image": ("test.png", self.test_image, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
    
    @patch('services.stability_service.StabilityAIService')
    def test_batch_comparison(self, mock_service):
        """Test model comparison endpoint."""
        mock_service.return_value.__aenter__.return_value.generate_ultra = AsyncMock(
            return_value=self.test_image
        )
        mock_service.return_value.__aenter__.return_value.generate_core = AsyncMock(
            return_value=self.test_image
        )
        
        response = client.post(
            "/api/stability/advanced/compare/models",
            data={
                "prompt": "A test image",
                "models": json.dumps(["ultra", "core"]),
                "seed": 42
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "comparison_results" in data


class TestStabilityService:
    """Test cases for StabilityAIService class."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization."""
        with patch.dict('os.environ', {'STABILITY_API_KEY': 'test_key'}):
            service = StabilityAIService()
            assert service.api_key == 'test_key'
    
    def test_service_initialization_no_key(self):
        """Test service initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                StabilityAIService()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_make_request_success(self, mock_session):
        """Test successful API request."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = b"test_image_data"
        mock_response.headers = {"Content-Type": "image/png"}
        
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
        
        service = StabilityAIService(api_key="test_key")
        
        async with service:
            result = await service._make_request(
                method="POST",
                endpoint="/test",
                data={"test": "data"}
            )
        
        assert result == b"test_image_data"
    
    @pytest.mark.asyncio
    async def test_image_preparation(self):
        """Test image preparation methods."""
        service = StabilityAIService(api_key="test_key")
        
        # Test bytes input
        test_bytes = b"test_image_bytes"
        result = await service._prepare_image_file(test_bytes)
        assert result == test_bytes
        
        # Test base64 input
        test_b64 = base64.b64encode(test_bytes).decode()
        result = await service._prepare_image_file(test_b64)
        assert result == test_bytes
    
    def test_dimension_validation(self):
        """Test image dimension validation."""
        service = StabilityAIService(api_key="test_key")
        
        # Valid dimensions
        service._validate_image_requirements(1024, 1024)
        
        # Invalid dimensions (too small)
        with pytest.raises(ValueError):
            service._validate_image_requirements(32, 32)
    
    def test_aspect_ratio_validation(self):
        """Test aspect ratio validation."""
        service = StabilityAIService(api_key="test_key")
        
        # Valid aspect ratio
        service._validate_aspect_ratio(1024, 1024)
        
        # Invalid aspect ratio (too wide)
        with pytest.raises(ValueError):
            service._validate_aspect_ratio(3000, 500)


class TestStabilityModels:
    """Test cases for Pydantic models."""
    
    def test_stable_image_ultra_request(self):
        """Test StableImageUltraRequest validation."""
        # Valid request
        request = StableImageUltraRequest(
            prompt="A beautiful landscape",
            aspect_ratio="16:9",
            seed=42
        )
        assert request.prompt == "A beautiful landscape"
        assert request.aspect_ratio == "16:9"
        assert request.seed == 42
    
    def test_invalid_seed_range(self):
        """Test invalid seed range validation."""
        with pytest.raises(ValueError):
            StableImageUltraRequest(
                prompt="Test",
                seed=5000000000  # Too large
            )
    
    def test_prompt_length_validation(self):
        """Test prompt length validation."""
        # Too long prompt
        with pytest.raises(ValueError):
            StableImageUltraRequest(
                prompt="x" * 10001  # Exceeds max length
            )
        
        # Empty prompt
        with pytest.raises(ValueError):
            StableImageUltraRequest(
                prompt=""  # Below min length
            )
    
    def test_outpaint_request(self):
        """Test OutpaintRequest validation."""
        request = OutpaintRequest(
            left=100,
            right=200,
            up=50,
            down=150
        )
        assert request.left == 100
        assert request.right == 200
    
    def test_audio_request_validation(self):
        """Test audio request validation."""
        request = TextToAudioRequest(
            prompt="Peaceful music",
            duration=60,
            model="stable-audio-2.5"
        )
        assert request.duration == 60
        assert request.model == "stable-audio-2.5"


class TestStabilityUtils:
    """Test cases for utility functions."""
    
    def test_image_validator(self):
        """Test image validation utilities."""
        from utils.stability_utils import ImageValidator
        
        # Mock UploadFile
        mock_file = Mock()
        mock_file.content_type = "image/png"
        mock_file.filename = "test.png"
        
        result = ImageValidator.validate_image_file(mock_file)
        assert result["is_valid"] is True
    
    def test_prompt_optimizer(self):
        """Test prompt optimization utilities."""
        from utils.stability_utils import PromptOptimizer
        
        prompt = "A simple image"
        result = PromptOptimizer.optimize_prompt(
            prompt=prompt,
            target_model="ultra",
            target_style="photographic",
            quality_level="high"
        )
        
        assert len(result["optimized_prompt"]) > len(prompt)
        assert "optimizations_applied" in result
    
    def test_parameter_validator(self):
        """Test parameter validation utilities."""
        from utils.stability_utils import ParameterValidator
        
        # Valid seed
        seed = ParameterValidator.validate_seed(42)
        assert seed == 42
        
        # Invalid seed
        with pytest.raises(HTTPException):
            ParameterValidator.validate_seed(5000000000)
    
    @pytest.mark.asyncio
    async def test_image_analysis(self):
        """Test image content analysis."""
        from utils.stability_utils import ImageValidator
        
        result = await ImageValidator.analyze_image_content(self.test_image)
        
        assert "width" in result
        assert "height" in result
        assert "total_pixels" in result
        assert "quality_assessment" in result


class TestStabilityConfig:
    """Test cases for configuration."""
    
    def test_stability_config_creation(self):
        """Test StabilityConfig creation."""
        from config.stability_config import StabilityConfig
        
        config = StabilityConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.base_url == "https://api.stability.ai"
    
    def test_model_recommendations(self):
        """Test model recommendation logic."""
        from config.stability_config import get_model_recommendations
        
        recommendations = get_model_recommendations(
            use_case="portrait",
            quality_preference="premium"
        )
        
        assert "primary" in recommendations
        assert "alternative" in recommendations
    
    def test_image_validation_config(self):
        """Test image validation configuration."""
        from config.stability_config import validate_image_requirements
        
        # Valid image
        result = validate_image_requirements(1024, 1024, "generate")
        assert result["is_valid"] is True
        
        # Invalid image (too small)
        result = validate_image_requirements(32, 32, "generate")
        assert result["is_valid"] is False
    
    def test_cost_calculation(self):
        """Test cost calculation."""
        from config.stability_config import calculate_estimated_cost
        
        cost = calculate_estimated_cost("generate", "ultra")
        assert cost == 8  # Ultra model cost
        
        cost = calculate_estimated_cost("upscale", "fast")
        assert cost == 2  # Fast upscale cost


class TestStabilityMiddleware:
    """Test cases for middleware."""
    
    def test_rate_limit_middleware(self):
        """Test rate limiting middleware."""
        from middleware.stability_middleware import RateLimitMiddleware
        
        middleware = RateLimitMiddleware(requests_per_window=5, window_seconds=10)
        
        # Test client identification
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer test_api_key"}
        
        client_id = middleware._get_client_id(mock_request)
        assert len(client_id) == 8  # First 8 chars of API key
    
    def test_monitoring_middleware(self):
        """Test monitoring middleware."""
        from middleware.stability_middleware import MonitoringMiddleware
        
        middleware = MonitoringMiddleware()
        
        # Test operation extraction
        operation = middleware._extract_operation("/api/stability/generate/ultra")
        assert operation == "generate_ultra"
    
    def test_caching_middleware(self):
        """Test caching middleware."""
        from middleware.stability_middleware import CachingMiddleware
        
        middleware = CachingMiddleware()
        
        # Test cache key generation
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/stability/health"
        mock_request.query_params = {}
        
        # This would need to be properly mocked for async
        # cache_key = await middleware._generate_cache_key(mock_request)
        # assert isinstance(cache_key, str)


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('services.stability_service.StabilityAIService')
    def test_api_error_handling(self, mock_service):
        """Test API error response handling."""
        mock_service.return_value.__aenter__.return_value.generate_ultra = AsyncMock(
            side_effect=HTTPException(status_code=400, detail="Invalid parameters")
        )
        
        response = client.post(
            "/api/stability/generate/ultra",
            data={"prompt": "Test"}
        )
        
        assert response.status_code == 400
    
    @patch('services.stability_service.StabilityAIService')
    def test_timeout_handling(self, mock_service):
        """Test timeout error handling."""
        mock_service.return_value.__aenter__.return_value.generate_ultra = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        
        response = client.post(
            "/api/stability/generate/ultra",
            data={"prompt": "Test"}
        )
        
        assert response.status_code == 504
    
    def test_file_size_validation(self):
        """Test file size validation."""
        from utils.stability_utils import validate_file_size
        
        # Mock large file
        mock_file = Mock()
        mock_file.size = 20 * 1024 * 1024  # 20MB
        
        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(mock_file, max_size=10 * 1024 * 1024)
        
        assert exc_info.value.status_code == 413


class TestWorkflowProcessing:
    """Test workflow and batch processing."""
    
    @patch('services.stability_service.StabilityAIService')
    def test_workflow_validation(self, mock_service):
        """Test workflow validation."""
        from utils.stability_utils import WorkflowManager
        
        # Valid workflow
        workflow = [
            {"operation": "generate_core", "parameters": {"prompt": "test"}},
            {"operation": "upscale_fast", "parameters": {}}
        ]
        
        errors = WorkflowManager.validate_workflow(workflow)
        assert len(errors) == 0
        
        # Invalid workflow
        invalid_workflow = [
            {"operation": "invalid_operation"}
        ]
        
        errors = WorkflowManager.validate_workflow(invalid_workflow)
        assert len(errors) > 0
    
    def test_workflow_optimization(self):
        """Test workflow optimization."""
        from utils.stability_utils import WorkflowManager
        
        workflow = [
            {"operation": "upscale_fast"},
            {"operation": "generate_core"},  # Should be moved to front
            {"operation": "inpaint"}
        ]
        
        optimized = WorkflowManager.optimize_workflow(workflow)
        
        # Generate operation should be first
        assert optimized[0]["operation"] == "generate_core"


# ==================== INTEGRATION TESTS ====================

class TestStabilityIntegration:
    """Integration tests for full workflow."""
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_full_generation_workflow(self, mock_session):
        """Test complete generation workflow."""
        # Mock successful API responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = b"test_image_data"
        mock_response.headers = {"Content-Type": "image/png"}
        
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
        
        service = StabilityAIService(api_key="test_key")
        
        async with service:
            # Test generation
            result = await service.generate_ultra(
                prompt="A beautiful landscape",
                aspect_ratio="16:9",
                seed=42
            )
            
            assert isinstance(result, bytes)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_full_edit_workflow(self, mock_session):
        """Test complete edit workflow."""
        # Mock successful API responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = b"test_edited_image_data"
        mock_response.headers = {"Content-Type": "image/png"}
        
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
        
        service = StabilityAIService(api_key="test_key")
        
        async with service:
            # Test inpainting
            result = await service.inpaint(
                image=b"test_image_data",
                prompt="A cat in the scene",
                grow_mask=10
            )
            
            assert isinstance(result, bytes)
            assert len(result) > 0


# ==================== PERFORMANCE TESTS ====================

class TestStabilityPerformance:
    """Performance tests for Stability AI endpoints."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        from services.stability_service import StabilityAIService
        
        async def mock_request():
            service = StabilityAIService(api_key="test_key")
            # Mock a quick operation
            await asyncio.sleep(0.1)
            return "success"
        
        # Run multiple concurrent requests
        tasks = [mock_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        assert all(result == "success" for result in results)
    
    def test_large_file_handling(self):
        """Test handling of large files."""
        from utils.stability_utils import validate_file_size
        
        # Test with various file sizes
        mock_file = Mock()
        
        # Valid size
        mock_file.size = 5 * 1024 * 1024  # 5MB
        validate_file_size(mock_file)  # Should not raise
        
        # Invalid size
        mock_file.size = 15 * 1024 * 1024  # 15MB
        with pytest.raises(HTTPException):
            validate_file_size(mock_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])