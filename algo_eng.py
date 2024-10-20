import os
import fnmatch
import logging
import time
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerationConfig
from termcolor import colored
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from rich import print as rprint
from rich import box
from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import difflib
import re
import json  # For handling JSON data
from algosdk.v2client import algod, indexer # Algorand SDK

load_dotenv('.env')
console = Console()

# Initialize Gemini client
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

logging.basicConfig(filename='algo_eng.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"  # Replace with your Algod address we are using testnet
ALGOD_TOKEN = "a" * 64
INDEXER_ADDRESS = "https://testnet-idx.algonode.cloud" # Replace with your indexer address we are using testnet
INDEXER_TOKEN = "a" * 64

algo_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ADDRESS)


CREATE_SYSTEM_PROMPT = """You are an advanced Algo engineer designed to create files and folders based on user instructions. Your primary objective is to generate the content of the files to be created as code blocks. Each code block should specify whether it's a file or folder, along with its path.

When given a user request, perform the following steps:

1. Understand the User Request: Carefully interpret what the user wants to create.
2. Generate Creation Instructions: Provide the content for each file to be created within appropriate code blocks. Each code block should begin with a special comment line that specifies whether it's a file or folder, along with its path.
3. You create full functioning, complete,code files, not just snippets. No approximations or placeholders. FULL WORKING CODE.

IMPORTANT: Your response must ONLY contain the code blocks with no additional text before or after. Do not use markdown formatting outside of the code blocks. Use the following format for the special comment line. Do not include any explanations, additional text:

For folders:
```
### FOLDER: path/to/folder
```

For files:
```language
### FILE: path/to/file.extension
File content goes here...
```

Example of the expected format:

```
### FOLDER: new_app
```

```html
### FILE: new_app/index.html
<!DOCTYPE html>
<html>
<head>
    <title>New App</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>
```

```css
### FILE: new_app/styles.css
body {
    font-family: Arial, sans-serif;
}
```

```javascript
### FILE: new_app/script.js
console.log('Hello, World!');
```

Ensure that each file and folder is correctly specified to facilitate seamless creation by the script."""


CODE_REVIEW_PROMPT = """You are an expert code reviewer. Your task is to analyze the provided code files and provide a comprehensive code review. For each file, consider:

1. Code Quality: Assess readability, maintainability, and adherence to best practices
2. Potential Issues: Identify bugs, security vulnerabilities, or performance concerns
3. Suggestions: Provide specific recommendations for improvements

Format your review as follows:
1. Start with a brief overview of all files
2. For each file, provide:
   - A summary of the file's purpose
   - Key findings (both positive and negative)
   - Specific recommendations
3. End with any overall suggestions for the codebase

Your review should be detailed but concise, focusing on the most important aspects of the code."""


EDIT_INSTRUCTION_PROMPT = """You are an advanced Algo engineer designed to analyze files and provide edit instructions based on user requests. Your task is to:

1. Understand the User Request: Carefully interpret what the user wants to achieve with the modification.
2. Analyze the File(s): Review the content of the provided file(s).
3. Generate Edit Instructions: Provide clear, step-by-step instructions on how to modify the file(s) to address the user's request.

Your response should be in the following format:

```
File: [file_path]
Instructions:
1. [First edit instruction]
2. [Second edit instruction]
...

File: [another_file_path]
Instructions:
1. [First edit instruction]
2. [Second edit instruction]
...
```

Only provide instructions for files that need changes. Be specific and clear in your instructions."""


APPLY_EDITS_PROMPT = """
Rewrite an entire file or files using edit instructions provided by another AI.

Ensure the entire content is rewritten from top to bottom incorporating the specified changes.

# Steps

1. **Receive Input:** Obtain the file(s) and the edit instructions. The files can be in various formats (e.g., .txt, .docx).
2. **Analyze Content:** Understand the content and structure of the file(s).
3. **Review Instructions:** Carefully examine the edit instructions to comprehend the required changes.
4. **Apply Changes:** Rewrite the entire content of the file(s) from top to bottom, incorporating the specified changes.
5. **Verify Consistency:** Ensure that the rewritten content maintains logical consistency and cohesiveness.
6. **Final Review:** Perform a final check to ensure all instructions were followed and the rewritten content meets the quality standards.
7. Do not include any explanations, additional text, or code block markers (such as ```html or ```).

Provide the output as the FULLY NEW WRITTEN file(s).
NEVER ADD ANY CODE BLOCK MARKER AT THE BEGINNING OF THE FILE OR AT THE END OF THE FILE (such as ```html or ```).

"""


