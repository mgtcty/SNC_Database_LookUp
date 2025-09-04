import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QListWidgetItem,
                             QTextEdit, QLineEdit, QFileDialog, QLabel, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os
from backend.DatabaseHandler import DatabaseManager
from dotenv import load_dotenv
from backend.Retriever import Retriever
from backend.Generator import Generator
from backend.Reranker import Reranker

class AIManualAssistant(QWidget):
    def __init__(self):
        # === Load .env ===
        load_dotenv()
        creds = {k: os.getenv(k) for k in ["user", "password", "host", "port", "dbname"]}

        # === Database ===
        url = f"postgresql+psycopg2://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"
        self.db = DatabaseManager(url)
        os.system("cls")

        # Get manual names and IDs from the database
        self.id_ls, self.manual_ls = self.db.getManualNameIdPairs()
        self.contents, self.ids = self.db.giveSections()
        os.system("cls")
        print(len(self.contents))

        # === AI Models ===
        self.retriever = Retriever()
        print("Retriever initialized.")
        self.reranker = Reranker()
        print("Reranker initialized.")
        self.generator = Generator()
        print("Generator initialized.") 

        # === UI Setup ===
        super().__init__()
        self.initUI()
        self.manuals = []

    def initUI(self):
        self.setWindowTitle('AI Manual Assistant')
        self.setGeometry(100, 100, 1200, 900)
        self.setStyleSheet("QWidget { background-color: #F4F4F6; font-family: Arial; color: black; }")

        main_layout = QHBoxLayout()

        # Left Panel (Manuals)
        manuals_label = QLabel('<b>Available Manuals</b>')
        manuals_label.setStyleSheet("font-size: 14pt;")
        left_panel_layout = QVBoxLayout()
        left_panel_layout.addWidget(manuals_label)
        
        self.manuals_list = QListWidget()
        self.manuals_list.setStyleSheet("""
            QListWidget {
                border-radius: 10px;
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 12pt;
                background-color: #3C3B3D;
            }
            QListWidget::item {
                padding: 10px;
                color: #F4F4F6;
            }
        """)

        # Add manuals from the database
        for i in range(len(self.manual_ls)):
            manual_name = self.manual_ls[i]
            manual_id = i + 1
            formatted_item = f"{manual_id}.) {manual_name}"
            self.manuals_list.addItem(formatted_item)
        left_panel_layout.addWidget(self.manuals_list)
        
        # Browse Button
        self.browse_pdf_btn = QPushButton('Add New Manual (PDF)')
        self.browse_pdf_btn.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                background-color: #9999A1;
                color: #191A20;
                padding: 10px;
                border: none;
                font-size: 12pt;
                padding-left: 10px;
            }
            QPushButton:hover {
                color: white;
                background-color: #3C3B3D;
                font-size: 12pt;
            }
        """)
        self.browse_pdf_btn.clicked.connect(self.browseForPDF)
        left_panel_layout.addWidget(self.browse_pdf_btn)

        # Right Panel (Chat)
        chat_label = QLabel('<b>Chat with Llama SNC AI</b>')
        chat_label.setStyleSheet("padding-left: 5px; font-size: 14pt;")
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(chat_label)
        
        # Chat History
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border-radius: 10px;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #3C3B3D;
                color: #F4F4F6;
                font-size: 12pt;
            }
        """)
        right_panel_layout.addWidget(self.chat_history)

        # Create the user input field
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message...")
        self.user_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                padding: 8px 15px;
                padding-right: 30px;
                border: 1px solid #ccc;
                font-size: 12pt;
                padding-right: 35px; /* Make space for the icon */
            }
        """)

        # Disclaimer label
        self.disclaimer_label = QLabel('Llama SNC AI may still make mistake. Check sources.')
        self.disclaimer_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #888888;
                padding: 5px;
            }
        """)
        self.disclaimer_label.setAlignment(Qt.AlignCenter)
        right_panel_layout.addWidget(self.disclaimer_label)

        # Create the send icon and action
        send_icon = QIcon("frontend/send-31.png")

        send_action = QAction(send_icon, "Send", self)
        send_action.triggered.connect(self.generateAIResponse)

        send_action = QAction(send_icon, "Send", self)
        send_action.triggered.connect(self.generateAIResponse)

        # Add the action to the right side of the QLineEdit
        self.user_input.addAction(send_action, QLineEdit.TrailingPosition)

        # Enter key
        self.user_input.returnPressed.connect(self.generateAIResponse)
        
        right_panel_layout.addWidget(self.user_input)

        main_layout.addLayout(left_panel_layout, 1)
        main_layout.addLayout(right_panel_layout, 2)

        self.setLayout(main_layout)

    def browseForPDF(self):
        """
        Opens a file dialog to select a PDF manual and adds it to the manuals list and database.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Manual", "", "PDF Files (*.pdf)")
        if file_path:
            self.manuals.append(file_path)
            filename = file_path.split('/')[-1]
            QListWidgetItem(filename, self.manuals_list)
            self.chat_history.append(f"<i>Manual '{filename}' has been added.</i>")

    def generateAIResponse(self, relevantSections=20):
        """
        Generates an AI response based on user input and updates the chat history.
        """
        userMessage = self.user_input.text()
        if not userMessage:
            return

        self.chat_history.append(f"<b>You:</b> {userMessage}")
        self.user_input.clear()

        if "hello" in userMessage.lower():
            aiResponse = "Hello! How can I help you with the manuals today?"
        elif "manuals" in userMessage.lower():
            if self.manuals:
                manualNames = ", ".join([path.split('/')[-1] for path in self.manuals])
                aiResponse = f"I have the following manuals available: {manualNames}."
            else:
                aiResponse = "There are no manuals loaded yet. Please add new manuals"
        else:
            # add and store in a vector database
            self.retriever.add(self.contents, self.ids)

            # retrieve [number] relevant sections using faisss
            topIds = self.retriever.search(userMessage, top_k=relevantSections)
            topContents, top_section_ids, sectionNumbers = self.db.giveSections(topIds)

            # rerank sections
            rerankedContents = self.reranker.rerank(userMessage, topContents, top_k=4)

            # generate response using TinyLlama (model used in Generator.py)
            print("Generating response...\n\n")
            aiResponse = self.generator.generate(userMessage, rerankedContents, sectionNumbers)
            print(aiResponse)

        self.chat_history.append(f"<b>AI:</b> {aiResponse}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AIManualAssistant()
    ex.show()
    sys.exit(app.exec_())