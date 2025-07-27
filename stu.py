# student_portal_ultimate_hybrid.py

import streamlit as st
import pandas as pd
import ollama
import os
import json
from web3 import Web3

# === CONFIG ===
NODE_URL = "http://127.0.0.1:8545"  # Change as needed
CONTRACT_ADDRESS = "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"  # Your deployed contract address

CONTRACT_ABI_JSON = """
[
  {
    "inputs": [{"internalType":"string","name":"_collegeName","type":"string"}],
    "name": "registerCollege",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"string","name":"_deptName","type":"string"},
      {"components": [
        {"internalType":"string","name":"name","type":"string"},
        {"internalType":"string","name":"role","type":"string"},
        {"internalType":"address","name":"wallet","type":"address"}
      ],"internalType":"struct CollegeAdmin.Faculty","name":"_faculty","type":"tuple"}
    ],
    "name": "addFaculty",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"},
      {"internalType":"string","name":"_subject","type":"string"},
      {"internalType":"uint8","name":"_marks","type":"uint8"}
    ],
    "name": "addMarks",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"},
      {"internalType":"uint256","name":"_pts","type":"uint256"}
    ],
    "name": "addPoints",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_wallet","type":"address"},
      {"components":[
        {"internalType":"string","name":"name","type":"string"},
        {"internalType":"string","name":"rollNo","type":"string"},
        {"internalType":"uint8","name":"year","type":"uint8"},
        {"internalType":"string","name":"department","type":"string"},
        {"internalType":"string","name":"section","type":"string"},
        {"internalType":"string","name":"email","type":"string"}
      ],"internalType":"struct CollegeAdmin.StudentInput","name":"_studentInput","type":"tuple"}
    ],
    "name": "addStudent",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"}
    ],
    "name": "redeemPoints",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"}
    ],
    "name": "getMarks",
    "outputs": [
      {"internalType":"string[]","name":"","type":"string[]"},
      {"internalType":"uint8[]","name":"","type":"uint8[]"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"}
    ],
    "name": "getPoints",
    "outputs": [{"internalType":"uint256","name":"","type":"uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"}
    ],
    "name": "getScholarship",
    "outputs": [{"internalType":"uint256","name":"","type":"uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType":"string","name":"_collegeName","type":"string"},
      {"internalType":"address","name":"_student","type":"address"}
    ],
    "name": "getStudent",
    "outputs": [{
      "components":[
        {"internalType":"string","name":"name","type":"string"},
        {"internalType":"string","name":"rollNo","type":"string"},
        {"internalType":"uint8","name":"year","type":"uint8"},
        {"internalType":"string","name":"department","type":"string"},
        {"internalType":"string","name":"section","type":"string"},
        {"internalType":"string","name":"email","type":"string"},
        {"internalType":"address","name":"wallet","type":"address"}
      ],
      "internalType":"struct CollegeAdmin.Student",
      "name":"",
      "type":"tuple"
    }],
    "stateMutability": "view",
    "type": "function"
  }
]
"""

CONTRACT_ABI = json.loads(CONTRACT_ABI_JSON)

# CSV files paths
STUDENTS_CSV = "students.csv"
GRADES_CSV = "grades.csv"
SCHOLARSHIPS_CSV = "scholarships.csv"
POINTS_CSV = "points.csv"

# --- Helper functions for CSV ---
def load_csv(file_path, columns):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)
    return pd.read_csv(file_path)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


# Load CSV files on app start
students_df = load_csv(STUDENTS_CSV, ['collegeName','wallet','name','rollNo','year','department','section','email'])
grades_df = load_csv(GRADES_CSV, ['collegeName','wallet','subject','marks'])
scholarships_df = load_csv(SCHOLARSHIPS_CSV, ['collegeName','wallet','amount'])
points_df = load_csv(POINTS_CSV, ['collegeName','wallet','points'])


# --- Web3 helper ---
def connect_blockchain():
    w3 = Web3(Web3.HTTPProvider(NODE_URL))
    if not w3.is_connected():
        return None, None
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    return w3, contract

