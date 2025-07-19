from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
from datetime import datetime
import gspread
import pandas as pd
from dotenv import load_dotenv
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID") 
credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- Helpers ---
def get_or_create_user_sheet(username):
    try:
        return spreadsheet.worksheet(username)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=username, rows="1000", cols="6")
        sheet.append_row(["ID", "Timestamp", "Amount", "Category", "Description", "Notes"])
        return sheet

def sheet_to_df(sheet):
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# --- Routes ---

@app.route("/log-expense", methods=["POST"])
def log_expense():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username", "amount", "category", "description"]
    if not all(k in data for k in required):
        return jsonify({
            "results": [
                {
                    "toolCallId": toolCallId,
                    "result": {"error": "Missing required fields"}
                }
            ]
        }), 400

    sheet = get_or_create_user_sheet(data["username"])
    rows = sheet.get_all_values()
    next_id = len(rows) if len(rows) > 1 else 1

    sheet.append_row([
        next_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["amount"],
        data["category"],
        data["description"],
        data.get("notes", "")
    ])
    return jsonify({
        "results": [
            {
                "toolCallId": toolCallId,
                "result": {"message": "Expense logged", "id": next_id}
            }
        ]
    }), 200

@app.route("/edit-expense", methods=["POST"])
def edit_expense():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username", "id"]
    if not all(k in data for k in required):
        return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Missing fields"}
                    }
                ]
            }), 400

    sheet = get_or_create_user_sheet(data["username"])
    rows = sheet.get_all_values()
    for idx, row in enumerate(rows[1:], start=2):
        if str(row[0]) == str(data["id"]):
            sheet.update(f"A{idx}:F{idx}", [[
                data["id"],
                row[1],  # Keep original timestamp
                data.get("new_amount", row[2]),
                data.get("new_category", row[3]),
                data.get("new_description", row[4]),
                data.get("new_notes", row[5]),
            ]])
            return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Expense updated"}
                    }
                ]
            }), 200
    return jsonify({
        "results": [
            {
                "toolCallId": toolCallId,
                "result": {"error": "Expense not found"}
            }
        ]
    }), 404

@app.route("/summary", methods=["POST"])
def summary():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username"]
    if not all(k in data for k in required):
        return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Missing fields"}
                    }
                ]
            }), 400
    username = data.get("username")
    period = data.get("period","month")
    category = data.get("category")

    sheet = get_or_create_user_sheet(username)
    df = sheet_to_df(sheet)

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    now = datetime.now()
    if period == "today":
        df = df[df["Timestamp"].dt.date == now.date()]
    elif period == "week":
        df = df[df["Timestamp"] >= now - pd.Timedelta(days=7)]
    elif period == "month":
        df = df[df["Timestamp"].dt.month == now.month]

    if category:
        df = df[df["Category"] == category]

    total = df["Amount"].astype(float).sum()
    return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"total": total, "count": len(df)}
                    }
                ]
        }), 200

@app.route("/set-budget", methods=["POST"])
def set_budget():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username", "category", "amount"]
    if not all(k in data for k in required):
        return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Missing fields"}
                    }
                ]
            }), 400

    sheet = get_or_create_user_sheet(data["username"])
    settings_sheet = get_or_create_user_sheet(data["username"] + "_budget")
    rows = settings_sheet.get_all_values()
    found = False

    for idx, row in enumerate(rows[1:], start=2):
        if row[0] == data["category"]:
            settings_sheet.update_cell(idx, 2, data["amount"])
            found = True
            break
    if not found:
        settings_sheet.append_row([data["category"], data["amount"]])
    return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Budget updated"}
                    }
                ]
            }), 200

@app.route("/get-expenses", methods=["POST"])
def get_expenses():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username"]
    if not all(k in data for k in required):
        return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Missing fields"}
                    }
                ]
            }), 400
    username = data.get("username")
    sheet = get_or_create_user_sheet(username)
    rows = sheet.get_all_records()
    return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"expenses": rows[-5:]}
                    }
                ]
            }), 200

# @app.route("/delete-expense", methods=["POST"])
# def delete_expense():
#     data = request.json
#     required = ["username", "id"]
#     if not all(k in data for k in required):
#         return jsonify({"error": "Missing fields"}), 400

#     sheet = get_or_create_user_sheet(data["username"])
#     rows = sheet.get_all_values()
#     for idx, row in enumerate(rows[1:], start=2):
#         if str(row[0]) == str(data["id"]):
#             sheet.delete_row(idx)
#             return jsonify({"message": "Expense deleted"}), 200
#     return jsonify({"error": "Expense not found"}), 404

@app.route("/top-categories", methods=["POST"])
def top_categories():
    raw_data = request.get_data(as_text=True)
    data = json.loads(raw_data)
    toolCallId = data['message']['toolCalls'][-1]['id']
    data = data['message']['toolCalls'][-1]['function']['arguments']
    required = ["username"]
    if not all(k in data for k in required):
        return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"message": "Missing fields"}
                    }
                ]
            }), 400
    username = data.get("username")
    sheet = get_or_create_user_sheet(username)
    df = sheet_to_df(sheet)
    df["Amount"] = df["Amount"].astype(float)
    grouped = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top = grouped.head(3).reset_index().to_dict(orient="records")
    return jsonify({
                "results": [
                    {
                        "toolCallId": toolCallId,
                        "result": {"top_categories": top}
                    }
                ]
            }), 200

if __name__ == "__main__":
    app.run(debug=True)
