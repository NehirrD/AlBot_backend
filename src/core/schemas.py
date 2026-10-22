#Shared Pydantic types used by several features' schemas.
#One mission: Converts decimal to JSON number
#Pydantic v2 writes Decimal as a string in JSON
from decimal import Decimal
from typing import Annotated
from pydantic import PlainSerializer

JsonDecimal = Annotated[
    Decimal, PlainSerializer(float, return_type=float, when_used="json")
]