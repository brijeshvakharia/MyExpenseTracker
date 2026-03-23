import json

import anthropic

from app.config import settings


def categorize_transactions(descriptions: list[str], categories: list[str]) -> list[str]:
    """Use Claude API to categorize transaction descriptions into predefined categories.

    Args:
        descriptions: List of transaction descriptions to categorize.
        categories: List of valid category names.

    Returns:
        List of category names, one per description (same order).
    """
    if not descriptions:
        return []

    if not settings.anthropic_api_key:
        return ["Other"] * len(descriptions)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    results = ["Other"] * len(descriptions)

    # Process in batches of 50
    for batch_start in range(0, len(descriptions), 50):
        batch = descriptions[batch_start:batch_start + 50]
        batch_results = _categorize_batch(client, batch, categories)
        for i, cat in enumerate(batch_results):
            results[batch_start + i] = cat

    return results


def _categorize_batch(client: anthropic.Anthropic, descriptions: list[str], categories: list[str]) -> list[str]:
    """Categorize a single batch of up to 50 descriptions."""
    category_list = ", ".join(categories)
    numbered_list = "\n".join(f'{i + 1}. "{desc}"' for i, desc in enumerate(descriptions))

    prompt = f"""You are a financial transaction categorizer. Given a list of bank transaction descriptions, assign each one to exactly one of these categories: {category_list}

Return ONLY a valid JSON array where each element is an object with "index" (1-based) and "category" (must be one of the categories listed above).

Transactions:
{numbered_list}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Extract JSON from the response (handle markdown code blocks)
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        parsed = json.loads(text)
        result = ["Other"] * len(descriptions)
        for item in parsed:
            idx = item.get("index", 0) - 1
            cat = item.get("category", "Other")
            if 0 <= idx < len(descriptions) and cat in categories:
                result[idx] = cat
        return result

    except Exception:
        return ["Other"] * len(descriptions)
