# Agentic Framework For Quality Engineering Tasks

Agentic framework to complete various API and UI test activities(Requirement analysis, test generation, test data integration, test execution). This is not generic framework but can be used as reference/boilerplate. It can be customized depending on your API and UI. As of now base application for API is https://petstore.swagger.io/. Need to build for UI yet.

## Folder Structure

```
software-qe-agentic-flow/
├── src/software_qe_flow/   # Agentic code
    ├── crews               # Source code for crews
    ├── models              # Data models that can be used as input/output to agents
    ├── tools               # Tools
    └── utils               # Utilities
├── knowledge/              # Knowledge sources/test data storage.
├── schema/                 # API schema for petstore
├── output/                 # Any output files that are generated.
├── main.py                 # Driver code
├── .env                    # environment file
├── pyproject.toml          # Python dependencies
└── README.md               # Project overview
```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/software-qe-agentic-flow.git
    cd software-qe-agentic-flow
    ```

2. Install dependencies (Ensure that `uv` is installed):
    ```bash
    uv sync
    ```

## LLM

As of now two LLMs are supported - Gemini LLM and Llama3.1:8b. To use, update the code in respective crew `api_testing_crew.py` and `ui_testing_crew.py`

## Usage

1. In case of Gemini usage, update .env file with your key. In case of Llama3.1, ensure that ollama is running on your system
2. Update the input values in `kickoff()` function of `main.py`
3. Run an example workflow:
    ```bash
    crewai run
    ```
4. You should see the console log as well as files generated in `output/` folder.

---

