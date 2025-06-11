#!/usr/bin/env python
import json
import os
from logging import getLogger
from pydantic import BaseModel

from crewai.flow import Flow, listen, start, router

from software_qe_flow.crews.api_testing_crew.api_testing_crew import ApiTestingCrew
from software_qe_flow.utils import read_file
from enum import Enum



class ActivityType(str, Enum):
    NONE = ""
    GENERATE_TEST = "generate_test"
    EXECUTE_TEST = "execute_test"
    ANALYZE_RESULTS = "analyze_results"

class TestActivityState(BaseModel):
    project: str = ""
    test_type: str = ""
    api_schema_path: str = ""
    api_schema: dict | None = None
    api_under_test: str = ""
    activity_type: ActivityType = ActivityType.NONE
    result: str = ""

class ApiTestFlow(Flow[TestActivityState]):

    @start()
    def read_test_type(self):
        print("Reading test type from state")
        if not self.state.test_type:
            raise ValueError("Test type is not specified in the state")
        print(f"Test type: {self.state.test_type}")
        if self.state.test_type.upper() == "API":
            # if test type is API, you might want to do some initial setup or validation or adding secrets etc.
            return "read_schema"
        else:
            raise ValueError(f"Unsupported test type: {self.state.test_type}")
    
    @router(read_test_type)
    def route_to_correct_type_of_testing_activities(self):
        print("Routing to correct type of testing activities")
        if self.state.test_type.upper() == "API":
            return "api_schema"
        else:
            return "ui_schema"  # Placeholder for other test types

    @listen("ui_schema")
    def read_ui_schema(self):
        print("Reading UI schema, but this is not implemented yet")
        raise NotImplementedError("UI schema reading is not implemented yet")

    @listen("api_schema")
    def read_api_schema(self):
        print("Reading API schema at:", self.state.api_schema_path)
        schema_path = os.path.join(os.path.dirname(__file__), "../../", self.state.api_schema_path)
        print(f"Schema path: {schema_path}")
        schema_contents = read_file(schema_path)
        if not schema_contents:
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
        self.state.api_schema = json.loads(schema_contents)
    
    @router(read_api_schema)
    def route_to_correct_api_detect_methods(self):
        print("Reading API under test")
        if not self.state.api_under_test:
            raise ValueError("API under test is not specified")
        if self.state.api_under_test.upper() == "ALL":
            return "all_methods_tests"
        elif self.state.api_under_test.find(",") != -1:
            return "multiple_methods_tests"
        else:
            return "single_method_test"

    @listen("multiple_methods_tests")
    def generate_tests_for_multiple_methods(self):
        print("Generating tests for multiple methods")
        api_testing_crew = ApiTestingCrew().crew(num_of_apis=self.state.api_under_test, activity_type=self.state.activity_type)
        input_sets = []
        for api in self.state.api_under_test.split(","):
            input_sets.append({'apiUnderTest': api.strip(), 'schema': self.state.api_schema})
        result = (
            api_testing_crew
            .kickoff_for_each(inputs=input_sets)
        )
        for res in result:
            print(f"Result: {res}")
        print("Crew Usage Metrics:", api_testing_crew.usage_metrics)
        self.state.result = result
    
    @listen("all_methods_tests")
    def generate_tests_for_all_methods(self):
        print("Generating tests for all methods")
        api_testing_crew = ApiTestingCrew().crew(num_of_apis=self.state.api_under_test, activity_type=self.state.activity_type)
        result = (
            api_testing_crew
            .kickoff(inputs={'apiUnderTest': self.state.api_under_test, 'schema': self.state.api_schema})
        )
        print("Tests generated", result)
        print("Crew Usage Metrics:", api_testing_crew.usage_metrics)
        self.state.result = result

    @listen("single_method_test")
    def generate_test_for_one_api(self):
        print("Generating test for a single API method:", self.state.api_under_test)
        api_testing_crew = ApiTestingCrew().crew(num_of_apis=self.state.api_under_test, activity_type=self.state.activity_type)
        result = (
            api_testing_crew
            .kickoff(inputs={'apiUnderTest': self.state.api_under_test, 'schema': self.state.api_schema})
        )
        print("Tests generated", result.raw)
        print("Crew Usage Metrics:", api_testing_crew.usage_metrics)
        self.state.result = result


def kickoff():
    test_flow = ApiTestFlow()
    api_under_test = "/pet/findByStatus, /pet/{petId}"  
    #api_under_test = "ALL"
    #api_under_test = "/pet/{petId}" 
    test_flow.kickoff(inputs={
        "project": "petstore",
        "test_type": "API",
        "api_schema_path": "schema/petstore/openapi.json",
        "api_under_test": api_under_test,
        "activity_type": ActivityType.GENERATE_TEST
    })


def plot():
    test_flow = ApiTestFlow()
    test_flow.plot()


if __name__ == "__main__":
    kickoff()
    plot()
