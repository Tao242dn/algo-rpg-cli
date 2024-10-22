# 🎮 AlgoRPG CLI

A command-line interface tool built with Algorand blockchain integration. Help learn Algorand effortlessly with our <b>AI powered by Gemini 1.5 Pro</b>. Get instant explanations, explore the blockchain, and master key concepts interactively.

## ✨ AI Features

- **Automated Code Generation**: Generate code for your projects effortlessly.

- **Conversation History**: Save and reset conversation histories as needed.

- **Code Review**: Analyze and review code files for quality and suggestions.

- **Enhanced File and Folder Management**: The `/add` and `/edit` commands now support adding and modifying both files and folders, providing greater flexibility in managing your project structure.

- **Project Planning**: Introducing the `/planning` command, which allows users to create comprehensive project plans that can be used to generate files and directories systematically.

- **Algo Explain and Explore**: The `/algo` command now includes two new subcommands: `/algo-explain` and `/algo-explore`. These commands allow users to explanation concept in Algorand blockchain and explore the Algorand blockchain, respectively.
  
## 🔧 Prerequisites

Before you begin, ensure you have met the following requirements:

- [AlgoKit](https://developer.algorand.org/docs/get-started/algokit/#install-algokit) installed
- [Python](https://www.python.org/downloads/) (3.12 or higher) installed
  
## 🛠️ Installation

Follow these steps to get the project up and running on your local machine:

1. Clone the repository:
   ```bash
   git clone https://github.com/Tao242dn/algo-rpg-cli.git
   cd algo-rpg-cli
   ```

2. Create a virtual environment:
   ```bash
   python -m venv env
   ```

3. Activate the virtual environment:
   - On Window:
     ```bash
     .\env\Scripts\activate
     ```
   - On MacOS and Linux:
     ```bash
     source env/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the SandBox:
   ```bash
   algokit localnet start
   ```

6. Create <b>.env</b> file

   ```env
   API_KEY=YOUR_API_KEY
   ALGO_ADDRESS=YOUR_FUND_ADDRESS
   TEMPLATE_URL=YOUR_TEMPLATE_URL
   ```

   - Using the Gemini API, you'll need an API key. If you don't already have one, create a key in [Google AI Studio](https://aistudio.google.com/app/apikey). Copy the API key and paste it to the `API_KEY` variable.

   - Running command below show the list of Algorand accounts on your machine.  Don't forget to run `algokit localnet start` before. Copy address with status `[online]` and paste it to the `ALGO_ADDRESS` variable.
      ```bash
      algokit goal account list
      ```

   - You can pass custom your template url to the `TEMPLATE_URL` variable. Default value is `https://github.com/Tao242dn/auction_template.git`.

   
7. Run the game:
   ```bash
   python main.py
   ```
