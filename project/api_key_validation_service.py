from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class ApiKeyValidationResponse(BaseModel):
    """
    Provides the result of the API key validation attempt.
    """

    is_valid: bool
    user_id: Optional[str] = None
    message: str


async def api_key_validation(api_key: str) -> ApiKeyValidationResponse:
    """
    Validates API keys for accessing protected endpoints.

    Args:
        api_key (str): The API key that needs to be validated for access.

    Returns:
        ApiKeyValidationResponse: Provides the result of the API key validation attempt.

    This function checks if the provided API key exists in the database and is active. If the API key is valid and active,
    the function returns an ApiKeyValidationResponse object indicating successful validation, the user's ID associated with
    the API key, and a success message. If the API key is not valid or not active, the function returns an ApiKeyValidationResponse
    object indicating the failure of validation, no user ID, and a message describing the reason for the failure.
    """
    api_key_record = await prisma.models.ApiKey.prisma().find_unique(
        where={"key": api_key}, include={"User": True}
    )
    if not api_key_record or not api_key_record.isActive:
        return ApiKeyValidationResponse(
            is_valid=False, message="API key is invalid or not active."
        )
    return ApiKeyValidationResponse(
        is_valid=True,
        user_id=api_key_record.userId,
        message="API key validation successful.",
    )
