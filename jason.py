from rich.console import Console

console = Console()

# Prompt the user for a file path
file = console.input("[bold blue]Enter the path to the JSON file: [/bold blue]")
console.log(file)
    
try:
    # Open and read the file
    with open(file, "r") as f:
        content = f.read()

    # Print formatted JSON
    console.print_json(content)
except FileNotFoundError:
    console.print(f"[bold red]Error:[/bold red] File '{file}' not found.")
except Exception as e:
    console.print(f"[bold red]An error occurred:[/bold red] {e}")
