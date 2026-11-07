PLAN_SYSTEM_PROMPT = """You extract shopping requirements from a user request.
Reply with ONLY a JSON object, no explanation, with these keys:
- "keywords": list of search keywords (strings)
- "requirements": object of minimum specs, e.g. {"min_ram_gb": 16, "gpu": "dedicated"}
- "max_price": number in TRY, or omit if the user gave no budget
"""