import streamlit as st
import json
import pandas as pd
from web3 import Web3
import os

# === CONFIGURATION ===
NODE_URL = "http://127.0.0.1:8545"  # Your local blockchain node URL or RPC endpoint
CONTRACT_ADDRESS = "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"  # Replace with your deployed contract address

# Replace this with your actual Contract ABI JSON string copied from Remix or Hardhat
CONTRACT_ABI = json.loads("""
[
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"}
        ],
        "name": "registerCollege",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"},
            {"internalType": "string", "name": "_deptName", "type": "string"},
            {"internalType": "address", "name": "_deptAdmin", "type": "address"}
        ],
        "name": "addDepartment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"},
            {"internalType": "string", "name": "_deptName", "type": "string"},
            {"internalType": "address", "name": "_wallet", "type": "address"},
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "string", "name": "_role", "type": "string"}
        ],
        "name": "addFaculty",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"},
            {"internalType": "string", "name": "_department", "type": "string"},
            {"internalType": "address", "name": "_wallet", "type": "address"},
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "string", "name": "_rollNo", "type": "string"},
            {"internalType": "uint8", "name": "_year", "type": "uint8"},
            {"internalType": "string", "name": "_section", "type": "string"},
            {"internalType": "string", "name": "_email", "type": "string"}
        ],
        "name": "addStudent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"},
            {"internalType": "address", "name": "_student", "type": "address"},
            {"internalType": "string", "name": "_subject", "type": "string"},
            {"internalType": "uint8", "name": "_marks", "type": "uint8"}
        ],
        "name": "addMarks",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_collegeName", "type": "string"},
            {"internalType": "address", "name": "_student", "type": "address"}
        ],
        "name": "getMarks",
        "outputs": [
            {"internalType": "string[]", "name": "", "type": "string[]"},
            {"internalType": "uint8[]", "name": "", "type": "uint8[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
""")

# === CSV FILE PATHS ===
DEPARTMENTS_CSV = "departments.csv"
FACULTY_CSV = "faculty.csv"
STUDENTS_CSV = "students.csv"
GRADES_CSV = "grades.csv"

