# AI on the Go

Welcome to AI on the Go! This project leverages cutting-edge AI to provide dynamic services directly through a web interface and a Telegram bot. Whether you're new to programming or an experienced developer, this guide will help you set up and contribute to the project effectively.

## Getting Started

### Prerequisites
- Python 3.11
- Poetry for dependency management

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://your-repository-url/ai-on-the-go.git
   cd ai-on-the-go
   
2. **Install Dependencies:**
Using Poetry, install all the required dependencies by running:
    ```bash
    poetry install
   
3. **Set up Pre-push Hooks:**
Ensure code quality and run tests before each commit by setting up pre-push hooks:
    ```bash
   cp path/to/your/project/directory/git_hooks/pre-push .git/hooks/
   # replace path/to/your/project/directory with your own path
   
Verify they are correctly installed:
    ```bash 
    ls -la .git/hooks/pre-push
    ```

### Running the Application
- **Start the Server:**
Launch the FastAPI server with:
    ```bash
    uvicorn ai_on_the_go.main:app --reload
  
- **Telegram Bot:**
To interact with the Telegram bot, set your API token in the environment variables and run:
    ```bash
    python ai_on_the_go/bot.py
### Testing
Run the unit and integration tests to ensure your setup is correct
```bash
   pytest
 ```

### Contributing
- **Create a Branch:**
Always work on a new branch for features or fixes:
    ```bash
    git checkout -b feature/JIRA-ID
    #example: feature/AIGO-23
- **Make Changes:** 
Implement your features or fixes.

- **Run Tests:**
Ensure all tests pass before committing:
    ```bash
    pytest
  
- **Commit and Push:**
After passing the tests, commit your changes:
    ```bash
    git commit -am "Add a meaningful commit message"
    git push origin your-new-branch-name
  
- **Open a Pull Request:**
Go to GitHub and open a pull request against the main branch.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments
Thanks to all contributors and maintainers.

Welcome aboard, and happy coding!