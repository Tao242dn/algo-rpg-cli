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
    
    "Project Genesis [red](command: init)[/red] Time to craft something new! Use the init command to initialize a new Algorand project. This creates the foundation for building your own smart contracts – the magical spells of the Algorand world. We recommend using project name [red]auction_project[/red] match with my default template.",
    
    "Constructing the Spell [red](command: build)[/red]: With a project in place, you can now begin building your smart contract. The build command compiles your code into the bytecode that the Algorand Virtual Machine (AVM) understands. This is like carefully inscribing the runes of your spell.",
    
    "Trial Run [red](command: test)[/red]: Before unleashing your magic upon the world, it's wise to practice. Use the test command to test your smart contract in a safe, isolated environment. This allows you to identify and fix any bugs or vulnerabilities before deploying it to the main blockchain.",
    
    "Scrutiny of the Sages [red](command: audit)[/red] Even the most skilled mages seek peer review. Use the audit command to analyze your smart contract for potential security flaws and inefficiencies. This is like having a council of wise mages examine your spell for weaknesses.",
    
    "Unleashing the Magic [red](command: deploy)[/red] Once you're confident in your creation, it's time to deploy your smart contract to the Algorand blockchain. The deploy command makes your contract live, allowing other users to interact with it. Your spell is now active in the world!",
    
    "Preserving the Lore [red](command: upload)[/red] Important artifacts and knowledge deserve to be preserved. Use the upload command to upload files to IPFS (InterPlanetary File System), a decentralized storage network. This ensures that your data is immutable and accessible to anyone, even if parts of the network go offline. Think of it as storing your magical scrolls in a secure, distributed library."
]

