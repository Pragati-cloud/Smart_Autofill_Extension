import os
import openai

openai.api_key = os.getenv("API_KEY")

def customize_for_autofill(parsed_json, platform="generic"):
    """
    Enhances parsed resume data with AI-generated autofill text.
    Works for LinkedIn, job portals, or custom forms.
    """
    try:
        prompt = f"""
        You are an AI that prepares short, professional autofill answers for online profiles.
        Given this resume data (JSON): {parsed_json}

        Platform: {platform}

        Generate:
        - Headline (max 10 words)
        - About summary (3-4 sentences)
        - Key strengths (comma-separated)
        - Work/Project summary (short)
        - Skills overview (1-line)

        Return valid JSON with these fields.
        """

        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        text = response["choices"][0]["message"]["content"].strip()
        return {"ai_generated": text}

    except Exception as e:
        return {"error": str(e)}
