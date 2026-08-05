from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    repository: str
    summary: str
    readme_length: int