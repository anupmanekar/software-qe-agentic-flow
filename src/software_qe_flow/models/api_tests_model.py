from pydantic import BaseModel, Field
from enum import Enum


class ApiInformation(BaseModel):
	"""Input schema for API test generation."""
	url: str = Field(..., description="URL of the API to generate tests for.")
	http_method: str = Field('GET', description="HTTP method to use for the request.")
	request_body: dict = Field({}, description="Request body to use for the request.")
	query_params: dict = Field({}, description="Query parameters to use for the request.")
	path_params: dict = Field({}, description="Path parameters to use for the request.")

class GeneratedTests(BaseModel):
    """Output schema for generated tests."""
    test_description: str = Field(..., description="Generated tests for the API.")
    url: str = Field(..., description="URL of the API to generate tests for.")
    http_method: str = Field('GET', description="HTTP method to use for the request.")
    request_body: dict = Field({}, description="Request body to use for the request.")
    query_params: dict = Field({}, description="Query parameters to use for the request.")
    path_params: dict = Field({}, description="Path parameters to use for the request.")
    expected_response_status_code: int = Field(200, description="Expected response status code for the API.")

class ActivityType(str, Enum):
    NONE = ""
    GENERATE_TEST = "generate_test"
    EXECUTE_TEST = "execute_test"
    ANALYZE_RESULTS = "analyze_results"