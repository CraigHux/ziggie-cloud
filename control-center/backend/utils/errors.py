"""
User-Friendly Error Handling Module
Maps technical errors to user-friendly messages
"""

from fastapi import HTTPException
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UserFriendlyError:
    """Maps technical errors to user-friendly messages"""

    ERROR_MESSAGES = {
        # File system errors
        "FileNotFoundError": "The requested file could not be found.",
        "PermissionError": "Access denied. You don't have permission to access this resource.",
        "IsADirectoryError": "Expected a file but found a directory.",
        "NotADirectoryError": "Expected a directory but found a file.",

        # Network and connectivity errors
        "ConnectionError": "Unable to connect to the service. Please try again later.",
        "ConnectionRefusedError": "Unable to connect to the service. Please check if it's running.",
        "TimeoutError": "The operation took too long. Please try again.",
        "TimeoutExpired": "The operation took too long. Please try again.",

        # Data validation errors
        "ValueError": "Invalid input provided. Please check your data.",
        "TypeError": "Invalid data type provided. Please check your input.",
        "KeyError": "Required information is missing.",
        "JSONDecodeError": "Invalid data format. Please check your input.",

        # Process and subprocess errors
        "ProcessLookupError": "The requested process could not be found.",
        "ChildProcessError": "Failed to execute the requested operation.",

        # Git-related errors
        "CalledProcessError": "The requested operation failed. Please check the configuration.",

        # Database errors
        "IntegrityError": "Data validation failed. Please check for duplicate entries.",
        "OperationalError": "Database operation failed. Please try again.",

        # Default fallback
        "default": "An unexpected error occurred. Please try again or contact support."
    }

    @staticmethod
    def handle_error(
        e: Exception,
        context: str = "",
        status_code: int = 500,
        include_debug: Optional[bool] = None
    ):
        """
        Convert technical exception to user-friendly HTTPException

        Args:
            e: The original exception
            context: Additional context (e.g., "while starting service")
            status_code: HTTP status code to return
            include_debug: Whether to include technical details (overrides settings.DEBUG)
        """
        from config import settings

        error_type = type(e).__name__
        user_message = UserFriendlyError.ERROR_MESSAGES.get(
            error_type,
            UserFriendlyError.ERROR_MESSAGES["default"]
        )

        # Add context if provided
        if context:
            user_message = f"{user_message} ({context})"

        # Log the actual technical error for debugging
        logger.error(
            f"Error in {context}: {error_type}: {str(e)}",
            exc_info=True,
            extra={
                "error_type": error_type,
                "context": context,
                "status_code": status_code
            }
        )

        # In development mode, include technical details
        should_include_debug = include_debug if include_debug is not None else settings.DEBUG

        if should_include_debug:
            debug_info = {
                "error_type": error_type,
                "error_message": str(e),
                "context": context
            }
            detail = {
                "message": user_message,
                "debug": debug_info
            }
        else:
            detail = user_message

        # Return user-friendly message
        raise HTTPException(status_code=status_code, detail=detail)

    @staticmethod
    def not_found(resource: str, resource_id: str = ""):
        """
        Raise a user-friendly 404 error

        Args:
            resource: The type of resource (e.g., "Agent", "Service", "File")
            resource_id: The ID or identifier of the resource
        """
        if resource_id:
            message = f"{resource} '{resource_id}' not found."
        else:
            message = f"{resource} not found."

        logger.warning(f"Resource not found: {resource} {resource_id}")
        raise HTTPException(status_code=404, detail=message)

    @staticmethod
    def validation_error(message: str, field: Optional[str] = None):
        """
        Raise a user-friendly validation error

        Args:
            message: The validation error message
            field: The field that failed validation (optional)
        """
        if field:
            full_message = f"Validation error for '{field}': {message}"
        else:
            full_message = f"Validation error: {message}"

        logger.warning(full_message)
        raise HTTPException(status_code=400, detail=full_message)

    @staticmethod
    def unauthorized(message: str = "Authentication required"):
        """Raise a user-friendly 401 error"""
        logger.warning(f"Unauthorized access attempt: {message}")
        raise HTTPException(status_code=401, detail=message)

    @staticmethod
    def forbidden(message: str = "Access denied"):
        """Raise a user-friendly 403 error"""
        logger.warning(f"Forbidden access attempt: {message}")
        raise HTTPException(status_code=403, detail=message)

    @staticmethod
    def service_unavailable(service: str):
        """
        Raise a user-friendly 503 error for service unavailability

        Args:
            service: The name of the unavailable service
        """
        message = f"The {service} service is currently unavailable. Please try again later."
        logger.error(f"Service unavailable: {service}")
        raise HTTPException(status_code=503, detail=message)


# Convenience functions for common error scenarios
def handle_file_error(e: Exception, file_path: str):
    """Handle file-related errors with file path context"""
    UserFriendlyError.handle_error(
        e,
        context=f"accessing file: {file_path}",
        status_code=404 if isinstance(e, FileNotFoundError) else 500
    )


def handle_service_error(e: Exception, service_name: str, operation: str):
    """Handle service-related errors"""
    UserFriendlyError.handle_error(
        e,
        context=f"{operation} service '{service_name}'",
        status_code=500
    )


def handle_database_error(e: Exception, operation: str):
    """Handle database-related errors"""
    UserFriendlyError.handle_error(
        e,
        context=f"database {operation}",
        status_code=500
    )
