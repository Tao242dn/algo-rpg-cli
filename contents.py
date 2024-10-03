plot_summary = """
A text-based RPG unfolds entirely within the command-line interface, where players' actions directly interact with the Algorand blockchain.

A command-line interface (CLI) based RPG guides new users through the concepts of the Algorand blockchain.

The game mechanics directly utilize Algorand's features, turning abstract technical concepts into tangible actions within the game's narrative.

This provides a hands-on, interactive learning experience for newcomers to Algorand, making the technology more accessible and engaging.
"""

quests = [
    "Environmental Check [red](command: env)[/red] Before we begin our journey, let's ensure your surroundings are properly configured. Use the env command to check if your system meets the requirements for interacting with the Algorand blockchain. This involves verifying the necessary software and tools are installed and that your environment variables are set correctly.",
    
    "Account Creation [red](command: account)[/red] Every adventurer needs an identity! Create your Algorand account using the account command. This will generate a unique address and private key, which are essential for managing your assets and interacting with the blockchain. Keep your private key safe – it's the key to your digital kingdom!",
    
    "Funding Your Adventure [red](command: fund)[/red] Every great quest requires provisions. Fund your newly created Algorand account using the fund command. You'll need some Algo (Algorand's native cryptocurrency) to pay for transaction fees and interact with the blockchain. Think of it as stocking up on potions and supplies before embarking on a dangerous journey.",
    
    "Checking Your Provisions [red](command: balance)[/red] Wise adventurers keep track of their resources. Use the balance command to check the balance of your Algorand account. This will show you how much Algo you have available for your quests.",
    
    "Sharing the Spoils [red](command: send)[/red] Generosity is a virtue, even in the digital realm. Use the send command to send Algo to another Algorand account. This is like sharing your treasure with a fellow adventurer [bold](note: 1 Algo = 1_000_000 MicroAlgos)[/bold]",
    
    "Project Genesis [red](command: init)[/red] Time to craft something new! Use the init command to initialize a new Algorand project. This creates the foundation for building your own smart contracts – the magical spells of the Algorand world.",
    
    "Constructing the Spell [red](command: build)[/red]: With a project in place, you can now begin building your smart contract. The build command compiles your code into the bytecode that the Algorand Virtual Machine (AVM) understands. This is like carefully inscribing the runes of your spell.",
    
    "Trial Run [red](command: test)[/red]: Before unleashing your magic upon the world, it's wise to practice. Use the test command to test your smart contract in a safe, isolated environment. This allows you to identify and fix any bugs or vulnerabilities before deploying it to the main blockchain.",
    
    "Scrutiny of the Sages [red](command: audit)[/red] Even the most skilled mages seek peer review. Use the audit command to analyze your smart contract for potential security flaws and inefficiencies. This is like having a council of wise mages examine your spell for weaknesses.",
    
    "Unleashing the Magic [red](command: deploy)[/red] Once you're confident in your creation, it's time to deploy your smart contract to the Algorand blockchain. The deploy command makes your contract live, allowing other users to interact with it. Your spell is now active in the world!",
    
    "Preserving the Lore [red](command: upload)[/red] Important artifacts and knowledge deserve to be preserved. Use the upload command to upload files to IPFS (InterPlanetary File System), a decentralized storage network. This ensures that your data is immutable and accessible to anyone, even if parts of the network go offline. Think of it as storing your magical scrolls in a secure, distributed library."
]

choice_content = "[bold green]Choose an option would like:\n1. Option [red]q&a[/red] you can interactive with AI really insteresting huh.\n2. With [red]game[/red] we start the game explore 11 quests.\n3. Or [red]quit[/red] quit the game, your journey is over.[/bold green]\nTell me what your choice:"

after_credits = """
Thank you for playing AlgoRPG!

We hope you enjoyed your adventure through the world of Algorand and that the game helped you learn more about blockchain technology. Your feedback is valuable to us, so please let us know what you thought of your experience. Did you find the game helpful in understanding Algorand? What did you enjoy most? What could we improve?

We're constantly working to make AlgoRPG even better, so your input is greatly appreciated.
""" 