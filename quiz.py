from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console

console = Console()

def quiz_battle():
    console.print(Panel("[bold green]Welcome to Quiz Battles![/bold green]", title="[bold blue]🧠 Algorand Quiz Battles 🧠", expand=True))
    
    # Start the quiz loop
    quiz_loop()

def quiz_loop():
    questions_count = 3
    correct_answers = 0

    for _ in range(questions_count):
        question, options, correct_option = get_random_question()
        user_answer = ask_question(question, options)
        if evaluate_answer(user_answer, correct_option):
            correct_answers += 1
            console.print("[bold green]Correct![/bold green]")
        else:
            console.print(f"[bold red]Wrong! The correct answer was {correct_option}[/bold red]")
        console.print("\\n")

    console.print(Panel(f"You got {correct_answers}/{questions_count} correct!", title="Quiz Summary", expand=True))

def get_random_question():
    # Placeholder for random question selection logic
    question = "What is the native currency of the Algorand blockchain?"
    options = ["ALGO", "ETH", "BTC", "SOL"]
    correct_option = "ALGO"
    return question, options, correct_option

def ask_question(question, options):
    console.print(Panel(f"[bold yellow]{question}[/bold yellow]", title="Question"))
    user_answer = Prompt.ask("Choose the correct option", choices=options)
    return user_answer

def evaluate_answer(user_answer, correct_option):
    return user_answer == correct_option
