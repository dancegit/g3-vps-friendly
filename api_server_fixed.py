"""FastAPI server for Anthropic-compatible API with load balancing."""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from .core import ProviderManager, NoHealthyProvidersError, ProviderError
from .providers import MiniMaxProvider, VastAIProvider, KimiProvider
from .config import ConfigManager, load_config
from .providers.base_provider import UsageLimitExceededError

logger = logging.getLogger(__name__)


class APIServer:
    """FastAPI server with load balancing for Anthropic-compatible APIs."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize API server.

        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        self.provider_manager = ProviderManager(
            health_check_interval=self.config.load_balancing.health_check_interval_seconds
        )

        self.app = FastAPI(
            title="Anthropic Load Balancer",
            description="Anthropic-compatible API with automatic provider failover",
            version="1.0.0",
            lifespan=self._lifespan
        )

        self._setup_middleware()
        self._setup_routes()

    async def _lifespan(self, app: FastAPI):
        """Manage application lifespan events."""
        # Startup
        await self.initialize()
        logger.info("API server initialized and ready")
        yield
        # Shutdown
        logger.info("Shutting down API server...")
        await self.shutdown()
        logger.info("API server shutdown complete")

    def _setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        cors_origins = self.config.api.cors_origins or ["*"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Trusted host middleware
        trusted_hosts = ["*"]  # Configure appropriately for production
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )

    def _setup_routes(self) -> None:
        """Setup API routes."""
        # Health check
        self.app.get(
            self.config.monitoring.health_check_endpoint,
            status_code=status.HTTP_200_OK
        )(self.health_check)

        # Provider health dashboard
        self.app.get(
            self.config.monitoring.dashboard_endpoint,
            status_code=status.HTTP_200_OK
        )(self.provider_dashboard)

        # Models endpoint
        self.app.get(
            "/v1/models",
            status_code=status.HTTP_200_OK
        )(self.get_models)

        # Messages endpoint
        self.app.post(
            "/v1/messages",
            status_code=status.HTTP_200_OK
        )(self.create_message)

        # Legacy endpoints for compatibility
        self.app.post(
            "/v1/chat/completions",
            status_code=status.HTTP_200_OK
        )(self.create_chat_completion)

        # Provider management
        self.app.get(
            "/v1/providers",
            status_code=status.HTTP_200_OK
        )(self.get_providers)

    async def initialize(self) -> None:
        """Initialize the server and load providers."""
        # Load providers from configuration
        for provider_name, provider_config in self.config_manager.get_enabled_providers().items():
            try:
                provider = self._create_provider(provider_name, provider_config)
                await self.provider_manager.add_provider(provider)
                logger.info(f"Loaded provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to load provider '{provider_name}': {e}")

        # Start health monitoring
        await self.provider_manager.start_health_monitoring()

        logger.info("API server initialized with {} providers".format(
            len(self.provider_manager.providers)
        ))

    def _create_provider(self, name: str, config) -> MiniMaxProvider | VastAIProvider | KimiProvider:
        """Create a provider instance from configuration.

        Args:
            name: Provider name
            config: Provider configuration

        Returns:
            Provider instance
        """
        # Determine provider type and create appropriate instance
        if 'vastai' in name.lower():
            return VastAIProvider(
                name=name,
                priority=config.priority,
                config=config.dict()
            )
        elif 'kimi' in name.lower() or config.type == 'kimi':
            # Create Kimi provider for thinking specialist
            return KimiProvider(
                name=name,
                priority=config.priority,
                config=config.dict()
            )
        else:
            # Default to MiniMax provider
            return MiniMaxProvider(
                name=name,
                priority=config.priority,
                config=config.dict()
            )

    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint with detailed provider statistics.

        Returns:
            Health status information including provider details and usage statistics
        """
        stats = self.provider_manager.get_provider_stats()
        current_time = time.time()

        # Build provider list with names and usage stats
        provider_details = []
        for provider_stats in stats["providers"]:
            provider_info = {
                "name": provider_stats["name"],
                "type": provider_stats["type"],
                "priority": provider_stats["priority"],
                "enabled": provider_stats["enabled"],
                "healthy": provider_stats["healthy"],
                "available": provider_stats["available"],
                "usage": {
                    "total": provider_stats["usage_count_total"],
                    "last_hour": provider_stats["usage_count_last_hour"],
                    "limit": provider_stats["usage_limit"]
                }
            }

            # Add exhaust status if applicable
            if provider_stats["exhausted"]:
                provider_info["exhausted"] = True
                if "exhaustion_remaining_seconds" in provider_stats:
                    provider_info["retry_in_seconds"] = int(provider_stats["exhaustion_remaining_seconds"])

            # Add health check timestamp
            if provider_stats["last_health_check"]:
                provider_info["last_health_check_seconds_ago"] = int(current_time - provider_stats["last_health_check"])

            provider_details.append(provider_info)

        return {
            "status": "healthy",
            "timestamp": current_time,
            "uptime_seconds": current_time - getattr(self, "start_time", current_time),
            "providers": {
                "total": stats["total_providers"],
                "healthy": stats["healthy_providers"],
                "available": stats["available_providers"],
                "details": provider_details
            }
        }

    async def provider_dashboard(self) -> Dict[str, Any]:
        """Provider health dashboard endpoint.

        Returns:
            Detailed provider information
        """
        stats = self.provider_manager.get_provider_stats()

        # Calculate uptime (would need to track start time in real implementation)
        return {
            "status": "healthy",
            "timestamp": stats.get("timestamp", None),
            "load_balancer": {
                "strategy": self.config.load_balancing.strategy,
                "health_check_interval": self.config.load_balancing.health_check_interval_seconds,
                "quota_aware": self.config.load_balancing.quota_aware
            },
            "providers": stats["providers"]
        }

    async def get_models(self, request: Request) -> Dict[str, Any]:
        """Get available models from the best provider.

        Args:
            request: FastAPI request

        Returns:
            Models response

        Raises:
            HTTPException: If no models can be retrieved
        """
        try:
            # Try to get models from all providers
            all_models = await self.provider_manager.get_models_from_all_providers()

            # Find the best provider's models
            healthy_providers = self.provider_manager.get_healthy_providers()
            if not healthy_providers:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No healthy providers available"
                )

            # Use the highest priority healthy provider
            best_provider = min(healthy_providers, key=lambda p: p.priority)
            models = all_models.get(best_provider.name, {})

            if "error" in models:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to get models: {models['error']}"
                )

            # Add provider information
            response = models.copy()
            response["_provider_info"] = {
                "name": best_provider.name,
                "type": best_provider.provider_type,
                "priority": best_provider.priority
            }

            return response

        except Exception as e:
            logger.error(f"Error getting models: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

    async def create_message(
        self,
        request: Request
    ) -> Response:
        """Create a message using the best available provider.

        Args:
            request: FastAPI request

        Returns:
            Streaming response or JSON response

        Raises:
            HTTPException: If request cannot be processed
        """
        try:
            # Parse request body
            body = await request.json()

            # Extract query parameters and merge with body
            # NOTE: Query parameters take precedence over body parameters
            query_params = dict(request.query_params)
            if query_params:
                logger.info(f"Extracted query parameters: {query_params}")
                # Filter out non-thinking parameters that clients might send
                # 'beta' is a normal Anthropic API parameter and not a thinking trigger
                filtered_params = {k: v for k, v in query_params.items() if k != 'beta'}
                if filtered_params:
                    body.update(filtered_params)

            # Extract parameters
            messages = body.get("messages", [])
            model = body.get("model")
            max_tokens = body.get("max_tokens")
            temperature = body.get("temperature")
            stream = body.get("stream", False)

            # Extract headers for thinking mode detection
            headers = dict(request.headers)

            # Add any additional parameters
            additional_params = {
                k: v for k, v in body.items()
                if k not in ["messages", "model", "max_tokens", "temperature", "stream"]
            }

            # Route to best provider
            if stream:
                # Handle streaming
                generator = self._create_streaming_generator(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    request_body=body,
                    headers=headers,
                    **additional_params
                )
                return StreamingResponse(
                    generator,
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Transfer-Encoding": "chunked"
                    }
                )
            else:
                # Handle non-streaming
                response = await self.provider_manager.route_create_message(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False,
                    request_body=body,
                    headers=headers,
                    **additional_params
                )

                return JSONResponse(content=response)

        except NoHealthyProvidersError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No healthy providers available"
            )
        except UsageLimitExceededError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Usage limit exceeded"
            )
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_chat_completion(
        self,
        request: Request
    ) -> Response:
        """Create a chat completion (OpenAI-compatible endpoint).

        Args:
            request: FastAPI request

        Returns:
            Streaming response or JSON response

        Raises:
            HTTPException: If request cannot be processed
        """
        try:
            # Parse request body
            body = await request.json()

            # Extract parameters
            messages = body.get("messages", [])
            model = body.get("model")
            max_tokens = body.get("max_tokens")
            temperature = body.get("temperature")
            stream = body.get("stream", False)

            # Extract headers for thinking mode detection
            headers = dict(request.headers)

            # Convert to Anthropic format
            anthropic_messages = self._convert_openai_to_anthropic(messages)

            # Route to provider
            if stream:
                generator = self._create_streaming_generator(
                    messages=anthropic_messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    headers=headers
                )
                return StreamingResponse(
                    generator,
                    media_type="text/event-stream"
                )
            else:
                response = await self.provider_manager.route_create_message(
                    messages=anthropic_messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False,
                    headers=headers
                )

                # Convert back to OpenAI format
                openai_response = self._convert_anthropic_to_openai(response)
                return JSONResponse(content=openai_response)

        except Exception as e:
            logger.error(f"Error creating chat completion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def _convert_openai_to_anthropic(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI message format to Anthropic format.

        Args:
            messages: OpenAI format messages

        Returns:
            Anthropic format messages
        """
        anthropic_messages = []

        for message in messages:
            role = message.get("role")
            content = message.get("content", "")

            # Convert role
            if role == "system":
                # System messages become the first user message with special handling
                anthropic_messages.append({
                    "role": "user",
                    "content": f"System: {content}"
                })
            elif role == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": content
                })
            elif role == "assistant":
                anthropic_messages.append({
                    "role": "assistant",
                    "content": content
                })

        return anthropic_messages

    def _convert_anthropic_to_openai(self, anthropic_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Anthropic response to OpenAI format.

        Args:
            anthropic_response: Anthropic format response

        Returns:
            OpenAI format response
        """
        content = anthropic_response.get("content", [])
        if isinstance(content, list) and content:
            text_content = content[0].get("text", "")
        else:
            text_content = anthropic_response.get("text", "")

        return {
            "id": anthropic_response.get("id", ""),
            "object": "chat.completion",
            "created": anthropic_response.get("created", 0),
            "model": anthropic_response.get("model", ""),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text_content
                    },
                    "finish_reason": anthropic_response.get("stop_reason", "stop")
                }
            ],
            "usage": anthropic_response.get("usage", {})
        }

    async def _create_streaming_generator(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        request_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Create async generator for streaming responses.

        Args:
            messages: List of messages
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Temperature
            request_body: Original request body for thinking model detection
            headers: Optional HTTP headers for thinking mode detection
            **kwargs: Additional parameters

        Yields:
            Streaming response chunks
        """
        try:
            response = await self.provider_manager.route_create_message(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                request_body=request_body,
                headers=headers,
                **kwargs
            )

            # Handle streaming response
            if hasattr(response, '__aiter__'):
                # response is an AsyncGenerator - stream the actual content
                async for chunk in response:
                    if isinstance(chunk, str):
                        # Provider returns properly formatted SSE data
                        yield chunk
                    else:
                        # Provider returns raw data - format it
                        yield f"data: {json.dumps(chunk)}\n\n"
            else:
                # Fallback: provider returned a regular response, convert to streaming format
                logger.warning("Provider returned non-streaming response for streaming request, converting to SSE format")
                yield f"data: {json.dumps(response)}\n\n"
                yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    async def get_providers(self) -> Dict[str, Any]:
        """Get information about all providers.

        Returns:
            Provider information
        """
        return self.provider_manager.get_provider_stats()

    async def shutdown(self) -> None:
        """Shutdown the server and cleanup resources."""
        logger.info("Shutting down API server...")
        await self.provider_manager.close()

    def run(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """Run the server.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        # Use config values if not specified
        host = host or self.config.api.host
        port = port or self.config.api.port

        # Run server (initialization and shutdown handled by lifespan)
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=self.config.api.reload,
            log_level=self.config.api.log_level.lower(),
            access_log=True
        )


if __name__ == "__main__":
    # Run server directly
    server = APIServer()
    server.run()
