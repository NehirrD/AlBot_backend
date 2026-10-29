# Shared Pydantic types used by the DTOs of several features.
# One job: write Decimal values as JSON numbers.
# Pydantic v2 writes Decimal as a string in JSON by default.
from decimal import Decimal
from typing import Annotated
from pydantic import PlainSerializer

JsonDecimal = Annotated[
    Decimal, PlainSerializer(float, return_type=float, when_used="json")
]