def get_student_web3(contract, college, wallet):
    try:
        s = contract.functions.getStudent(college, wallet).call()
        if s[0] == "":
            return None
        return dict(name=s[0], rollNo=s[1], year=s[2], department=s[3], section=s[4], email=s[5], wallet=s[6])
    except Exception:
        return None

def get_grades_web3(contract, college, wallet):
    try:
        subjects, marks = contract.functions.getMarks(college, wallet).call()
        return subjects, marks
    except Exception:
        return [], []

def get_scholarship_web3(contract, college, wallet):
    try:
        return contract.functions.getScholarship(college, wallet).call()
    except Exception:
        return 0

def get_points_web3(contract, college, wallet):
    try:
        return contract.functions.getPoints(college, wallet).call()
    except Exception:
        return 0

def build_sign_send_tx(w3, priv_key, tx_function, gas=300000, gas_price_gwei=2):
    account = w3.eth.account.from_key(priv_key)
    nonce = w3.eth.get_transaction_count(account.address)
    tx = tx_function.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": gas,
        "gasPrice": w3.to_wei(gas_price_gwei, 'gwei'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, priv_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def redeem_points_web3(w3, contract, private_key, college_name):
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.redeemPoints(college_name).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 150000,
        'gasPrice': w3.to_wei('2', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()


# --- CSV fallback functions ---
def get_student_csv(college, wallet):
    wallet = wallet.lower()
    df = students_df[(students_df['collegeName'] == college) & (students_df['wallet'].str.lower() == wallet)]
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def get_grades_csv(college, wallet):
    wallet = wallet.lower()
    df = grades_df[(grades_df['collegeName'] == college) & (grades_df['wallet'].str.lower() == wallet)]
    if df.empty:
        return [], []
    return df['subject'].tolist(), df['marks'].astype(int).tolist()

def get_scholarship_csv(college, wallet):
    wallet = wallet.lower()
    df = scholarships_df[(scholarships_df['collegeName'] == college) & (scholarships_df['wallet'].str.lower() == wallet)]
    if df.empty:
        return 0
    return df.iloc[0]['amount']

def get_points_csv(college, wallet):
    wallet = wallet.lower()
    df = points_df[(points_df['collegeName'] == college) & (points_df['wallet'].str.lower() == wallet)]
    if df.empty:
        return 0
    return df.iloc[0]['points']

def redeem_points_csv(college, wallet):
    wallet = wallet.lower()
    global points_df
    idx = points_df[(points_df['collegeName'] == college) & (points_df['wallet'].str.lower() == wallet)].index
    if len(idx) == 0:
        return False, "No points available to redeem."
    current_points = points_df.at[idx[0], 'points']
    if current_points <= 0:
        return False, "No points available to redeem."
    points_df.at[idx[0], 'points'] = 0
    save_csv(points_df, POINTS_CSV)
    return True, f"Successfully redeemed {current_points} points."


# --- Streamlit app ---
def main():
    st.set_page_config(page_title="🎓 Hybrid Student Portal", layout="wide")

    web3mode = st.sidebar.checkbox("Use Blockchain (Web3)", value=True)

    college_name = st.sidebar.text_input("Enter College Name")
    wallet_address = st.sidebar.text_input("Your Ethereum Wallet Address")

    if not college_name or not wallet_address:
        st.warning("Please enter both College Name and Wallet Address in the sidebar.")
        return

    wallet_address = wallet_address.lower()

    if web3mode:
        w3, contract = connect_blockchain()
        if w3 is None or contract is None:
            st.error("Failed to connect to blockchain node. Using CSV fallback.")
            use_csv = True
        else:
            use_csv = False
    else:
        use_csv = True

    menu = st.sidebar.selectbox("Navigation", [
        "🏠 Home",
        "👤 Student Profile & Grades",
        "🎓 Scholarship & Rewards",
        "🛒 Redeem Points",
        "🤖 AI Campus Assistant",
        "⚙️ Account Settings",
        "ℹ️ About / Help"
    ])

    if menu == "🏠 Home":
        st.header("👋 Welcome to the Hybrid Student Portal")
        st.markdown("""
        This portal uses blockchain as source of truth if available, otherwise falls back to local CSV data.
        """)

    elif menu == "👤 Student Profile & Grades":
        st.header("📘 Your Academic Profile & Grades")

        if use_csv:
            student = get_student_csv(college_name, wallet_address)
            subjects, marks = get_grades_csv(college_name, wallet_address)
        else:
            student = get_student_web3(contract, college_name, wallet_address)
            subjects, marks = get_grades_web3(contract, college_name, wallet_address)

        if not student:
            st.info("Student record not found. Please verify your details.")
            return

        st.markdown(f"""
        ### Student Information
        - **Name:** {student.get('name')}
        - **Roll Number:** {student.get('rollNo')}
        - **Year:** {student.get('year')}
        - **Department:** {student.get('department')}
        - **Section:** {student.get('section')}
        - **Email:** {student.get('email')}
        - **Wallet:** {student.get('wallet')}
        """)

        if subjects:
            df_grades = pd.DataFrame({"Subject": subjects, "Marks": marks})
            st.subheader("Your Grades")
            st.table(df_grades)
        else:
            st.info("No grades found yet.")

    elif menu == "🎓 Scholarship & Rewards":
        st.header("🏅 Scholarship & Reward Points Overview")

        if use_csv:
            scholarship = get_scholarship_csv(college_name, wallet_address)
            points = get_points_csv(college_name, wallet_address)
        else:
            scholarship = get_scholarship_web3(contract, college_name, wallet_address)
            points = get_points_web3(contract, college_name, wallet_address)

        st.metric(label="Scholarship Amount", value=str(scholarship))
        st.metric(label="Reward Points", value=str(points))

    elif menu == "🛒 Redeem Points":
        st.header("🎁 Redeem Your Reward Points")

        if use_csv:
            points = get_points_csv(college_name, wallet_address)
        else:
            points = get_points_web3(contract, college_name, wallet_address)

        st.info(f"Current redeemable points: {points}")

        if points <= 0:
            st.warning("You have no points available to redeem.")
            return

        if st.button("Redeem Points"):
            if use_csv:
                success, msg = redeem_points_csv(college_name, wallet_address)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                priv_key = st.text_input("Enter your private key to sign the redeem transaction", type="password")
                if not priv_key:
                    st.error("Private key required for blockchain transaction.")
                else:
                    try:
                        tx_hash = redeem_points_web3(w3, contract, priv_key, college_name)
                        st.success(f"Redeem transaction submitted! TX Hash: {tx_hash}")
                    except Exception as e:
                        st.error(f"Redeem transaction failed: {e}")

    elif menu == "🤖 AI Campus Assistant":
        st.header("🤖 Campus AI Assistant powered by Ollama Models")

        system_prompt = (
            "You are a knowledgeable, friendly college AI assistant specializing in grades, scholarships, "
            "redeeming points, student administration, and campus life. Answer concisely and helpfully."
        )
        user_question = st.text_input("Ask your campus AI assistant anything:")

        if st.button("Ask AI") and user_question.strip():
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question.strip()}
                ]
                response = ollama.chat(model="llama3", messages=messages)
                st.text_area("AI Response", value=response['message']['content'], height=200)
            except Exception as e:
                st.error(f"AI assistant error: {e}")

    elif menu == "⚙️ Account Settings":
        st.header("⚙️ Account Settings & Security")
        st.info(f"College: {college_name}")
        st.info(f"Wallet: {wallet_address}")
        st.info(f"Data Source: {'Blockchain/Web3' if not use_csv else 'CSV fallback'}")

    elif menu == "ℹ️ About / Help":
        st.header("ℹ️ About & Help")
        st.markdown("""
        This hybrid student portal uses blockchain as the primary source of truth with CSV fallback.
        Redeeming points require blockchain transaction for security.
        The Ollama AI assistant provides campus info & help.
        """)

if __name__ == "__main__":
    main()
