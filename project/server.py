import logging
from contextlib import asynccontextmanager

import project.api_key_validation_service
import project.interpret_emoji_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="test",
    lifespan=lifespan,
    description="To create an endpoint that connects to Groq and takes in an emoji as input to explain its meaning, you'll follow these steps:\n\n1. Initialize your FastAPI application by installing FastAPI and Uvicorn. Use `pip install fastapi uvicorn` for installation.\n2. Create a new file for your application, for instance, `app.py`, and import FastAPI to initiate the app object.\n3. Define an endpoint that accepts an emoji as input. Considering emojis are strings, this can be accomplished using a path or query parameter. Your endpoint might look like `@app.get(\"/emoji/{emoji_input}\")`.\n4. Within the defined endpoint, utilize the search information gathered earlier to interpret the emoji. You would typically use the 'emoji' Python library for converting the emoji to text, employing `emoji.demojize(emoji_input)`.\n5. Before connecting to Groq, it's important to understand that directly connecting to Groq to interpret emoji meanings may not be straightforward since Groq focuses on hardware acceleration and its APIs are more geared towards computational tasks rather than data interpretation or text analysis. Therefore, you may need to reconsider or clarify how Groq would be specifically utilized for interpreting emojis. If Groq provides an API for text analysis or any functionality that could be leveraged for emoji interpretation, integrate those API calls within your FastAPI route.\n6. Ensure your endpoint returns the interpreted meaning of the emoji, possibly with additional processing or analysis done through Groq if applicable and available.\n7. Run your FastAPI application with `uvicorn app:app --reload` command.\n\nNote: The direct usage of Groq for emoji interpretation requires further clarification. Groq's platform is primarily for accelerating computation-heavy tasks. It's suggested to explore Groq's documentation or support to understand if and how their API can be specifically used for text or emoji interpretation, aside from the computational tasks it's designed for.",
)


@app.post(
    "/api/auth/validate",
    response_model=project.api_key_validation_service.ApiKeyValidationResponse,
)
async def api_post_api_key_validation(
    api_key: str,
) -> project.api_key_validation_service.ApiKeyValidationResponse | Response:
    """
    Validates API keys for accessing protected endpoints.
    """
    try:
        res = await project.api_key_validation_service.api_key_validation(api_key)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/emoji/interpret/{emoji_input}",
    response_model=project.interpret_emoji_service.EmojiInterpretResponse,
)
async def api_get_interpret_emoji(
    emoji_input: str,
) -> project.interpret_emoji_service.EmojiInterpretResponse | Response:
    """
    Endpoint to receive an emoji input and return its interpretation.
    """
    try:
        res = await project.interpret_emoji_service.interpret_emoji(emoji_input)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
