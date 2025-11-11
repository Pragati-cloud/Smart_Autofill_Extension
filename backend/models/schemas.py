from pydantic import BaseModel
from typing import Dict

class AttributeRequest(BaseModel):
    attributes: Dict[str, str]
    company_type: str
