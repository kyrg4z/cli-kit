from rich import print as rprint
from rich import pretty
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.text import Text

import sqlite3

console = Console()

def welcome():
    console.rule("[bold red] Journal ctl")
    header = Text("📝 PyTodo CLI App", style="bold green", justify="center")
    console.print(Panel(header, subtitle="Fast & Simple To-Do Manager", subtitle_align="right"))

    # Instructions table
    table = Table(title="📌 Available Commands", show_header=True, header_style="bold magenta")
    table.add_column("Key", justify="center", style="cyan", no_wrap=True)
    table.add_column("Action", style="white")

    table.add_row("[bold]q[/bold]", "Quit the application")
    table.add_row("[bold]c[/bold]", "Add a new task")
    table.add_row("[bold]r[/bold]", "List all tasks")
    table.add_row("[bold]u[/bold]", "Update a task")
    table.add_row("[bold]d[/bold]", "Remove a task")
    console.print(table)


def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority INTEGER,
        completed BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def add_task(title, description="", due_date=None, priority=1):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)",
                  (title, description, due_date, priority))
    conn.commit()
    conn.close()

def read():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    for task in tasks:
        console.print(f"ID: {task[0]}, Title: {task[1]}, Description: {task[2]}, Due Date: {task[3]}, Priority: {task[4]}, Completed: {task[5]}")

def update():
    task_id = console.input("Enter the ID of the task to update: ")
    title = console.input("Enter the new title: ")
    description = console.input("Enter the new description: ")
    due_date = console.input("Enter the new due date: ")
    priority = console.input("Enter the new priority: ")
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title=?, description=?, due_date=?, priority=? WHERE id=?",
                  (title, description, due_date, priority, task_id))
    conn.commit()
    conn.close()

def delete():
    task_id = console.input("Enter the ID of the task to delete: ")
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# json.loads()


if __name__ == "__main__":
    welcome()
    init_db()

    while True:
        command = console.input("")
        if command == "q":
            break  
        elif command == "c":
            title = console.input("Enter a task title: ")
            description = console.input("Enter a task description: ")
            due_date = console.input("Enter a task due date: ")
            priority = console.input("Enter a task priority: ")
            add_task(title, description, due_date, priority)
        elif command == "r":
            read()
        elif command == "u":
            update()
        elif command == "d":
            delete()

        else:
            print("Unknown command. Please try again")
    
