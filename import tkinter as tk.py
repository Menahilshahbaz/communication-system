import tkinter as tk
from tkinter import messagebox
from collections import defaultdict, deque
import time

class CommunicationSystem:
    def __init__(self):
        self.users = {}  # {user_id: username}
        self.user_inboxes = defaultdict(deque)  # {user_id: deque([messages])}
        self.current_user_id = 1

    def register_user(self, username):
        user_id = str(self.current_user_id)
        self.users[user_id] = username
        self.user_inboxes[user_id] = deque()
        self.current_user_id += 1
        return user_id

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            del self.user_inboxes[user_id]
        else:
            raise ValueError("User does not exist.")

    def send_message(self, sender_id, receiver_id, message_body,sender_name,receiver_name):
        if sender_id not in self.users or receiver_id not in self.users:
            raise ValueError("Sender or Receiver does not exist.")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        message_to_receiver = {
            "index": len(self.user_inboxes[receiver_id]),
            "from": "Receiver",
            "to": receiver_name,
            "message": message_body,
            "time": timestamp,
        }
        message_to_sender = {
            "index": len(self.user_inboxes[sender_id]),
            "from": "Sender",
            "to": sender_name,
            "message": message_body,
            "time": timestamp,
        }
        self.user_inboxes[receiver_id].append(message_to_receiver)
        self.user_inboxes[sender_id].append(message_to_sender)

    def retrieve_inbox(self, user_id):
        if user_id not in self.users:
            raise ValueError("User does not exist.")
        return list(self.user_inboxes[user_id])

    def delete_message(self, user_id, index):
        if user_id in self.user_inboxes and 0 <= index < len(self.user_inboxes[user_id]):
            del self.user_inboxes[user_id][index]
            # Update indices for remaining messages
            for i, msg in enumerate(self.user_inboxes[user_id]):
                msg["index"] = i
        else:
            raise ValueError("Invalid message index.")

    def search_message(self, user_id, keyword):
        if user_id not in self.users:
            raise ValueError("User does not exist.")
        return [msg for msg in self.user_inboxes[user_id] if keyword.lower() in msg["message"].lower()]

