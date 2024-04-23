from typing import List, Optional

import emoji
import prisma
import prisma.models
from pydantic import BaseModel


class ComplexType(BaseModel):
    """
    A structured object containing additional context or insights related to the emoji interpretation.
    """

    related_emojis: List[str]
    usage_examples: List[str]
    sentiment_score: Optional[float] = None


class EmojiInterpretResponse(BaseModel):
    """
    This model outlines the structure of the response provided to the user after interpreting the emoji input. It includes fields for the original emoji, its textual interpretation, and additional context or insights where available.
    """

    original_emoji: str
    textual_interpretation: str
    additional_context: Optional[ComplexType] = None


async def interpret_emoji(emoji_input: str) -> EmojiInterpretResponse:
    """
    Endpoint to receive an emoji input and return its interpretation.

    Args:
    emoji_input (str): The Unicode emoji sent by the user for interpretation.

    Returns:
    EmojiInterpretResponse: This model outlines the structure of the response provided to the user after interpreting the emoji input. It includes fields for the original emoji, its textual interpretation, and additional context or insights where available.
    """
    textual_interpretation = emoji.demojize(emoji_input, language="en")
    query = await prisma.models.EmojiQuery.prisma().find_unique(
        where={"emoji": emoji_input}, include={"GroqAnalysis": True}
    )
    additional_context = None
    if query and query.GroqAnalysis:
        analysis = query.GroqAnalysis[0].analysisResult
        if analysis:
            analysis_result = dict(analysis) if analysis else {}
            related_emojis = analysis_result.get("related_emojis", [])
            usage_examples = analysis_result.get("usage_examples", [])
            sentiment_score = analysis_result.get("sentiment_score", None)
            additional_context = ComplexType(
                related_emojis=related_emojis,
                usage_examples=usage_examples,
                sentiment_score=sentiment_score,
            )
    response = EmojiInterpretResponse(
        original_emoji=emoji_input,
        textual_interpretation=textual_interpretation,
        additional_context=additional_context,
    )
    return response
