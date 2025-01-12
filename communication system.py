import tkinter as tk
from tkinter import messagebox, simpledialog
import heapq
from collections import defaultdict
from datetime import datetime


class MessageNode:
    def __init__(self, message_id, sender_id, receiver_id, message_body, timestamp):
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_body = message_body
        self.timestamp = timestamp
        self.next = None

class MessageLinkedList:
    def __init__(self):
        self.head = None

    def add_message(self, message_node):
        if not self.head:
            self.head = message_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = message_node

    def delete_message(self, message_id):
        current = self.head
        prev = None
        while current:
            if current.message_id == message_id:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return True
            prev = current
            current = current.next
        return False

    def get_messages(self):
        messages = []
        current = self.head
        while current:
            messages.append((current.timestamp, current))
            current = current.next
        return messages

class CommunicationSystem:
    def __init__(self):
        self.users = {} 
        self.user_inboxes = defaultdict(MessageLinkedList)  
        self.messages = {}  
        self.keyword_index = defaultdict(list)
        self.next_user_id = 1  

    def register_user(self, username):
        user_id = str(self.next_user_id)
        self.next_user_id += 1
        self.users[user_id] = username
        return user_id

    def send_message(self, sender_id, receiver_id, message_body):
        if sender_id not in self.users or receiver_id not in self.users:
            return None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_id = f"m{len(self.messages) + 1}"
        new_message = MessageNode(message_id, sender_id, receiver_id, message_body, timestamp)
        self.user_inboxes[receiver_id].add_message(new_message)
        self.messages[message_id] = new_message
        for word in message_body.split():
            self.keyword_index[word.lower()].append(message_id)
            return message_id
    def retrieve_inbox(self, user_id):
        if user_id not in self.users:
            return []
        messages = self.user_inboxes[user_id].get_messages()
        heapq.heapify(messages)
        sorted_messages = []
        chat_partners = set()
        while messages:
            _, message = heapq.heappop(messages)
            sorted_messages.append(message)
            chat_partners.add(message.sender_id)
        return sorted_messages, chat_partners

    def search_messages(self, keyword):
        keyword = keyword.lower()
        if keyword not in self.keyword_index:
            return []
        return [self.messages[message_id] for message_id in self.keyword_index[keyword]]

    def delete_message(self, user_id, message_id):
        if message_id not in self.messages:
            return False

        message = self.messages[message_id]
        if user_id != message.receiver_id:
            return False

        success = self.user_inboxes[user_id].delete_message(message_id)
        if success:
            for word in message.message_body.split():
                word = word.lower()
                self.keyword_index[word].remove(message_id)
                if not self.keyword_index[word]:
                    del self.keyword_index[word]
            del self.messages[message_id]
            return True
        return False

    def delete_user(self, user_id):
        if user_id in self.users:
            current = self.user_inboxes[user_id].head
            while current:
                del self.messages[current.message_id]
                current = current.next
            del self.user_inboxes[user_id]
            del self.users[user_id]
            return True
        return False


class CommunicationSystemGUI:
    def __init__(self, root):
        self.system = CommunicationSystem()
        self.root = root
        self.root.title("DSA-GRAM")
        
        self.frame = tk.Frame(root, bg="lightblue")  # Set background color for the 
        self.frame = tk.Frame(root)
        self.frame.pack(pady=12)

        tk.Button(self.frame, text="User Registration", command=self.register_user).grid(row=0, column=0, padx=5)
        tk.Button(self.frame, text="Messages", command=self.send_message).grid(row=0, column=1, padx=5)
        tk.Button(self.frame, text="Inbox", command=self.retrieve_inbox).grid(row=0, column=2, padx=5)
        tk.Button(self.frame, text="Seach Msg", command=self.search_messages).grid(row=0, column=3, padx=5)
        tk.Button(self.frame, text="Del Msg", command=self.delete_message).grid(row=0, column=4, padx=5)
        tk.Button(self.frame, text="Del User", command=self.delete_user).grid(row=0, column=5, padx=5)

        self.output = tk.Text(root, width=80, height=40, bg="white", fg="black")  # Text widget with white background and black text
        self.output.pack(pady=12)

    def register_user(self):
        username = simpledialog.askstring("Register New User", "Enter username:")
        if username:
            user_id = self.system.register_user(username)
            self.output.insert(tk.END, f"User '{username}' registered with ID: {user_id}\n")

    def send_message(self):
        sender_id = simpledialog.askstring("Send Message", "Enter Sender ID:")
        receiver_id = simpledialog.askstring("Send Message", "Enter Receiver ID:")
        message_body = simpledialog.askstring("Send Message", "Enter Message:")
        if sender_id and receiver_id and message_body:
            message_id = self.system.send_message(sender_id, receiver_id, message_body)
            if message_id:
                self.output.insert(tk.END, f"Message sent with ID: {message_id}\n")
            else:
                messagebox.showerror("Error", "Invalid Sender or Receiver ID")

    def retrieve_inbox(self):
        user_id = simpledialog.askstring("Retrieve Inbox", "Enter User ID:")
        if user_id:
            messages, chat_partners = self.system.retrieve_inbox(user_id)
            if not messages:
                self.output.insert(tk.END, f"Inbox for User ID {user_id} is empty.\n")
                return
            self.output.insert(tk.END, f"Inbox for User ID {user_id} (Chatting with: {', '.join([self.system.users[pid] for pid in chat_partners])}):\n")
            for msg in messages:
                sender_name = self.system.users.get(msg.sender_id, "Unknown")
                self.output.insert(tk.END, f"[{msg.timestamp}] From {sender_name}: {msg.message_body}\n")

    def search_messages(self):
        keyword = simpledialog.askstring("Search Messages", "Enter Keyword:")
        if keyword:
            results = self.system.search_messages(keyword)
            self.output.insert(tk.END, f"Messages containing '{keyword}':\n")
            for msg in results:
                sender_name = self.system.users.get(msg.sender_id, "Unknown")
                receiver_name = self.system.users.get(msg.receiver_id, "Unknown")
                self.output.insert(tk.END, f"[{msg.timestamp}] From {sender_name} to {receiver_name}: {msg.message_body}\n")

    def delete_message(self):
        user_id = simpledialog.askstring("Delete Message", "Enter User ID:")
        message_id = simpledialog.askstring("Delete Message", "Enter Message ID:")
        if user_id and message_id:
            success = self.system.delete_message(user_id, message_id)
            if success:
                self.output.insert(tk.END, f"Message {message_id} deleted successfully.\n")
            else:
                messagebox.showerror("Error", "Invalid User ID or Message ID")

    def delete_user(self):
        user_id = simpledialog.askstring("Delete User", "Enter User ID:")
        if user_id:
            success = self.system.delete_user(user_id)
            if success:
                self.output.insert(tk.END, f"User {user_id} deleted successfully.\n")
            else:
                messagebox.showerror("Error", "Invalid User ID")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommunicationSystemGUI(root)
    root.mainloop()


