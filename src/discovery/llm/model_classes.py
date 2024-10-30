from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ApiModel(BaseModel):
    """Model for an API"""

    url: str = Field(description="The URL of the API call")
    domain: str = Field(description="The domain of the API call")
    path: str = Field(description="The path of the API call")
    query_string: Optional[str] = Field(description="The query string of the API call")
    url_path_params: Optional[Dict[str, str]] = Field(description="The URL path parameters of the API call")
    method: str = Field(description="The HTTP method used in the API call, such as 'GET' or 'POST'")
    headers: Dict[str, str] = Field(description="The headers sent with the API call")
    postData: Optional[Dict[str, str]] = Field(description="The data sent with the API call, key-value pairs")

class ApiModelList(BaseModel):
    """Model for a list of APIs"""

    apis: List[ApiModel] = Field(description="The list of APIs")

class InteractionModel(BaseModel):
    """Model for an interaction"""

    name: str = Field(description="The name of the interaction")
    description: str = Field(description="The description of the interaction")
    input_fields: List[Dict[str, str]] = Field(description="The input fields of the interaction")

class InteractionModelList(BaseModel):
    """Model for a list of interactions"""

    interactions: List[InteractionModel] = Field(description="The list of interactions")


class RankedInteraction(BaseModel):
    """Model for ranked interaction"""

    interaction: str = Field(description="The name of the interaction")
    approaches: int = Field(description="The number of approaches to be genereated for the interaction")


class RankedInteractions(BaseModel):
    """Model for ranked interactions"""

    interactions_list: List[RankedInteraction] = Field(description="The list of interactions to be ranked")
