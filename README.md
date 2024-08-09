### README.md

# AI-Powered Proposal Generator

This project is an AI-powered proposal generator built using Python. It leverages various libraries and APIs to create comprehensive proposals for clients based on user input and uploaded documents.

## Features

- **Document Processing**: Extracts text from uploaded files (TXT, DOCX, PDF, XLSX).
- **AI-Powered Research**: Uses LangChain Agents to perform research based on user input.
- **Proposal Generation**: Generates a detailed proposal in DOCX format.
- **Review and Comment**: Allows users to review and comment on the draft proposal.
- **Proposal Improvement**: Uses an alternative LLM to improve the proposal based on user comments.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Calance_Proposal_Gen-main2.git
   cd Calance_Proposal_Gen-main2
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Setup Ollama Package[ follow: OllamaPackageInstallationSteps.txt]
4. Set up your environment variables (if needed) for API keys.
   
   
## Usage

1. Run the Streamlit app:
   ```sh
   streamlit run calancepropseAgnt2.py
   ```

2. Open your browser and navigate to the URL provided by Streamlit.

3. Follow the on-screen instructions to input client details, project requirements, and upload relevant documents.

4. Generate, review, and download the proposal.

## Dependencies

- `streamlit`
- `langchain`
- `langchain_community`
- `openai`
- `docx`
- `fitz`
- `openpyxl`
- `logging`
- `duckduckgo-search`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

