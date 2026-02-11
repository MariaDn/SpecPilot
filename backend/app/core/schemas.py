from pydantic import BaseModel, Field, validator
from typing import List, Dict

class TZSection(BaseModel):
  code: str
  name: str
  content: str
  status: str = "complete"

class TZDocument(BaseModel):
  sections: List[TZSection]

  @validator('sections')
  def validate_all_sections_present(cls, v):
    expected_codes = [str(i) for i in range(1, 11)]
    received_codes = [s.code.split('.')[0] for s in v]
    
    missing = set(expected_codes) - set(received_codes)
    if missing:
      print(f"Warning: Missing sections: {missing}")
    return v