PLANNING_PROMPT = """You are an AI planning assistant. Your task is to create a detailed plan based on the user's request. Consider all aspects of the task, break it down into steps, and provide a comprehensive strategy for accomplishment. Your plan should be clear, actionable, and thorough."""


last_ai_response = None
conversation_history = []

def is_binary_file(file_path):
    """Check if a file is binary by reading a small portion of it."""
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)  # Read the first 1024 bytes
            if b'\0' in chunk:
                return True  # File is binary if it contains null bytes
            # Use a heuristic to detect binary content
            text_characters = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)))
            non_text = chunk.translate(None, text_characters) # type: ignore
            if len(non_text) / len(chunk) > 0.30: # type: ignore
                return True  # Consider binary if more than 30% non-text characters
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return True  # Assume binary if an error occurs
    return False  # File is likely text


# Load .gitignore patterns if in a git repository
def load_gitignore_patterns(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(file_path, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def add_file_to_context(file_path, added_files, action='to the chat context'):
    """Add a file to the given dictionary, applying exclusion rules."""
    excluded_dirs = {
    '__pycache__',
    '.git',
    'node_modules',
    'venv',
    'env',
    '.vscode',
    '.idea',
    'dist',
    'build',
    '__mocks__',
    'coverage',
    '.pytest_cache',
    '.mypy_cache',
    'logs',
    'temp',
    'tmp',
    'secrets',
    'private',
    'cache',
    'addons'
    }
    # Removed reliance on 'excluded_extensions' and 'supported_extensions'

    # Load .gitignore patterns if in a git repository
    gitignore_patterns = []
    if os.path.exists('.gitignore'):
        gitignore_patterns = load_gitignore_patterns('.')

    if os.path.isfile(file_path):
        # Exclude based on directory
        if any(ex_dir in file_path for ex_dir in excluded_dirs):
            print(colored(f"Skipped excluded directory file: {file_path}", "yellow"))
            logging.info(f"Skipped excluded directory file: {file_path}")
            return
        # Exclude based on gitignore patterns
        if gitignore_patterns and should_ignore(file_path, gitignore_patterns):
            print(colored(f"Skipped file matching .gitignore pattern: {file_path}", "yellow"))
            logging.info(f"Skipped file matching .gitignore pattern: {file_path}")
            return
        if is_binary_file(file_path):
            print(colored(f"Skipped binary file: {file_path}", "yellow"))
            logging.info(f"Skipped binary file: {file_path}")
            return
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                added_files[file_path] = content
                print(colored(f"Added {file_path} {action}.", "green"))
                logging.info(f"Added {file_path} {action}.")
        except Exception as e:
            print(colored(f"Error reading file {file_path}: {e}", "red"))
            logging.error(f"Error reading file {file_path}: {e}")
    else:
        print(colored(f"Error: {file_path} is not a file.", "red"))
        logging.error(f"{file_path} is not a file.")



def apply_modifications(new_content, file_path):
    try:
        with open(file_path, 'r') as file:
            old_content = file.read()

        if old_content.strip() == new_content.strip():
            print(colored(f"No changes detected in {file_path}", "red"))
            return True

        display_diff(old_content, new_content, file_path)

        confirm = prompt(f"Apply these changes to {file_path}? (yes/no): ", style=Style.from_dict({'prompt': 'orange'})).strip().lower()
        if confirm == 'yes':
            with open(file_path, 'w') as file:
                file.write(new_content)
            print(colored(f"Modifications applied to {file_path} successfully.", "green"))
            logging.info(f"Modifications applied to {file_path} successfully.")
            return True
        else:
            print(colored(f"Changes not applied to {file_path}.", "red"))
            logging.info(f"User chose not to apply changes to {file_path}.")
            return False

    except Exception as e:
        print(colored(f"An error occurred while applying modifications to {file_path}: {e}", "red"))
        logging.error(f"Error applying modifications to {file_path}: {e}")
        return False

def display_diff(old_content, new_content, file_path):
    diff = list(difflib.unified_diff(
old_content.splitlines(keepends=True),
new_content.splitlines(keepends=True),
fromfile=f"a/{file_path}",
tofile=f"b/{file_path}",
lineterm='',
n=5
))
    if not diff:
        print(f"No changes detected in {file_path}")
        return
    console = Console()
    table = Table(title=f"Diff for {file_path}")
    table.add_column("Status", style="bold")
    table.add_column("Line")
    table.add_column("Content")
    line_number = 1
    for line in diff:
        status = line[0]
        content = line[2:].rstrip()
        if status == ' ':
            continue  # Skip unchanged lines
        elif status == '-':
            table.add_row("Removed", str(line_number), content, style="red")
        elif status == '+':
            table.add_row("Added", str(line_number), content, style="green")
        line_number += 1
    console.print(table)

def apply_creation_steps(creation_response, added_files, retry_count=0):
    max_retries = 3
    try:
        code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', creation_response)
        if not code_blocks:
            raise ValueError("No code blocks found in the AI response.")

        print("Successfully extracted code blocks:")
        logging.info("Successfully extracted code blocks from creation response.")

        for code in code_blocks:
            # Extract file/folder information from the special comment line
            info_match = re.match(r'### (FILE|FOLDER): (.+)', code.strip())

            if info_match:
                item_type, path = info_match.groups()

                if item_type == 'FOLDER':
                    # Create the folder
                    os.makedirs(path, exist_ok=True)
                    print(colored(f"Folder created: {path}", "green"))
                    logging.info(f"Folder created: {path}")
                elif item_type == 'FILE':
                    # Extract file content (everything after the special comment line)
                    file_content = re.sub(r'### FILE: .+\n', '', code, count=1).strip()

                    # Create directories if necessary
                    directory = os.path.dirname(path)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                        print(colored(f"Folder created: {directory}", "green"))
                        logging.info(f"Folder created: {directory}")

                    # Write content to the file
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    print(colored(f"File created: {path}", "green"))
                    logging.info(f"File created: {path}")
            else:
                print(colored("Error: Could not determine the file or folder information from the code block.", "red"))
                logging.error("Could not determine the file or folder information from the code block.")
                continue

        return True

    except ValueError as e:
        if retry_count < max_retries:
            print(colored(f"Error: {str(e)} Retrying... (Attempt {retry_count + 1})", "red"))
            logging.warning(f"Creation parsing failed: {str(e)}. Retrying... (Attempt {retry_count + 1})")
            error_message = f"{str(e)} Please provide the creation instructions again using the specified format."
            time.sleep(2 ** retry_count)  # Exponential backoff
            new_response = chat_with_ai(error_message, is_edit_request=False, added_files=added_files)
            if new_response:
                return apply_creation_steps(new_response, added_files, retry_count + 1)
            else:
                return False
        else:
            print(colored(f"Failed to parse creation instructions after multiple attempts: {str(e)}", "red"))
            logging.error(f"Failed to parse creation instructions after multiple attempts: {str(e)}")
            print("Creation response that failed to parse:")
            print(creation_response)
            return False
    except Exception as e:
        print(colored(f"An unexpected error occurred during creation: {e}", "red"))
        logging.error(f"An unexpected error occurred during creation: {e}")
        return False



def parse_edit_instructions(response):
    instructions = {}
    current_file = None
    current_instructions = []

    for line in response.split('\n'):
        if line.startswith("File: "):
            if current_file:
                instructions[current_file] = "\n".join(current_instructions)
            current_file = line[6:].strip()
            current_instructions = []
        elif line.strip() and current_file:
            current_instructions.append(line.strip())

    if current_file:
        instructions[current_file] = "\n".join(current_instructions)

    return instructions

def apply_edit_instructions(edit_instructions, original_files):
    modified_files = {}
    for file_path, content in original_files.items():
        if file_path in edit_instructions:
            instructions = edit_instructions[file_path]
            prompt = f"{APPLY_EDITS_PROMPT}\n\nOriginal File: {file_path}\nContent:\n{content}\n\nEdit Instructions:\n{instructions}\n\nUpdated File Content:"
            response = chat_with_ai(prompt, is_edit_request=True)
            if response:
                modified_files[file_path] = response.strip()
        else:
            modified_files[file_path] = content  # No changes for this file
    return modified_files

def chat_with_ai(user_message, is_edit_request=False, retry_count=0, added_files=None):
    global last_ai_response, conversation_history
    try:
        # Include added file contents and conversation history in the user message
        if added_files:
            file_context = "Added files:\n"
            for file_path, content in added_files.items():
                file_context += f"File: {file_path}\nContent:\n{content}\n\n"
            user_message = f"{file_context}\n{user_message}"

        # Include conversation history
        if not is_edit_request:
            history = "\n".join([f"User: {msg}" if i % 2 == 0 else f"AI: {msg}" for i, msg in enumerate(conversation_history)])
            if history:
                user_message = f"{history}\nUser: {user_message}"

        # Prepare the message content based on the request type
        if is_edit_request:
            prompt = EDIT_INSTRUCTION_PROMPT if retry_count == 0 else APPLY_EDITS_PROMPT
            message_content = f"{prompt}\n\nUser request: {user_message}"
        else:
            message_content = user_message

        if is_edit_request and retry_count == 0:
            print(colored("Analyzing files and generating modifications...", "magenta"))
            logging.info("Sending edit request to AI.")
        elif not is_edit_request:
            print(colored("Algo engineer is thinking...", "magenta"))
            logging.info("Sending general query to AI.")

        response = model.generate_content(
            message_content,
            generation_config=GenerationConfig(temperature=0.0, max_output_tokens=1500, top_p=0.95, top_k=40)
        )
        logging.info("Received response from AI.")
        last_ai_response = response.text

        if not is_edit_request:
            # Update conversation history
            conversation_history.append(user_message)
            conversation_history.append(last_ai_response)
            if len(conversation_history) > 20:  # 10 interactions (user + AI each)
                conversation_history = conversation_history[-20:]

        return last_ai_response
    except Exception as e:
        print(colored(f"Error while communicating with Germini: {e}", "red"))
        logging.error(f"Error while communicating with Germini: {e}")
        return None

def algo_explain(concept: str):
    """Explains an Algorand concept using Algo."""
    prompt = f"Explain the concept of '{concept}' in the Algorand blockchain to a beginner. Use simple language and provide practical examples to illustrate how it works in real-life scenarios."
    response = chat_with_ai(prompt)
    return response


def algo_explorer(query: str):  #  Simplified example, needs error handling
    """Queries the Algorand blockchain using the indexer."""
    try:
        if query.startswith("account"):
            account_id = console.input("[bold yellow]Enter the address of the account to explore 🗃️  : [/bold yellow]").strip()
            response = indexer_client.account_info(address=account_id)
        elif query.startswith("transaction"):
            txid = console.input("[bold yellow]Enter the ID of the transaction to explore 📋: [/bold yellow]").strip()
            response = indexer_client.transaction(txid=txid)
        # ... Add more query types ...
        else:
            response = "[bold red]Invalid query format. Make sure address or txid is valid'[/bold red]"
        return json.dumps(response, indent=2) # Format the JSON for better readability

    except Exception as e:
        return f"Error: {e}"

def start_algo_eng():
    global last_ai_response, conversation_history

    table = Table(title="Algo engineer ready to help you solve problems 🤖", show_lines=True, box=box.SQUARE, title_justify="center", title_style="bold red")

    table.add_column("Command", style="green", no_wrap=True)
    table.add_column("Description", style="yellow", justify="left")

    table.add_row("/edit", "Edit files or directories (followed by paths)")
    table.add_row("/create", "Create files or folders (followed by instructions)")
    # table.add_row("/add", "Add files or folders to context")
    table.add_row("/debug", "Print the last AI response")
    table.add_row("/reset", "Reset chat context and clear added files")
    table.add_row("/review", "Review code files (followed by file paths)")
    table.add_row("/planning", "Generate a detailed plan based on your request")
    table.add_row("/algo", "Explain and explore concepts in the Algorand blockchain")
    table.add_row("/quit", "Exit the program")

    console.print(table)

    style = Style.from_dict({
        'prompt': 'cyan',
    })

    # Get the list of files in the current directory
    files = [f for f in os.listdir('.') if os.path.isfile(f)]

    # Create a WordCompleter with available commands and files
    completer = WordCompleter(
        ['/edit', '/create', '/quit', '/debug', '/reset', '/review', '/planning', '/algo'] + files,
        ignore_case=True
    )

    added_files = {}
    file_contents = {}

    while True:
        print()  # Add a newline before the prompt
        user_input = prompt("You: ", style=style, completer=completer).strip()

        if user_input.lower() == '/quit':
            print("Goodbye!")
            logging.info("User exited the program.")
            break

        elif user_input.lower() == '/debug':
            if last_ai_response:
                print(colored("Last AI Response:", "blue"))
                print(last_ai_response)
            else:
                print(colored("No AI response available yet.", "red"))

        elif user_input.lower() == '/reset':
            conversation_history = []
            added_files.clear()
            last_ai_response = None
            print(colored("Chat context and added files have been reset.", "green"))
            logging.info("Chat context and added files have been reset by the user.")

        elif user_input.startswith('/add'):
            paths = user_input.split()[1:]
            if not paths:
                print(colored("Please provide at least one file or folder path.", "red"))
                logging.warning("User issued /add without file or folder paths.")
                continue

            for path in paths:
                if os.path.isfile(path):
                    add_file_to_context(path, added_files)
                elif os.path.isdir(path):
                    for root, dirs, files_in_dir in os.walk(path):
                        # Skip excluded directories
                        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'node_modules'}]
                        for file in files_in_dir:
                            file_path = os.path.join(root, file)
                            add_file_to_context(file_path, added_files)
                else:
                    print(colored(f"Error: {path} is neither a file nor a directory.", "red"))
                    logging.error(f"{path} is neither a file nor a directory.")
            total_size = sum(len(content) for content in added_files.values())
            if total_size > 100000:  # Warning if total content exceeds ~100KB
                print(colored("Warning: The total size of added files is large and may affect performance.", "red"))
                logging.warning("Total size of added files exceeds 100KB.")

        elif user_input.startswith('/edit'):
            paths_enter = console.input(f"[bold yellow]Enter the file or folder paths to edit 📂 : [/bold yellow]").strip()
            paths = paths_enter.split()[0:]
            if not paths:
                print(colored("Please provide at least one file or folder path.", "red"))
                logging.warning("User issued /edit without file or folder paths.")
                continue
            for path in paths:
                if os.path.isfile(path):
                    add_file_to_context(path, added_files)
                elif os.path.isdir(path):
                    for root, dirs, files_in_dir in os.walk(path):
                        # Skip excluded directories
                        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'node_modules'}]
                        for file in files_in_dir:
                            file_path = os.path.join(root, file)
                            add_file_to_context(file_path, added_files)
                else:
                    print(colored(f"Error: {path} is neither a file nor a directory.", "red"))
                    logging.error(f"{path} is neither a file nor a directory.")
            if not added_files:
                print(colored("No valid files to edit.", "red"))
                continue
            edit_instruction = prompt(f"Edit instruction for all files: ", style=style).strip()

            edit_request = f"""User request: {edit_instruction}

Files to modify:
"""
            for file_path, content in added_files.items():
                edit_request += f"\nFile: {file_path}\nContent:\n{content}\n\n"

            ai_response = chat_with_ai(edit_request, is_edit_request=True, added_files=added_files)

            if ai_response:
                print("Algo engineer: Here are the suggested edit instructions:")
                rprint(Markdown(ai_response))

                confirm = prompt("Do you want to apply these edit instructions? (yes/no): ", style=style).strip().lower()
                if confirm == 'yes':
                    edit_instructions = parse_edit_instructions(ai_response)
                    modified_files = apply_edit_instructions(edit_instructions, added_files)
                    for file_path, new_content in modified_files.items():
                        apply_modifications(new_content, file_path)
                else:
                    print(colored("Edit instructions not applied.", "red"))
                    logging.info("User chose not to apply edit instructions.")

        elif user_input.startswith('/create'):
            creation_instruction = user_input[7:].strip()  # Remove '/create' and leading/trailing whitespace
            if not creation_instruction:
                print(colored("Please provide creation instructions after /create.", "red"))
                logging.warning("User issued /create without instructions.")
                continue

            create_request = f"{CREATE_SYSTEM_PROMPT}\n\nUser request: {creation_instruction}"
            ai_response = chat_with_ai(create_request, is_edit_request=False, added_files=added_files)

            if ai_response:
                while True:
                    print("Algo engineer: Here is the suggested creation structure:")
                    rprint(Markdown(ai_response))

                    confirm = prompt("Do you want to execute these creation steps? (yes/no): ", style=style).strip().lower()
                    if confirm == 'yes':
                        success = apply_creation_steps(ai_response, added_files)
                        if success:
                            break
                        else:
                            retry = prompt("Creation failed. Do you want the AI to try again? (yes/no): ", style=style).strip().lower()
                            if retry != 'yes':
                                break
                            ai_response = chat_with_ai("The previous creation attempt failed. Please try again with a different approach.", is_edit_request=False, added_files=added_files)
                    else:
                        print(colored("Creation steps not executed.", "red"))
                        logging.info("User chose not to execute creation steps.")
                        break

        elif user_input.startswith('/review'):
            paths_enter = console.input(f"[bold yellow]Enter the file or folder paths to review 📂 : [/bold yellow]").strip()
            paths = paths_enter.split()[0:]
            if not paths:
                print(colored("Please provide at least one file or folder path.", "red"))
                logging.warning("User issued /review without file or folder paths.")
                continue

            file_contents = {}
            for path in paths:
                if os.path.isfile(path):
                    add_file_to_context(path, file_contents, action='to review')
                elif os.path.isdir(path):
                    for root, dirs, files_in_dir in os.walk(path):
                        # Skip excluded directories
                        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'node_modules'}]
                        for file in files_in_dir:
                            file_path = os.path.join(root, file)
                            add_file_to_context(file_path, file_contents, action='to review')
                else:
                    print(colored(f"Error: {path} is neither a file nor a directory.", "red"))
                    logging.error(f"{path} is neither a file nor a directory.")

            if not file_contents:
                print(colored("No valid files to review.", "red"))
                continue

            review_request = f"{CODE_REVIEW_PROMPT}\n\nFiles to review:\n"
            for file_path, content in file_contents.items():
                review_request += f"\nFile: {file_path}\nContent:\n{content}\n\n"

            print(colored("Analyzing code and generating review...", "magenta"))
            ai_response = chat_with_ai(review_request, is_edit_request=False, added_files=added_files)

            if ai_response:
                print()
                print(colored("Code Review:", "blue"))
                rprint(Markdown(ai_response))
                logging.info("Provided code review for requested files.")

        elif user_input.startswith('/planning'):
            planning_instruction = user_input[9:].strip()  # Remove '/planning' and leading/trailing whitespace
            if not planning_instruction:
                print(colored("Please provide a planning request after /planning.", "red"))
                logging.warning("User issued /planning without instructions.")
                continue
            planning_request = f"{PLANNING_PROMPT}\n\nUser request: {planning_instruction}"
            ai_response = chat_with_ai(planning_request, is_edit_request=False, added_files=added_files)
            if ai_response:
                print()
                print(colored("Algo engineer: Here is your detailed plan:", "blue"))
                rprint(Markdown(ai_response))
                logging.info("Provided planning response to user.")
            else:
                print(colored("Failed to generate a planning response. Please try again.", "red"))
                logging.error("AI failed to generate a planning response.")

        elif user_input.startswith('/algo'):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                command = parts[1]
                if command.startswith("explain"):
                    concept = console.input("[bold yellow]Please enter Algorand concepts and I will help you answer 💬 : [/bold yellow]").strip()
                    explanation = algo_explain(concept)
                    if explanation:
                        rprint(Markdown(explanation))
                elif command.startswith("explore "):
                    query = command.split("explore ", 1)[1]
                    result = algo_explorer(query)
                    console.print(Panel(f"Details here 🔎:\n{result}", highlight=True))  # Print JSON directly or further process it
                else:
                    console.print("[bold red]Invalid: /algo command. Try '/algo explain' or '/algo explore <account | transaction>'[/bold red]")

            else:
                console.print("[bold green]Usage: /algo explain <concept>  or /algo explore <query>[/bold green]")

        else:
            ai_response = chat_with_ai(user_input, added_files=added_files)
            if ai_response:
                print()
                print(colored("Algo engineer:", "blue"))
                rprint(Markdown(ai_response))
                logging.info("Provided AI response to user query.")
