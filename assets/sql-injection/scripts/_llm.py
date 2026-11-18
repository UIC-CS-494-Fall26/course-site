"""Shared LiteLLM wrapper for the fallback scripts.

LiteLLM routes one call to any provider. Pick the model with --model and set the
matching key in your environment, for example:
  OpenAI:    export OPENAI_API_KEY=...    --model gpt-4.1
  Anthropic: export ANTHROPIC_API_KEY=... --model claude-sonnet-4-5
  Google:    export GEMINI_API_KEY=...    --model gemini/gemini-2.5-pro
  Local:     ollama serve                 --model ollama/llama3.1
"""
import sys


def ask(model, system, user):
    try:
        import litellm
    except ImportError:
        sys.exit("litellm is missing. Run: pip install -r requirements.txt")
    resp = litellm.completion(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0,
    )
    return resp.choices[0].message.content