class ChatGUI:
    def __init__(self, root, system):
        self.system = system
        self.root = root
        self.root.title("Chat Application")
        self.root.configure(bg="#ECE5DD")

        # User Registration Frame
        self.user_frame = tk.Frame(self.root, bg="#25D366", padx=10, pady=5)
        self.user_frame.pack(fill="x")

        tk.Label(self.user_frame, text="Register New User", bg="#25D366", fg="white", font=("Helvetica", 12)).pack(side="left")
        self.username_entry = tk.Entry(self.user_frame, width=20)
        self.username_entry.pack(side="left", padx=5)
        tk.Button(self.user_frame, text="Register", command=self.register_user).pack(side="left")

        # Chat Box
        self.chat_box = tk.Text(self.root, height=20, state=tk.DISABLED, bg="#FFFFFF", fg="#000", font=("Helvetica", 10), wrap="word")
        self.chat_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Message Entry Frame
        self.message_frame = tk.Frame(self.root, bg="#ECE5DD", pady=5)
        self.message_frame.pack(fill="x")

        tk.Label(self.message_frame, text="Sender ID:", bg="#ECE5DD").grid(row=0, column=0, padx=5)
        self.sender_id_entry = tk.Entry(self.message_frame, width=10)
        self.sender_id_entry.grid(row=0, column=1)

        tk.Label(self.message_frame, text="Receiver ID:", bg="#ECE5DD").grid(row=0, column=2, padx=5)
        self.receiver_id_entry = tk.Entry(self.message_frame, width=10)
        self.receiver_id_entry.grid(row=0, column=3)

        tk.Label(self.message_frame, text="Message:", bg="#ECE5DD").grid(row=1, column=0, padx=5)
        self.message_entry = tk.Entry(self.message_frame, width=40)
        self.message_entry.grid(row=1, column=1, columnspan=3, pady=5)

        tk.Button(self.message_frame, text="Send", bg="#128C7E", fg="white", command=self.send_message).grid(row=0, column=4, rowspan=2, padx=5)

        # Tools Frame
        self.tools_frame = tk.Frame(self.root, bg="#ECE5DD")
        self.tools_frame.pack(fill="x")

        tk.Label(self.tools_frame, text="Search (User ID):", bg="#ECE5DD").pack(side="left")
        self.search_user_id_entry = tk.Entry(self.tools_frame, width=10)
        self.search_user_id_entry.pack(side="left", padx=5)

        tk.Label(self.tools_frame, text="Keyword:", bg="#ECE5DD").pack(side="left")
        self.search_keyword_entry = tk.Entry(self.tools_frame, width=20)
        self.search_keyword_entry.pack(side="left", padx=5)
        tk.Button(self.tools_frame, text="Search", command=self.search_message).pack(side="left", padx=5)

        tk.Label(self.tools_frame, text="Delete Message (ID, Index):", bg="#ECE5DD").pack(side="left")
        self.delete_user_entry = tk.Entry(self.tools_frame, width=10)
        self.delete_user_entry.pack(side="left")
        self.delete_index_entry = tk.Entry(self.tools_frame, width=5)
        self.delete_index_entry.pack(side="left", padx=5)
        tk.Button(self.tools_frame, text="Delete", command=self.delete_message).pack(side="left", padx=5)

        # Retrieve Inbox
        tk.Label(self.tools_frame, text="Inbox (User ID):", bg="#ECE5DD").pack(side="left")
        self.inbox_user_id_entry = tk.Entry(self.tools_frame, width=10)
        self.inbox_user_id_entry.pack(side="left", padx=5)
        tk.Button(self.tools_frame, text="Retrieve", command=self.retrieve_inbox).pack(side="left", padx=5)

        # Delete User
        tk.Label(self.tools_frame, text="Delete User (ID):", bg="#ECE5DD").pack(side="left")
        self.delete_user_id_entry = tk.Entry(self.tools_frame, width=10)
        self.delete_user_id_entry.pack(side="left", padx=5)
        tk.Button(self.tools_frame, text="Delete User", command=self.delete_user).pack(side="left", padx=5)

    def refresh_chat(self, messages=None):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        if messages is None:
            messages = []
            for user_id in self.system.users:
                messages.extend(self.system.retrieve_inbox(user_id))
        for message in messages:
            formatted_message = f"[{message['index']}] {message['from']} -> {message['to']} ({message['time']}):\n   {message['message']}\n\n"
            self.chat_box.insert(tk.END, formatted_message)
        self.chat_box.config(state=tk.DISABLED)

    def register_user(self):
        username = self.username_entry.get()
        if username:
            user_id = self.system.register_user(username)
            messagebox.showinfo("Success", f"User Registered: {username} (ID: {user_id})")
            self.username_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Username cannot be empty")

    def send_message(self):
        sender_id = self.sender_id_entry.get()
        receiver_id = self.receiver_id_entry.get()
        message = self.message_entry.get()
        sender_name = self.system.users[sender_id]
        receiver_name = self.system.users[receiver_id]
        try:
            self.system.send_message(sender_id, receiver_id, message,sender_name,receiver_name)
            self.message_entry.delete(0, tk.END)
            self.refresh_chat()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def search_message(self):
        user_id = self.search_user_id_entry.get()
        keyword = self.search_keyword_entry.get()
        try:
            messages = self.system.search_message(user_id, keyword)
            self.refresh_chat(messages)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_message(self):
        user_id = self.delete_user_entry.get()
        try:
            index = int(self.delete_index_entry.get())
            self.system.delete_message(user_id, index)
            self.refresh_chat()
            messagebox.showinfo("Success", "Message Deleted")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def retrieve_inbox(self):
        user_id = self.inbox_user_id_entry.get()
        try:
            messages = self.system.retrieve_inbox(user_id)
            self.refresh_chat(messages)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        user_id = self.delete_user_id_entry.get()
        try:
            self.system.delete_user(user_id)
            self.refresh_chat()
            messagebox.showinfo("Success", f"User {user_id} deleted")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    system = CommunicationSystem()
    app = ChatGUI(root, system)
    root.mainloop()