qa_dict = {
    "Who founded Algorand?": [["Vitalik Buterin", "Satoshi Nakamoto", "Silvio Micali", "Charles Hoskinson"], "Silvio Micali"],
    
    "What consensus mechanism does Algorand use?": [["Proof-of-Work", "Delegated Proof-of-Stake", "Byzantine Fault Tolerance", "Pure Proof-of-Stake (PPoS)"], "Pure Proof-of-Stake (PPoS)"],
    
    "What is the native cryptocurrency of Algorand?": [["ALGO", "ETH", "BTC", "SOL"], "ALGO"],
    
    "How does Algorand ensure decentralization?": [["Mining", "Random selection of validators", "Staking", "Proof of Work"], "Random selection of validators"],
    
    "What is the average block time on Algorand?": [["3.7 seconds", "10 minutes", "15 seconds", "1 hour"], "3.7 seconds"],
    
    "How does Algorand solve the blockchain trilemma?": [["Mining", "Proof-of-Stake", "Scalability, security, decentralization", "Validators"], "Scalability, security, decentralization"],
    
    "How does Algorand handle transaction finality?": [["Immediate finality", "Confirmation in 10 blocks", "Delayed finality", "Stochastic finality"], "Immediate finality"],
    
    "What is the main purpose of Algorand?": [["Smart contracts", "NFT minting", "High-speed transactions", "DeFi"], "High-speed transactions"],
    
    "What is Algorand’s approach to scalability?": [["Sidechains", "Layer-2", "Sharding", "Efficient consensus"], "Efficient consensus"],
    
    "How does Algorand achieve low transaction costs?": [["High gas fees", "Layer-2", "Efficient consensus", "Sharding"], "Efficient protocol design"],
    
    "What feature allows Algorand to handle multiple transactions simultaneously?": [["Parallel processing", "Atomic transfers", "Sharding", "Multi-threading"], "Atomic transfers"],
    
    "What is the Algorand Foundation’s role?": [["Funding and research", "Governance and development", "Marketing and promotion", "Community building"], "Governance and development"],
    
    "How does TEAL ensure smart contract security in Algorand?": [["Formal verification", "Stack-based language", "Sandboxing", "Static analysis"], "Stack-based language"],
    
    "How does Algorand handle stateful vs. stateless smart contracts?": [["Combined execution", "Separate execution environments", "Dynamic switching", "Hybrid approach"], "Separate execution environments"],
    
    "Explain Algorand’s approach to optimizing transaction throughput in its protocol?": [["Sharding", "Fast consensus and block finality", "Large block sizes", "Off-chain transactions"], "Fast consensus and block finality"],
    
    "What role do relay nodes play in Algorand’s network architecture?": [["Facilitate communication", "Validate transactions", "Store blockchain data", "Execute smart contracts"], "Facilitate communication"],
    
    "Discuss the role of Algorand’s Virtual Machine (AVM) in executing contracts?": [["Compiles TEAL code", "Executes TEAL scripts", "Manages state", "Verifies transactions"], "Executes TEAL scripts"],
    
    "Explain how atomic transfers are implemented in Algorand?": [["Single transactions", "Grouped transactions", "Chained transactions", "Smart contracts"], "Grouped transactions"],
    
    "What are the engineering challenges in implementing Algorand Standard Assets (ASA)?": [["Tokenization standards", "Custom asset creation", "Decentralized exchange", "Security audits"], "Custom asset creation"],
    
    "How does Algorand manage network latency and ensure consistency?": [["Centralized servers", "Fast block propagation", "Caching mechanisms", "Redundant networks"], "Fast block propagation"],
    
    "What is the TEAL programming language used for in Algorand?": [["Writing smart contracts", "Developing dApps", "Building blockchain infrastructure", "Creating cryptographic algorithms"], "Writing smart contracts"],
    
    "What are Algorand Smart Contracts (ASC1)?": [["Off-chain contracts", "Layer-2 smart contracts", "Layer-1 smart contracts", "Hybrid smart contracts"], "Layer-1 smart contracts"],
    
    "What is an Algorand Standard Asset (ASA)?": [["Native cryptocurrency", "Custom tokens framework", "Stablecoin protocol", "Decentralized exchange"], "Custom tokens framework"],
    
    "How does Algorand handle smart contract execution fees?": [["Fixed fees", "Based on complexity", "Gas fees", "Transaction size"], "Based on complexity"],
    
    "What is a Stateful Smart Contract in Algorand?": [["Stateless contract", "Maintains state", "Temporary contract", "Immutable contract"], "Maintains state"],
    
    "How are nodes incentivized in the Algorand network?": [["Transaction fees", "Block rewards", "Staking rewards", "Mining rewards"], "Block rewards"],
    
    "What are the security implications of Algorand’s PPoS model?": [["Increases centralization risk", "Reduces centralization risk", "Vulnerable to 51% attacks", "Requires high energy consumption"], "Reduces centralization risk"],
    
    "What is Cryptographic Sortition in Algorand?": [["Random number generation", "Selects consensus participants", "Encrypts transactions", "Verifies block integrity"], "Selects consensus participants"],
    
    "Can anyone participate in Algorand's consensus?": [["Yes", "No", "Only selected nodes", "Only authorized participants"], "Yes"],
    
    "What year was Algorand launched?": [["2017", "2018", "2019", "2020"], "2019"]
}

choice_content = "[bold green]Choose an option you would like:\n1. Option [red]Q&A[/red] 🤖 you can interactive with AI really insteresting huh.\n2. With [red]Game[/red] 🎮 we start the game explore 11 quests.\n3. Let [red]Quiz[/red] 📖 if you want to test your knowledge.\n4. Or [red]Quit[/red] 👌 quit the game, your journey is over.[/bold green]\nTell me what your choice"

after_credits = """
Thank you for playing AlgoRPG!

We hope you enjoyed your adventure through the world of Algorand and that the game helped you learn more about blockchain technology. Your feedback is valuable to us, so please let us know what you thought of your experience. Did you find the game helpful in understanding Algorand? What did you enjoy most? What could we improve?

We're constantly working to make AlgoRPG even better, so your input is greatly appreciated.
""" 