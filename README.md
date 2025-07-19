# 🧾 Voice-Activated Expense Tracker

A voice-driven expense tracker that allows users to **call a phone number**, speak their expenses naturally, and have them **automatically logged to their personal Google Sheet**.

Built for the **Vapi Build Challenge** 🛠️ using:

- [Vapi](https://vapi.ai/) for voice assistant and phone interface
- **Flask (Python)** for backend
- **Google Sheets API** for expense storage

---

## 📞 How It Works

1. The user calls the Vapi-assigned number.
2. The voice assistant (powered by Vapi) asks for expense details like:
   - "How much did you spend?"
   - "What was it for?"
   - "When did this happen?"
3. Once the user responds, the assistant sends structured data to the Flask backend.
4. The backend:
   - Creates a new sheet for first-time users
   - Logs expenses for existing users
   - Allows editing, summarizing, budgeting, and deletion

---

## 🔧 Features

✅ Log expenses via voice  
✅ Auto-create a Google Sheet per user  
✅ Track monthly expenses by category  
✅ Edit or delete expenses  
✅ Summarize totals and budgets via voice  
✅ SMS confirmation via Twilio (optional)

---

## 🛠️ Tech Stack

| Layer           | Tech                         |
| --------------- | ---------------------------- |
| Voice Assistant | Vapi                         |
| Backend         | Flask (Python)               |
| Storage         | Google Sheets API            |
| Auth            | Google Cloud Service Account |

---

## 📂 Folder Structure

```

📁 voice-expense-tracker/
├── app.py                   # Main Flask server
├── utils.py                 # Google Sheets helper functions
├── credentials.json         # Google service account creds
├── requirements.txt         # Python dependencies
└── README.md

```

---

## 🔐 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/voice-expense-tracker.git
cd voice-expense-tracker
```

### 2. Create a Google Cloud Project

- Enable **Google Sheets API**
- Create a **Service Account** and download `credentials.json`
- Share your target spreadsheet with the service account email

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Flask App

```bash
python app.py
```

> The server runs at `http://localhost:5000`

---

## 🔌 API Endpoints

| Method | Route             | Description                       |
| ------ | ----------------- | --------------------------------- |
| POST   | `/log-expense`    | Logs a new expense                |
| POST   | `/edit-expense`   | Edits an existing expense entry   |
| POST   | `/delete-expense` | Deletes an expense                |
| POST   | `/set-budget`     | Sets budget                       |
| POST   | `/get-expenses`   | Fetches all expenses for a user   |
| POST   | `/summary`        | Returns monthly/overall summary   |
| POST   | `/budget`         | Returns remaining budget by month |

All endpoints accept and return **JSON**.

---

## 🗣️ Vapi Assistant Configuration

### Tool: `log_expense`

```json
{
  "name": "log_expense",
  "description": "Log an expense to the backend",
  "parameters": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "category": { "type": "string" },
      "amount": { "type": "number" },
      "date": { "type": "string" }
    },
    "required": ["category", "amount", "date"]
  }
}
```

Repeat similarly for `edit_expense`, `delete_expense`, etc.

---

## 🚀 Example Voice Flow

**User:** "Hey, I spent 300 rupees on groceries yesterday."

**Assistant:**

> "Got it! Logging ₹300 for groceries on May 27. Anything else you'd like to add?"

---

## 🧪 Sample Request

### `POST /log-expense`

```json
{
  "name": "Aditya",
  "category": "Food",
  "amount": 500,
  "date": "2025-05-28"
}
```

---

## ✨ Credits

Built by [Aditya](https://github.com/Paulie-Aditya) for the Vapi Build Challenge 2025
Inspired by the idea of **natural, zero-friction expense tracking** using voice and LLMs

---

## 📜 License

MIT License – feel free to fork, extend, and deploy.