# === Helper functions for CSV ===
def load_csv(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
    return pd.read_csv(file_path)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# Load CSV at app start
departments_df = load_csv(DEPARTMENTS_CSV, ['collegeName', 'deptName', 'deptAdmin'])
faculty_df = load_csv(FACULTY_CSV, ['collegeName', 'deptName', 'wallet', 'name', 'role'])
students_df = load_csv(STUDENTS_CSV, ['collegeName', 'department', 'wallet', 'name', 'rollNo', 'year', 'section', 'email'])
grades_df = load_csv(GRADES_CSV, ['collegeName', 'studentWallet', 'subject', 'marks'])

# --- Web3 helpers ---
def connect_blockchain():
    w3 = Web3(Web3.HTTPProvider(NODE_URL))
    if not w3.is_connected():
        return None, None
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    return w3, contract

def get_marks_web3(contract, college, student_wallet):
    try:
        subjects, marks = contract.functions.getMarks(college, student_wallet).call()
        return subjects, marks
    except Exception:
        return [], []

# === CSV fallback fetch functions ===
def get_departments_csv(college_name):
    df = departments_df[departments_df['collegeName']==college_name]
    return df['deptName'].tolist()

def get_faculty_csv(college_name, dept_name):
    df = faculty_df[(faculty_df['collegeName']==college_name) & (faculty_df['deptName']==dept_name)]
    return df[['wallet','name','role']].to_dict('records')

def get_student_csv(college_name, student_wallet):
    df = students_df[(students_df['collegeName']==college_name) & (students_df['wallet'].str.lower() == student_wallet.lower())]
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def get_marks_csv(college_name, student_wallet):
    df = grades_df[(grades_df['collegeName']==college_name) & (grades_df['studentWallet'].str.lower() == student_wallet.lower())]
    if df.empty:
        return [], []
    subjects = df['subject'].tolist()
    marks = df['marks'].astype(int).tolist()
    return subjects, marks

# --- Streamlit app ---
def main():
    st.set_page_config(page_title="🎓 College Admin Portal Hybrid", layout="wide")
    st.title("🎓 Decentralized College Admin Portal (Hybrid Web3 + CSV Fallback)")

    use_web3 = st.sidebar.checkbox("Use Blockchain (Web3)", value=True)

    menu = st.sidebar.radio("Navigation", [
        "🏠 Home",
        "🎓 Register College",
        "🏢 Add Department",
        "👩‍🏫 Add Faculty/Staff",
        "🧑‍🎓 Add Students",
        "📝 Add/View Grades"
    ])

    if menu == "🏠 Home":
        st.markdown("""
        ## Features:
        - Register colleges, departments, faculty, and students on-chain.
        - Pay ETH salary to faculty at registration.
        - Add and view marks (grades) for students.
        - CSV fallback for offline/local testing.
        """)

    elif menu == "🎓 Register College":
        st.info("Register College is blockchain-only in this hybrid app.")

    elif menu == "🏢 Add Department":
        st.header("Add Department")
        college_name = st.text_input("College Name")
        dept_name = st.text_input("Department Name")
        dept_admin = st.text_input("Department Admin ETH Address")
        admin_priv = st.text_input("Admin Private Key", type="password")

        if st.button("Add Department"):
            if use_web3:
                try:
                    w3, contract = connect_blockchain()
                    if w3 is None:
                        st.error("Blockchain node connection failed.")
                        return
                    priv = admin_priv.strip()
                    if not priv.startswith("0x"):
                        priv = "0x" + priv
                    admin = w3.eth.account.from_key(priv)
                    dept_admin_addr = Web3.to_checksum_address(dept_admin)
                    nonce = w3.eth.get_transaction_count(admin.address)
                    tx = contract.functions.addDepartment(college_name, dept_name, dept_admin_addr).build_transaction({
                        "from": admin.address,
                        "nonce": nonce,
                        "gas": 350000,
                        "gasPrice": w3.to_wei("2", "gwei"),
                    })
                    signed = w3.eth.account.sign_transaction(tx, priv)
                    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                    st.success(f"Department added! Tx Hash: {w3.to_hex(tx_hash)}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                # CSV fallback add department
                global departments_df
                if ((departments_df['collegeName']==college_name) & (departments_df['deptName']==dept_name)).any():
                    st.warning("Department already exists in CSV database.")
                else:
                    new_row = pd.DataFrame([{
                        'collegeName': college_name,
                        'deptName': dept_name,
                        'deptAdmin': dept_admin
                    }])
                    departments_df = pd.concat([departments_df, new_row], ignore_index=True)
                    save_csv(departments_df, DEPARTMENTS_CSV)
                    st.success("Department added to CSV database.")

    elif menu == "👩‍🏫 Add Faculty/Staff":
        st.header("Add Faculty/Staff")
        college_name = st.text_input("College Name")
        dept_name = st.text_input("Department Name")
        faculty_name = st.text_input("Faculty Name")
        faculty_eth = st.text_input("Faculty ETH Address")
        role = st.selectbox("Role", ["Professor", "Asst Prof", "Lab Assistant", "Office", "Other"])
        admin_priv = st.text_input("Admin Private Key", type="password")

        if st.button("Add Faculty"):
            if use_web3:
                try:
                    w3, contract = connect_blockchain()
                    if w3 is None:
                        st.error("Blockchain node connection failed.")
                        return
                    priv = admin_priv.strip()
                    if not priv.startswith("0x"):
                        priv = "0x" + priv
                    admin = w3.eth.account.from_key(priv)
                    faculty_addr = Web3.to_checksum_address(faculty_eth)
                    nonce = w3.eth.get_transaction_count(admin.address)
                    tx = contract.functions.addFaculty(
                        college_name, dept_name, faculty_addr, faculty_name, role
                    ).build_transaction({
                        "from": admin.address,
                        "nonce": nonce,
                        "gas": 300000,
                        "gasPrice": w3.to_wei("2", "gwei"),
                    })
                    signed = w3.eth.account.sign_transaction(tx, priv)
                    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                    st.success(f"Faculty added! Tx Hash: {w3.to_hex(tx_hash)}")
                except Exception as e:
                    st.error(f"Transaction failed: {e}")
            else:
                # CSV fallback add faculty
                global faculty_df
                if ((faculty_df['collegeName']==college_name) & (faculty_df['deptName']==dept_name) & 
                    (faculty_df['wallet'].str.lower()==faculty_eth.lower())).any():
                    st.warning("Faculty already exists in CSV database.")
                else:
                    new_row = pd.DataFrame([{
                        'collegeName': college_name,
                        'deptName': dept_name,
                        'wallet': faculty_eth,
                        'name': faculty_name,
                        'role': role
                    }])
                    faculty_df = pd.concat([faculty_df, new_row], ignore_index=True)
                    save_csv(faculty_df, FACULTY_CSV)
                    st.success("Faculty added to CSV database.")

    elif menu == "🧑‍🎓 Add Students":
        st.header("Add Students")
        college_name = st.text_input("College Name")
        dept = st.text_input("Department")
        name = st.text_input("Student Name")
        roll = st.text_input("Roll No")
        year = st.selectbox("Year", [1, 2, 3, 4])
        section = st.text_input("Section")
        email = st.text_input("Email")
        student_eth = st.text_input("Student ETH Address")
        admin_priv = st.text_input("Admin Private Key", type="password")

        if st.button("Add Student"):
            if use_web3:
                try:
                    w3, contract = connect_blockchain()
                    if w3 is None:
                        st.error("Blockchain node connection failed.")
                        return
                    priv = admin_priv.strip()
                    if not priv.startswith("0x"):
                        priv = "0x" + priv
                    admin = w3.eth.account.from_key(priv)
                    student_addr = Web3.to_checksum_address(student_eth)
                    nonce = w3.eth.get_transaction_count(admin.address)
                    tx = contract.functions.addStudent(
                        college_name, dept, student_addr, name, roll, year, section, email
                    ).build_transaction({
                        "from": admin.address,
                        "nonce": nonce,
                        "gas": 300000,
                        "gasPrice": w3.to_wei("2", "gwei"),
                    })
                    signed = w3.eth.account.sign_transaction(tx, priv)
                    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                    st.success(f"Student added! Tx Hash: {w3.to_hex(tx_hash)}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                # CSV fallback add student
                global students_df
                if ((students_df['collegeName']==college_name) & (students_df['wallet'].str.lower()==student_eth.lower())).any():
                    st.warning("Student already exists in CSV database.")
                else:
                    new_row = pd.DataFrame([{
                        'collegeName': college_name,
                        'department': dept,
                        'wallet': student_eth,
                        'name': name,
                        'rollNo': roll,
                        'year': year,
                        'section': section,
                        'email': email
                    }])
                    students_df = pd.concat([students_df, new_row], ignore_index=True)
                    save_csv(students_df, STUDENTS_CSV)
                    st.success("Student added to CSV database.")

    elif menu == "📝 Add/View Grades":
        st.header("Add or View Student Grades")
        college_name = st.text_input("College Name", key="grade_college")
        student_eth = st.text_input("Student ETH Address", key="grade_student")

        if college_name and student_eth:
            if use_web3:
                try:
                    w3, contract = connect_blockchain()
                    if w3 is None:
                        st.error("Blockchain node connection failed.")
                        return
                    student_addr = Web3.to_checksum_address(student_eth)
                    action = st.radio("Action", ["Add Marks", "View Marks"])

                    if action == "Add Marks":
                        subject = st.text_input("Subject Name")
                        marks = st.number_input("Marks (0-100)", min_value=0, max_value=100, step=1)
                        admin_priv = st.text_input("Admin Private Key", type="password")

                        if st.button("Submit Marks"):
                            priv = admin_priv.strip()
                            if not priv.startswith("0x"):
                                priv = "0x" + priv
                            admin = w3.eth.account.from_key(priv)
                            nonce = w3.eth.get_transaction_count(admin.address)
                            tx = contract.functions.addMarks(
                                college_name, student_addr, subject, marks
                            ).build_transaction({
                                "from": admin.address,
                                "nonce": nonce,
                                "gas": 200000,
                                "gasPrice": w3.to_wei("2", "gwei"),
                            })
                            signed = w3.eth.account.sign_transaction(tx, priv)
                            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                            st.success(f"Marks added successfully! Tx Hash: {w3.to_hex(tx_hash)}")

                    elif action == "View Marks":
                        subjects, marks_list = contract.functions.getMarks(college_name, student_addr).call()
                        if len(subjects) == 0:
                            st.info("No marks found for this student.")
                        else:
                            df = pd.DataFrame({"Subject": subjects, "Marks": marks_list})
                            st.table(df)
                except Exception as e:
                    st.error(f"Failed or invalid input: {e}")
            else:
                # CSV fallback
                subjects, marks = get_marks_csv(college_name, student_eth)
                action = st.radio("Action", ["Add Marks (CSV Not Supported)", "View Marks"])
                if action == "View Marks":
                    if len(subjects)==0:
                        st.info("No marks found for this student in CSV.")
                    else:
                        df = pd.DataFrame({"Subject": subjects, "Marks": marks})
                        st.table(df)
                else:
                    st.warning("Adding marks is only supported on blockchain in this app.")


if __name__ == "__main__":
    main()
