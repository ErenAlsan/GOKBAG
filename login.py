import os
import json
import tkinter as tk
from tkinter import messagebox
from utilities.user_management import hash_password, generate_salt, update_user_data, generate_password, load_users
from drone_controller import DroneController

user_data_file = "user_data.json"
users = load_users(user_data_file)

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")
        self.root.geometry("400x300")

        self.username_label = tk.Label(root, text="Username")
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(root, text="Password")
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(root, show='*')
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in users:
            stored_password = users[username]['password']
            salt = bytes.fromhex(users[username]['salt'])
            if stored_password == hash_password(password, salt):
                if username == 'admin':
                    self.admin_page()
                else:
                    self.user_page()
            else:
                messagebox.showerror("Login Error", "Invalid username or password")
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    def admin_page(self):
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Admin Page")
        self.admin_window.geometry("400x400")

        self.user_listbox = tk.Listbox(self.admin_window)
        self.user_listbox.pack(pady=10)

        for user in users:
            self.user_listbox.insert(tk.END, f"{user}")

        self.edit_button = tk.Button(self.admin_window, text="Edit Selected User", command=self.edit_user)
        self.edit_button.pack(pady=10)

        self.new_password_entry = tk.Entry(self.admin_window)
        self.new_password_entry.pack(pady=10)
        self.new_password_entry.insert(0, "New Password")

        self.save_button = tk.Button(self.admin_window, text="Save New Password", command=self.save_password, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        self.random_password_button = tk.Button(self.admin_window, text="Assign Random Password", command=self.assign_random_password, state=tk.DISABLED)
        self.random_password_button.pack(pady=10)

    def edit_user(self):
        selected = self.user_listbox.curselection()
        if not selected:
            return

        index = selected[0]
        self.selected_user = self.user_listbox.get(index)
        self.new_password_entry.delete(0, tk.END)
        self.new_password_entry.insert(0, "New Password")

        self.save_button.config(state=tk.NORMAL)
        self.random_password_button.config(state=tk.NORMAL)

    def save_password(self):
        new_password = self.new_password_entry.get()
        new_salt = generate_salt()
        hashed_password = hash_password(new_password, new_salt)
        users[self.selected_user] = {'password': hashed_password, 'salt': new_salt.hex()}
        update_user_data(users, user_data_file)
        messagebox.showinfo("Password Update", "Password updated successfully")

    def assign_random_password(self):
        new_password = generate_password()
        new_salt = generate_salt()
        hashed_password = hash_password(new_password, new_salt)
        users[self.selected_user] = {'password': hashed_password, 'salt': new_salt.hex()}
        update_user_data(users, user_data_file)
        messagebox.showinfo("Password Update", f"New password for {self.selected_user}: {new_password}")

    def user_page(self):
        self.root.destroy()
        gui = DroneController()
        gui.run_app()
