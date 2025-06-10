import os
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
	def generate_api_tests_in_json_format(self) -> Task:
		return Task(
			config=self.tasks_config['generate_api_tests_task'],
			output_file='output/generated_tests.json',
			max_retries=0,
			#output_pydantic=GeneratedTests
		)

	@task
	def generate_api_tests_in_pytest_format(self) -> Task:
		return Task(
			config=self.tasks_config['generate_api_pytest_task'],
			output_file='output/cat_api_tests.py',
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

	@task
	def analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['test_analysis_task'],
			max_retries=0
		)

	@task
	def generate_bdd_tests_for_ticket_id(self) -> Task:
		return Task(
			config=self.tasks_config['get_bdd_test_for_ticket_id'],
			output_file='output/bdd_tests.json',
			max_retries=0
		)
	@task
	def extract_bdd_scenarios(self) -> Task:
		return Task(
			config=self.tasks_config['extract_bdd_scenarios'],
			output_file='output/bdd_scenarios.feature',
			max_retries=0
		)

	@task
	def ui_execution_task(self) -> Task:
		return Task(
			config=self.tasks_config['ui_test_executor_task'],
			max_retries=0
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the QA Agent Analyst crew"""

		return Crew(
			agents=[self.software_qa_engineer()],
			tasks=[self.extract_api_information(), self.generate_api_tests_in_json_format(), self.generate_api_tests_in_pytest_format()], # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			knowledge_sources=[self.csv_source],
			embedder={
				"provider": "google",
				"config": {
					"model": "models/text-embedding-004",
					"api_key": GEMINI_API_KEY,
				}
			}
		)