import os
from random import randint
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools.tools import CodeDocsSearchTool, FileReadTool
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from software_qe_flow.tools.qe_tools import invoke_api_tool
from software_qe_flow.models.api_tests_model import ApiInformation, GeneratedTests


GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    temperature=0,
)

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ApiTestingCrew():
	"""ApiTestingCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	csv_source = CSVKnowledgeSource(
		file_paths=["petstore_testdata.csv"]
	)

	@agent
	def software_qa_engineer(self) -> Agent:
		# open_api_json = FileReadTool(file_path='schema/openapi.json')
		return Agent(
			config=self.agents_config['software_qa_engineer'],
			verbose=True,
			llm=gemini_llm,
			max_iter=1,
			max_retry_limit=0,
			knowledge_sources=[self.csv_source],
			embedder= {
			"provider": "google",
				"config": {
					"model": "models/text-embedding-004",
					"api_key": GEMINI_API_KEY,
				}
			},
		)

	
	@task
	def extract_api_information(self) -> Task:
		return Task(
			config=self.tasks_config['extract_api_information'],
			output_pydantic=ApiInformation,
			output_file='output/api_information.json',
			max_retries=0,
			human_input=True
		)
	
	@task
	def extract_all_api_information(self) -> Task:
		return Task(
			config=self.tasks_config['extract_all_api_information'],
			output_pydantic=ApiInformation,
			output_file='output/api_information.json',
			max_retries=0,
			human_input=True
		)
	
	@task
	def generate_api_tests_in_json_format(self) -> Task:
		return Task(
			config=self.tasks_config['generate_api_tests_task'],
			output_file='output/generated_tests.json',
			max_retries=0,
			#output_pydantic=GeneratedTests
		)

	@task
	def generate_api_tests_in_pytest_format(self) -> Task:
		random_number = randint(1, 9999)
		output_file = f"output/cat_api_tests_{random_number}.py"
		return Task(
			config=self.tasks_config['generate_api_pytest_task'],
			output_file=output_file,
			max_retries=1,
			human_input=True
		)

	@task
	def api_execution_task(self) -> Task:
		return Task(
			config=self.tasks_config['api_test_task'],
			context=[self.extract_api_information()],
			max_retries=0
		)


	@crew
	def crew(self, num_of_apis:str, activity_type:str) -> Crew:
		"""Creates the QA Agent Analyst crew"""
		print(f"Params received in crew: {num_of_apis} and {activity_type}")
		identified_tasks = []
		
		if (num_of_apis == "ALL"):
			identified_tasks.extend([self.extract_all_api_information()])
		elif num_of_apis.find(",") != -1:
			identified_tasks.extend([self.extract_api_information(), self.generate_api_tests_in_json_format(), self.generate_api_tests_in_pytest_format()])
		else:
			identified_tasks.extend([self.extract_api_information(), self.generate_api_tests_in_json_format(), self.generate_api_tests_in_pytest_format(), self.api_execution_task()])	
		
		print(f"Tasks to be executed: {identified_tasks}")
		
		return Crew(
			agents=[self.software_qa_engineer()],
			tasks= identified_tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			knowledge_sources=[self.csv_source],
			embedder={
				"provider": "google",
				"config": {
					"model": "models/text-embedding-004",
					"api_key": GEMINI_API_KEY,
				}
			},
			output_log_file=True
		)
	