import random
import csv
import os

from prompt_toolkit.shortcuts.prompt import _T
from contents import qa_dict
from datetime import datetime
from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.progress import BarColumn, Progress
from rich.table import Table
import re

console = Console()


def quiz_battle():
    console.print("\n")
    console.print(Panel("[bold yellow]Welcome to our Quiz Battles!\nIf you are confident in passing our challenges, start now\nYou only have [red]3[/red] chances to correct your mistakes. If you run out of chances, you will lose", title="[bold blue]🧠 Algorand Quiz Battles 🧠[/bold blue]", expand=True))
    
     # Get the player's name
    player_name = get_player_name()
    console.print(f"Hello, [bold cyan]{player_name}[/bold cyan]! Let's start the quiz.\n")
    
     # Get the difficulty level
    num_questions = get_difficulty_level()
    console.print(f"You've chosen to answer [bold cyan]{num_questions}[/bold cyan] questions. Let's begin!\n")
    
    # Start the quiz loop
    quiz_loop(player_name, num_questions)
    
def get_player_name():
    while True:
           name = Prompt.ask("Please enter your name (3-12 alphanumeric characters)")
           # Validate the name using a regular expression
           if re.match("^[A-Za-z0-9]{3,12}$", name):
               return name
           else:
               console.print("[bold red]Invalid name.[/bold red] Please use 3-12 alphanumeric characters.\n")
           
def get_difficulty_level():
    console.print(Panel("[bold green]Choose your difficulty level:[/bold green]\n\n[bold cyan]1.[/bold cyan] Easy (10 questions)\n[bold cyan]2.[/bold cyan] Medium (20 questions)\n[bold cyan]3.[/bold cyan] Hard (30 questions)", title="[bold yellow]Difficulty Level[/bold yellow]", expand=True))
        
    while True:
        choice = Prompt.ask("Select a difficulty level", choices=["1", "2", "3"])
        if choice == "1":
            return 10  # Easy
        elif choice == "2":
            return 20  # Medium
        elif choice == "3":
            return 30  # Hard
        else:
            return

def quiz_loop(player_name, num_questions):
    correct_answers = 0
    incorrect_answers = 0
    hearts = 3
    used_5050 = False
    used_spoil = False   
    streak_counter = 0  # To track consecutive correct answers
    total_streak_bonus = 0  # To accumulate bonus points from streaks
    in_super_streak = False  # Flag for Super Streak Mode
    super_streak_questions = 0  # Counter for Super Streak questions
    heart_recovery_activated = False
    choice_option = ""
               
    # Randomize questions from the pool
    questions = random.sample(list(qa_dict.keys()), num_questions)
                 
    for i, question in enumerate(questions, start=1):
        correct_answer = qa_dict[question][1]  # The second element is always the correct answer
                
        # Shuffle the answer options
        options = random.sample(qa_dict[question][0], len(qa_dict[question][0]))
        
        if hearts == 1 and not heart_recovery_activated:
            heart_recovery_activated = True  # Activate heart recovery
            console.print("[bold yellow]You are running low on hearts! Answer this question below correctly to restore [bold red]1 heart[/bold red].[/bold yellow]")
                    
        console.print(f"\n[bold green]Question {i}:[/bold green] [bold yellow]{question}[/bold yellow]")
        ask_question(options)
        
        if not used_5050 or not used_spoil:
            available_power_ups = []
        
            if not used_5050:
                available_power_ups.append("1: 50/50")
            if not used_spoil:
                available_power_ups.append("2: Spoil Answer")
                choice_option = ""
        
            available_power_ups.append("3: No Power-Up")
        
            # Only ask for power-up if any are available
            power_up_choice = Prompt.ask(f"Do you want to use a power-up? [bold green][{', '.join(available_power_ups)}][/bold green]")
        
            # Handle 50/50 Lifeline
            if power_up_choice == "1" and not used_5050:
                options = use_5050_lifeline(options, correct_answer)
                used_5050 = True  # Mark 50/50 as used
                choice_option = f"[bold green]1. {options[0]} or 2. {options[1]}[/bold green]"
                console.print("[bold yellow]50/50 Lifeline used![/bold yellow]")
                    
            # Handle Skip Question
            elif power_up_choice == "2" and not used_spoil:
               used_spoil = use_spoiler(correct_answer)
        
       
        user_input = Prompt.ask(f"Choose the correct option {choice_option}", choices=[str(i) for i in range(1, len(options) + 1)])
    
        user_answer = options[int(user_input) - 1] 
    
        if user_answer.strip().lower() == correct_answer.strip().lower():
            console.print("[bold green]Correct![/bold green]")
            correct_answers += 1
            streak_counter += 1
            
            if heart_recovery_activated:
                hearts += 1  # Restore 1 heart
                heart_recovery_activated = False  # Disable heart recovery after restoring
                console.print("[bold green]Congratulations! You've restored [bold red]1 heart[/bold red].[/bold green]")
            
            if streak_counter == 3:    
                console.print("[bold blue]Streak Bonus! +5 points for 3 correct answers![/bold blue]")
                total_streak_bonus += 5
                    
            elif streak_counter == 5:
                console.print("[bold blue]Streak Bonus! +10 points for 5 correct answers![/bold blue]")
                total_streak_bonus += 10
                
            elif streak_counter == 15:
                console.print("[bold blue]Streak Bonus! +20 points for 15 correct answers![/bold blue]")
                total_streak_bonus += 20
                console.print("[bold yellow]🎉 Super Streak Mode Activated! Points will be doubled for the next 5 questions! 🎉[/bold yellow]")
                in_super_streak = True  # Activate Super Streak Mode
                
            elif streak_counter == 25:
                console.print("[bold blue]Streak Bonus! +30 points for 25 correct answers![/bold blue]")
                total_streak_bonus += 30
                console.print("[bold yellow]🎉 Super Streak Mode Activated! Points will be doubled for the next 5 questions! 🎉[/bold yellow]")
                in_super_streak = True  # Activate Super Streak Mode    
            
            # Super Streak Mode logic
            if in_super_streak:
                super_streak_questions += 1
                correct_answers += 2  # Double points for each correct answer
                console.print("[bold cyan]Super Streak: You earned double points for this question![/bold cyan]")
            
                if super_streak_questions == 5:
                    in_super_streak = False  # End Super Streak Mode after 5 questions
                    super_streak_questions = 0
                    console.print("[bold yellow]Super Streak Mode Ended! Back to normal scoring.[/bold yellow]")    
                
        else:
            incorrect_answers += 1
            hearts -= 1
            console.print(f"[bold red]Incorrect![/bold red] The correct answer was: [bold green]{correct_answer}[/bold green]")
            console.print(f"[bold yellow]You have {hearts} heart[/bold yellow]")
            streak_counter = 0
            in_super_streak = False
                
        if hearts == 0:
            console.print("[bold red]Game Over![/bold red]")
            break
            
            
    final_score = correct_answers + total_streak_bonus
    
    # Save results to CSV after the game
    save_results_to_csv(player_name, correct_answers, incorrect_answers, num_questions, total_streak_bonus, final_score)
    
    # Display results from CSV
    display_results_from_csv()


