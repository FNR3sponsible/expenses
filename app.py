import sqlite3
import json
con = sqlite3.connect('database.db')
cur = con.cursor()
where = False
def create_table():
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    pwd TEXT NOT NULL)''')
    con.commit()

def reg():
    username = input("Enter username: ")
    pwd = input("Enter password: ")
    print(f"Username: {username}, Password: {pwd}")
    cur.execute("INSERT INTO users (username, pwd) VALUES (?, ?)", (username, pwd))
    con.commit()

def login():
    username = input("Enter username: ")
    pwd = input("Enter password: ")
    cur.execute("SELECT * FROM users WHERE username=? AND pwd=?", (username, pwd))
    user = cur.fetchone()
    if user:
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False

def main():
    while True:
        choice = input("Enter 1 to register, 2 to login, or 3 to exit: ")
        if choice == '1':
            reg()
        elif choice == '2':
            if login():
                to_do_main()
                break
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def to_do_main():
    while True:
        choice = input("Enter 1 to add a to-do item, 2 to view to-do items, or 3 to exit: ")
        if choice == '1':
            item = input("Enter a to-do item: ")
            try:
                with open('todo.json', 'r') as f:
                    todo_list = json.load(f)
            except FileNotFoundError:
                todo_list = []
            todo_list.append(item)
            with open('todo.json', 'w') as f:
                json.dump(todo_list, f)
        elif choice == '2':
            try:
                with open('todo.json', 'r') as f:
                    todo_list = json.load(f)
                print("To-Do List:")
                for idx, item in enumerate(todo_list, 1):
                    print(f"{idx}. {item}")
            except FileNotFoundError:
                print("No to-do items yet.")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    create_table()
    main()