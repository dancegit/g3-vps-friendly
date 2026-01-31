"""MiniMax provider implementation for Anthropic-compatible API."""

from typing import Dict, Any, Optional, AsyncGenerator
import aiohttp
import asyncio
import logging

from .base_provider import BaseProvider, ProviderError, UsageLimitExceededError, HealthCheckError

logger = logging.getLogger(__name__)


class MiniMaxProvider(BaseProvider):
    """MiniMax provider supporting both subscription and pay-per-use modes.

    This provider can operate in two modes:
    1. Subscription: Uses minimax-m2 model (has usage limits)
    2. Pay-per-use: Uses minimax-m2-stable model (no usage limits, charges per request)
    """

    def __init__(self, name: str, priority: int, config: Dict[str, Any]):
        """Initialize MiniMax provider.

        Args:
            name: Provider name
            priority: Provider priority (lower number = higher priority)
            config: Provider configuration
        """
        super().__init__(name, priority, "subscription" if "subscription" in name.lower() else "pay_per_use", config)
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=int(self.config.get('env', {}).get('API_TIMEOUT_MS', 30000)) / 1000
            )
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def health_check(self) -> bool:
        """Perform health check on MiniMax API.

        Returns:
            True if healthy, False otherwise

        Raises:
            HealthCheckError: If health check fails
        """
        # Note: MiniMax API doesn't have /models endpoint
        # For now, mark as healthy and let actual requests determine health
        self._healthy = True
        self._last_health_check = 200
        logger.debug(f"MiniMax provider '{self.name}' marked as healthy (health check skipped)")
        return True

        # TODO: Implement proper health check using a valid endpoint
        # when MiniMax API documentation is available

    async def get_models(self) -> Dict[str, Any]:
        """Get available models from MiniMax.

        Returns:
            Dictionary containing model information

        Raises:
            ProviderError: If unable to retrieve models
        """
        # MiniMax API doesn't have a /models endpoint
        # Return mock Anthropic-compatible models for compatibility
        try:
            model_name = self.get_model_name()
            logger.debug(f"Returning mock models for provider '{self.name}' with model '{model_name}'")

            # Return mock models in Anthropic API format
            models = [
                {
                    "id": model_name,
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "minimax"
                },
                # Also include common Anthropic model aliases for compatibility
                {
                    "id": "claude-3-opus-20240229",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                },
                {
                    "id": "claude-3-sonnet-20240229",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                },
                {
                    "id": "claude-3-haiku-20240307",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                },
                {
                    "id": "claude-2.1",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                },
                {
                    "id": "claude-2",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                },
                {
                    "id": "claude-instant-1.2",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "anthropic"
                }
            ]

            return {
                "object": "list",
                "data": models
            }
        except Exception as e:
            logger.error(f"Error returning mock models for '{self.name}': {e}")
            raise ProviderError(f"Get models failed: {e}")

    async def create_message(
        self,
        messages: list,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a message using MiniMax API.

        Args:
            messages: List of message objects
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            API response dictionary

        Raises:
            ProviderError: If the request fails
            UsageLimitExceededError: If usage limit is exceeded
        """
        try:
            session = await self._get_session()
            url = f"{self.get_api_base()}/messages"

            # Build request payload
            payload = {
                "messages": messages,
                "model": model or self.get_model_name(),
            }

            if max_tokens is not None:
                payload["max_tokens"] = max_tokens

            if temperature is not None:
                payload["temperature"] = temperature

            # Add any additional parameters that MiniMax supports
            # Filter out problematic parameters that MiniMax rejects
            supported_kwargs = {}
            for k, v in kwargs.items():
                # Skip parameters that commonly cause 400 errors with MiniMax
                # These are either unsupported or should have specific formats
                if k not in ["metadata", "stop_sequences", "top_p", "top_k"]:
                    supported_kwargs[k] = v

            payload.update(supported_kwargs)

            # Build headers
            headers = self.get_headers()
            if 'x-api-key' in headers:
                headers['Authorization'] = f"Bearer {self.get_auth_token()}"
            elif 'Authorization' not in headers:
                headers['Authorization'] = f"Bearer {self.get_auth_token()}"

            # Add stream header if needed
            if stream:
                headers['Accept'] = 'text/event-stream'

            logger.debug(
                f"Sending request to MiniMax provider '{self.name}', "
                f"model={payload['model']}, stream={stream}"
            )

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    self.increment_usage()
                    if stream:
                        return await self._handle_stream_response(response)
                    else:
                        data = await response.json()
                        logger.info(
                            f"Successfully created message with provider '{self.name}', "
                            f"usage count: {self.usage_count}"
                        )
                        return data
                else:
                    error_text = await response.text()
                    try:
                        error_data = await response.json()
                        if self.parse_usage_limit_error(error_data):
                            logger.warning(
                                f"Usage limit exceeded for provider '{self.name}' "
                                f"(HTTP {response.status})"
                            )
                            raise UsageLimitExceededError(
                                f"Usage limit exceeded: {error_text}"
                            )
                    except UsageLimitExceededError:
                        # Re-raise usage limit errors to trigger proper failover
                        raise
                    except Exception:
                        # Other parsing errors, continue to regular error handling
                        pass

                    logger.error(
                        f"MiniMax API error (provider '{self.name}'): "
                        f"HTTP {response.status} - {error_text}"
                    )

                    # Provide more specific error types for better failover handling
                    if response.status >= 500:
                        # 5xx errors are server-side issues, likely transient
                        raise ProviderError(
                            f"Upstream server error (HTTP {response.status}): {error_text}"
                        )
                    elif response.status >= 400:
                        # 4xx errors are client-side, likely permanent
                        raise ProviderError(
                            f"Client request error (HTTP {response.status}): {error_text}"
                        )
                    else:
                        raise ProviderError(
                            f"API request failed: HTTP {response.status} - {error_text}"
                        )
        except UsageLimitExceededError:
            raise
        except Exception as e:
            logger.error(f"Error creating message with '{self.name}': {e}")
            raise ProviderError(f"Create message failed: {e}")

    async def _handle_stream_response(self, response) -> AsyncGenerator[str, None]:
        """Handle streaming response from MiniMax API.

        Args:
            response: aiohttp response object

        Yields:
            Server-sent events formatted chunks
        """
        try:
            # Process the streaming response
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    # Already properly formatted SSE data
                    yield line + '\n'
                elif line == '':
                    # Empty line, skip
                    continue
                elif line == '[DONE]':
                    # End of stream marker
                    yield 'data: [DONE]\n\n'
                    break
                else:
                    # Raw data, wrap in SSE format
                    if line != '[DONE]':
                        yield f'data: {line}\n\n'
                    else:
                        yield 'data: [DONE]\n\n'
                        break
        except Exception as e:
            logger.error(f"Error processing streaming response: {e}")
            yield f'data: {{"error": "{str(e)}"}}\n\n'

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            try:
                # Properly close the session - close() returns a coroutine in some versions
                close_coro = self._session.close()
                if close_coro is not None and asyncio.iscoroutine(close_coro):
                    await close_coro
                # Give aiohttp time to close connections
                await asyncio.sleep(0.1)
                logger.debug(f"Closed aiohttp session for provider '{self.name}'")
            except Exception as e:
                logger.warning(f"Error closing session for provider '{self.name}': {e}")

    def get_usage_limit_error_codes(self) -> list:
        """Get error codes that indicate usage limit exceeded.

        Returns:
            List of error codes/strings that indicate usage limits
        """
        return ['2056', 'usage_limit_exceeded', 'quota_exceeded', 'rate_limit_exceeded']

    def __str__(self) -> str:
        """String representation of MiniMax provider."""
        mode = "subscription" if self.provider_type == "subscription" else "pay-per-use"
        exhausted_str = ", exhausted" if self.is_exhausted() else ""
        return (
            f"MiniMaxProvider(name='{self.name}', mode='{mode}', "
            f"priority={self.priority}, healthy={self._healthy}{exhausted_str}, "
            f"usage={self.usage_count}/{self.usage_limit or 'unlimited'})"
        )
