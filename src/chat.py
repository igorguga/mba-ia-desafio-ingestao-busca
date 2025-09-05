import os
from dotenv import load_dotenv
from search import search_prompt
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
for k in ("GOOGLE_API_KEY", "GEMINI_MODEL"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

def _invoke_model(question) -> str:
    prompt = search_prompt(question)

    model = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"), temperature=0.5)
    return model.invoke(prompt).content


def main():
    console = Console()
    
    # Header do chat
    console.print()
    console.print()
    title = Text("🤖 Busca utilizando RAG", style="bold magenta")
    console.print(Align.left(title))
    console.print()

    # Instruções
    instructions = Panel(
        "[bold cyan]Instruções:[/bold cyan]\n"
        "• Faça sua pergunta e pressione Enter\n"
        "• Digite 'sair', 'quit' ou 'exit' para encerrar o chat\n"
        "• Digite 'limpar' para limpar a tela\n"
        "• Digite 'ajuda' para ver os comandos",
        border_style="green"
    )
    console.print(instructions)
    console.print()

    while True:
        try:
            # Input do usuário com estilo
            user_input = Prompt.ask(
                "[bold green]Pergunta[/bold green]"
            ).strip()
            
            # Comandos especiais
            if user_input.lower() in ['sair', 'quit', 'exit']:
                if Confirm.ask("[yellow]Tem certeza que deseja sair?[/yellow]"):
                    console.print("\n[bold blue]👋 Até logo![/bold blue]")
                    console.print()
                    break
                else:
                    continue
                    
            elif user_input.lower() == 'limpar':
                console.clear()
                continue
                
            elif user_input.lower() == 'ajuda':
                help_panel = Panel(
                    "[bold]Comandos disponíveis:[/bold]\n\n"
                    "[green]sair/quit/exit[/green] - Encerra o chat\n"
                    "[green]limpar[/green] - Limpa a tela\n"
                    "[green]ajuda[/green] - Mostra esta ajuda\n",
                    title="Ajuda",
                    title_align="left",
                    border_style="yellow"
                )
                console.print()
                console.print(help_panel)
                console.print()
                continue        
                        
            # Ignora inputs vazios
            if not user_input:
                console.print("[dim]Por favor, digite uma mensagem.[/dim]")
                continue
            
            with console.status("[bold green]buscando resposta...", spinner="dots"):
                response = _invoke_model(user_input)
            
            
            # Exibe a resposta em um painel estilizado
            console.print()
            console.print(Text("Resposta:", style="cyan"))
            response_panel = Panel(
                response,
                border_style="cyan",
                padding=(0, 1)
            )
            console.print(response_panel)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido pelo usuário.[/yellow]")
            if Confirm.ask("[yellow]Deseja realmente sair?[/yellow]"):
                console.print("\n[bold blue]👋 Até logo![/bold blue]")
                console.print()
                break
        except EOFError:
            console.print("\n[bold blue]👋 Até logo![/bold blue]")
            console.print()
            break

if __name__ == "__main__":
    main()