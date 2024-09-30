import subprocess
import time
import random
import os
from contents import plot_summary, after_credits
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from algosdk import account, mnemonic
from algosdk.v2client import algod

console = Console()

def print_quest_not_completed():
    console.print(Panel(f"[bold]Quest not completed yet 🙁. Don't give up try again.[/bold]", title="[bold red]Oops! Something went wrong 😭[/bold red]", border_style="bold red", expand=True, highlight=True))

class AlgorandQuest():
    def __init__(self):
        self.player = {}
        self.algod_client: algod.AlgodClient
        self.current_act:int = 1
        self.current_quest:int = 1
        self.quests_structure = {
           1: 5,
           2: 4,
        }
    
    def start_game(self):
        console.print(Panel(f"[bold yellow]{plot_summary}[/bold yellow]", title="[bold red]The Algorand Quest Master the Algorand Blockchain[/bold red]", subtitle="[bold cyan]Made By AlgoRPG Team[/bold cyan]", box=box.DOUBLE, border_style="bold", expand=True, highlight=True))
        
        console.print("\n")
        with Progress() as progress:
            task = progress.add_task("[bold]:hourglass: Loading...[/bold]", total=100)
            while not progress.finished:
                progress.update(task, advance=random.uniform(0.5, 2))
                time.sleep(0.05)
                
        self.setup_algod_client()
        self.main_game_loop()
        
    def setup_algod_client(self):
        algo_token = "a" * 64
        algo_address = "http://localhost:4001"
        self.algod_client = algod.AlgodClient(algo_token, algo_address)
        
    def main_game_loop(self):
        while True:
            if self.current_act > len(self.quests_structure) or (self.current_act == len(self.quests_structure) and self.current_quest > self.quests_structure[self.current_act]):
                console.print("\n")
                console.print(Panel(f"[bold yellow]{after_credits}[/bold yellow]", title="[bold red]AlgoRPG[/bold red]",subtitle="[bold cyan]A Blockchain Adventure[/bold cyan]", box=box.DOUBLE, border_style="bold", expand=True, highlight=True))
                break
            
            console.print("\n")
            self.display_current_quest()
            action = console.input("[bold yellow]What would you like to do 🤔: [/bold yellow]")
            with console.status("", spinner="dots") as status:
                status.update("Executing command...")
                time.sleep(3)  # simulate a long-running task    
            self.process_action(action)
    
    def display_current_quest(self):
        quest_description = {
            (1, 1): "Check the environment",
            (1, 2): "Create an Algorand account",
            (1, 3): "Funding the account",
            (1, 4): "Check the account balance",
            (1, 5): "Send ALGO to another account",
            (2, 1): "Initialize a new project",
            (2, 2): "Build the contract",
            (2, 3): "Test the contract",
            (2, 4): "Audit the contract",
            # (2, 5): "Deploy the contract",
        }

        current_quest = quest_description.get((self.current_act, self.current_quest), "Quest not defined")
        
        console.print(Panel(f"Quest: [bold magenta]{current_quest}[/bold magenta]", title=f"[bold red]Quest {self.current_quest} in Act {self.current_act}[/bold red]", box=box.SQUARE, border_style="bold", expand=True, highlight=True))
        
    def process_action(self, action: str):
        match(self.current_act, self.current_quest):
            case (1, 1):
                self.process_check_env(action)
            case (1, 2):
                self.process_create_account(action)
            case (1, 3):
                self.process_fund_account(action)
            case (1, 4):
                self.process_check_account_balance(action)
            case (1, 5):
                self.process_send_algo(action)
            case (2, 1):
                self.process_init_project(action)
            case (2, 2):
                self.process_build_contract(action)
            case (2, 3):
                self.process_test_contract(action)
            case (2, 4):
                self.process_audit_contract(action)
            # case (2, 5):
            #     self.process_deploy_contract(action)
            case _:
                console.print(Panel(f"[bold red]Quest not completed yet![/bold red]"))
        
        if self.current_quest > self.quests_structure[self.current_act]:
            self.current_act += 1
            self.current_quest = 1
    
    def process_check_env(self, action: str):
        if action.lower().strip() == "env":
            try:
               result = subprocess.run(["algokit", "doctor"], capture_output=True, text=True)
               if result.returncode == 0:
                   console.print(Panel(f"[bold]The environment is ready 🚀\n{result.stdout}[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                   self.current_quest += 1
               else:
                   console.print(Panel(f"[bold]The environment is not ready 🥲: {result.stderr}[/bold]", title=f"[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title=f"[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title=f"[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
                
        else:
            print_quest_not_completed()
    
    def process_create_account(self, action: str):
        if action.lower().strip() == "account":
            private_key, address = account.generate_account()
            self.player = {
                "address": address,
                "private_key": private_key,
                "mnemonic": mnemonic.from_private_key(private_key)
            }
            try:
                result = subprocess.run(["algokit", "goal", "account", "import", "-m", self.player["mnemonic"]], capture_output=True, text=True)
                if result.returncode == 0:
                   console.print(Panel(f"[bold]Your address ✉️:  [green]{self.player['address']}[/green]\nKeep your private key safe 🔑: [red]{self.player['private_key']}[/red][/bold]\nAuto import mnemonic in your computer 💾", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                   self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't create account 😢: {result.stderr}[/bold]", title="[yellow]Command is executed but an error occurred ⚠️[/yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error:{e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        
        else:
            print_quest_not_completed()
            
    
    def process_fund_account(self, action: str):
        if action.lower().strip() == "fund":
            amount = "10000000"
            from_addr = "B7445LSKMBOQPOJ7DAAJRS3HJBFXWDLBNRDDBK4KN4OO2EUFOYM466OXHI"
            try:
                result = subprocess.run(["algokit", "goal", "clerk", "send", "-a", amount, "-f", from_addr, "-t",    self.player["address"]], capture_output=True, text=True)
                if result.returncode == 0:
                   console.print(Panel(f"[bold]Fund 10 Algo 🪙 to [cyan]{self.player['address']}[/cyan] successfully !", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                   self.current_quest += 1
                else:
                   console.print(Panel(f"[bold]Can't fund your account 😢: {result.stderr}[/bold]", title="[bold][yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
    def process_check_account_balance(self, action: str):
        if action.lower().strip() == "balance":
            account_info = self.algod_client.account_info(self.player["address"])
            console.print(Panel(f"[bold]Your account balance 💰: {account_info.get('amount') // 1000000} Algo[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True)) # type: ignore
            self.current_quest += 1
        else:
            print_quest_not_completed()
        
    def process_send_algo(self, action: str):
        if action.lower().strip() == "send":
            receive_addr = console.input("[bold yellow]Enter the address or username of the receiver to send Algo 📝: [/bold yellow]")
            amount = console.input("[bold yellow]Enter the amount of Algo to send 💵: [/bold yellow]")
            amount_microalgos = str(int(float(amount) * 1000000))
            try:
                result = subprocess.run(["algokit", "goal", "clerk", "send", "-a", amount_microalgos, "-f", self.player["address"], "-t", receive_addr], capture_output=True, text=True)
                
                if result.returncode == 0:
                    account_info = self.algod_client.account_info(self.player["address"])
                    console.print(Panel(f"[bold]Transaction successfully 🎉. Send {amount} Algo to [green]{receive_addr}[/green]\nTransaction fees: 0.001 Algo\nYour available balance is {account_info.get('amount') / 1000000} Algo[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True)) # type: ignore
                    self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't send Algo to {receive_addr} 😢: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
            
    def process_init_project(self, action: str):
        if action.lower().strip() == "init":
            url = "https://github.com/Tao242dn/auction_template.git"
            non_ie_option = "--UNSAFE-SECURITY-accept-template-url"
            project_name = console.input("[bold yellow]Enter the name of the project ⌨️ : [/bold yellow]")
            self.player = {
                "project_directory": project_name + "/"
            }
            try:
                result = subprocess.run(["algokit", "init", "-n", project_name, "--template-url", url, "--no-git", "--no-ide", "--no-workspace", "--bootstrap", non_ie_option], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(Panel(f"[bold]Project [cyan]{project_name}[/cyan] initialized successfully 🎉\n{result.stdout}[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                    self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't initialization [cyan]{project_name}[/cyan] project 😔: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
            
    def process_build_contract(self, action: str):
        if action.lower().strip() == "build":
            try:
                # Change to the project directory
                project_dir = self.player.get("project_directory", "")
                if project_dir:
                    os.chdir(project_dir)
                    
                result = subprocess.run(["poetry", "run", "python", "-m", "smart_contracts", "build"], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(Panel(f"[bold]Building contract successfully 🎉\nCreating [green]{result.stdout}[/green]Congratulations! You have successfully building your contract 🔨", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                    self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't build contract 😢: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
            
    def process_test_contract(self, action: str):
        if action.lower().strip() == "test":
            try: 
                result = subprocess.run(["poetry", "run", "pytest"], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(Panel(f"[bold]Testing contract successfully 🎉\nCongratulations! You have successfully testing your contract 🛠️\n{result.stdout}[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                    self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't test contract 😢: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
    
    def process_audit_contract(self, action: str):
        if action.lower().strip() == "audit":
            try:
                # Generate requirements.txt
                subprocess.run(["poetry", "export", "--without=dev", "-o", "requirements.txt"], capture_output=True, text=True)
                
                result = subprocess.run(["poetry", "run", "pip-audit", "-r", "requirements.txt"], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(Panel(f"[bold]Auditing contract successfully 🎉\nCongratulations! You have successfully audited your contract 🔍[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
                    self.current_quest += 1
                else:
                    console.print(Panel(f"[bold]Can't audit contract 😢: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
            except subprocess.CalledProcessError as e:
                console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
            except Exception as e:
                console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
        else:
            print_quest_not_completed()
            
    
    # def process_deploy_contract(self, action: str):
    #     if action.lower().strip() == "deploy":
    #         try:
    #             # Generate .env file
    #             subprocess.run(["algokit", "generate", "env-file", "-a", "target_network", "localnet"],
    #             capture_output=True, text=True)
                
    #             result = subprocess.run(["poetry", "run", "python", "-m", "smart_contracts", "deploy"],       capture_output=True, text=True)
    #             if result.returncode == 0:
    #                 console.print(Panel(f"[bold]Deploying contract successfully 🎉\nCongratulations! You have successfully deployed your contract 🧭[/bold]", title="[bold green]Quest completed successfully ✅[/bold green]", border_style="bold green", expand=True, highlight=True))
    #                 self.current_quest += 1
    #             else:
    #                 console.print(Panel(f"[bold]Can't deploy contract 😢: {result.stderr}[/bold]", title="[bold yellow]Command is executed but an error occurred ⚠️[/bold yellow]", border_style="bold yellow", expand=True, highlight=True))
    #         except  subprocess.CalledProcessError as e:
    #             console.print(Panel(f"[bold]Error: {e.stdout}[/bold]", title="[bold red]Command executed failed ❗[/bold red]", border_style="bold red", expand=True, highlight=True))
    #         except Exception as e:
    #             console.print(Panel(f"[bold]Error: {str(e)}[/bold]", title="[bold red]An error occurred ❗❗[/bold red]", border_style="bold red", expand=True, highlight=True))
    #     else:
    #         print_quest_not_completed()
            

if __name__ == "__main__":
    game = AlgorandQuest()
    game.start_game()        