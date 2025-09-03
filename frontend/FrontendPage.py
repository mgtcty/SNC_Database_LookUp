import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QListWidgetItem,
                             QTextEdit, QLineEdit, QFileDialog, QLabel, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class AIManualAssistant(QWidget):
    def __init__(self):
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
                background-color: #3C3B3D;
            }
        """)
        left_panel_layout.addWidget(self.manuals_list)
        
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
        self.browse_pdf_btn.clicked.connect(self.browse_for_pdf)
        left_panel_layout.addWidget(self.browse_pdf_btn)

        # Right Panel (Chat)
        chat_label = QLabel('<b>Chat with SNC AI</b>')
        chat_label.setStyleSheet("padding-left: 5px; font-size: 14pt;")
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(chat_label)
        
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

        # --- MODIFIED SECTION ---
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

        # Create the send icon and action
        send_icon = QIcon("send-31.png")

        send_action = QAction(send_icon, "Send", self)
        send_action.triggered.connect(self.generate_ai_response)

        send_action = QAction(send_icon, "Send", self)
        send_action.triggered.connect(self.generate_ai_response)

        # Add the action to the right side of the QLineEdit
        self.user_input.addAction(send_action, QLineEdit.TrailingPosition)

        # Enter key
        self.user_input.returnPressed.connect(self.generate_ai_response)
        
        right_panel_layout.addWidget(self.user_input)

        main_layout.addLayout(left_panel_layout, 1)
        main_layout.addLayout(right_panel_layout, 2)

        self.setLayout(main_layout)

    def browse_for_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Manual", "", "PDF Files (*.pdf)")
        if file_path:
            self.manuals.append(file_path)
            filename = file_path.split('/')[-1]
            QListWidgetItem(filename, self.manuals_list)
            self.chat_history.append(f"<i>Manual '{filename}' has been added.</i>")

    def generate_ai_response(self):
        user_message = self.user_input.text()
        if not user_message:
            return

        self.chat_history.append(f"<b>You:</b> {user_message}")
        self.user_input.clear()

        if "hello" in user_message.lower():
            ai_response = "Hello! How can I help you with the manuals today?"
        elif "manuals" in user_message.lower():
            if self.manuals:
                manual_names = ", ".join([path.split('/')[-1] for path in self.manuals])
                ai_response = f"I have the following manuals available: {manual_names}."
            else:
                ai_response = "There are no manuals loaded yet. Please add new manuals"
        else:
            ai_response = "I'm sorry, I can't provide a detailed response to that query yet. I'm a simple manual assistant!"
            
        self.chat_history.append(f"<b>AI:</b> {ai_response}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AIManualAssistant()
    ex.show()
    sys.exit(app.exec_())