def ask_question(options):
    for idx, option in enumerate(options, start=1):
        console.print(f"[bold yellow]{idx}.[/bold yellow] {option}")
        
        
def use_5050_lifeline(options, correct_answer):
    # Get a list of incorrect options
    incorrect_options = [option for option in options if option != correct_answer]
        
    # Randomly select two incorrect options to remove
    if len(incorrect_options) >= 2:
        removed_options = random.sample(incorrect_options, 2)
    else:
        removed_options = incorrect_options  # Just in case there are fewer than 2 options
    
    # Keep the correct answer and one random incorrect answer (if available)
    remaining_options = [correct_answer] + [option for option in incorrect_options if option not in removed_options]
        
    # Shuffle the remaining options to avoid giving away the correct answer position
    random.shuffle(remaining_options)
        
    return remaining_options
    
     
def use_spoiler(correct_answer):
    console.print(f"[bold yellow]Spoil Answer used! The correct answer is: [bold green]{correct_answer}[/bold green][/bold yellow]")
    return True
    
    
def save_results_to_csv(player_name, correct_answers, incorrect_answers, total_questions, total_streak_bonus, final_score):
    filename = "quiz_results.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if the file exists; if not, create it and write the header
    file_exists = os.path.isfile(filename)
    
    # Write to CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Player Name", "Correct Answers", "Incorrect Answers", "Total Questions", "Total Streak Bonus", "Final Score", "Date and Time"])
            
        # Write the results
        writer.writerow([player_name, correct_answers, incorrect_answers, total_questions, total_streak_bonus, final_score, current_time])
        
        
def display_results_from_csv():
    filename = "quiz_results.csv"
    
    console.print("\n[bold cyan]Quiz Results:[/bold cyan]")
    
    # Create a table for displaying results
    table = Table(show_lines=True)
    table.add_column("Player Name", justify="center", style="cyan", no_wrap=True)
    table.add_column("Correct Answers", justify="center", style="green")
    table.add_column("Incorrect Answers", justify="center", style="green")
    table.add_column("Total Questions", justify="center", style="blue")
    table.add_column("Total Streak Bonus", justify="center", style="blue")
    table.add_column("Final Score", justify="center", style="yellow")
    table.add_column("Date and Time", justify="center", style="magenta", no_wrap=True)
    
    results = []
    
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        # Skip header row
        next(reader)
        for row in reader:
            results.append(row)
            
    results.sort(key=lambda x: datetime.strptime(x[6], "%Y-%m-%d %H:%M:%S"), reverse=True)

    for row in results:
        table.add_row(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
    
    console.print(table) 