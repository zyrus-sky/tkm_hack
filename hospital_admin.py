import streamlit as st
import json
import pandas as pd
from web3 import Web3
from datetime import datetime
import os

# === CONFIG ===
NODE_URL = "http://127.0.0.1:8545"  # Your Ethereum node (Ganache, Hardhat)
CONTRACT_ADDRESS = "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853"  # Replace with your deployed contract address

# Paste your contract ABI JSON string copied from Remix or Hardhat (your own full ABI)
CONTRACT_ABI = json.loads("""
[
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "staffEth",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "staffName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "staffRole",
				"type": "string"
			}
		],
		"name": "addStaff",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "staff",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "student",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "cid",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "points",
				"type": "uint256"
			}
		],
		"name": "HealthReportSubmitted",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "admin",
				"type": "address"
			}
		],
		"name": "HospitalRegistered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			}
		],
		"name": "registerHospital",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "staffAddr",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "newSalary",
				"type": "uint256"
			}
		],
		"name": "SalaryUpdated",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "staffEth",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "salaryInWei",
				"type": "uint256"
			}
		],
		"name": "setSalary",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "staffAddr",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "staffName",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "role",
				"type": "string"
			}
		],
		"name": "StaffAdded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "student",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "cid",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "points",
				"type": "uint256"
			},
			{
				"internalType": "bytes32",
				"name": "summaryHash",
				"type": "bytes32"
			}
		],
		"name": "submitHealthReport",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			}
		],
		"name": "getAllReports",
		"outputs": [
			{
				"components": [
					{
						"internalType": "address",
						"name": "student",
						"type": "address"
					},
					{
						"internalType": "string",
						"name": "cid",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "points",
						"type": "uint256"
					},
					{
						"internalType": "bytes32",
						"name": "summaryHash",
						"type": "bytes32"
					}
				],
				"internalType": "struct HealthPortal.HealthReport[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "staffEth",
				"type": "address"
			}
		],
		"name": "getSalary",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			}
		],
		"name": "getStaffList",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "staffAddresses",
				"type": "address[]"
			},
			{
				"internalType": "string[]",
				"name": "names",
				"type": "string[]"
			},
			{
				"internalType": "string[]",
				"name": "rolesArr",
				"type": "string[]"
			},
			{
				"internalType": "uint256[]",
				"name": "salaries",
				"type": "uint256[]"
			},
			{
				"internalType": "bool[]",
				"name": "activeFlags",
				"type": "bool[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hospitalName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "isAdmin",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "roles",
		"outputs": [
			{
				"internalType": "enum HealthPortal.Role",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
""")

# === CSV FILE PATHS ===
STAFF_CSV = 'staff.csv'
SALARY_CSV = 'salary.csv'
REPORTS_CSV = 'reports.csv'


# === Helper Functions for CSV Handling ===
def load_csv_or_create(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
    return pd.read_csv(file_path)


def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


# Load CSVs
staff_df = load_csv_or_create(STAFF_CSV, ['hospitalName', 'staffAddress', 'staffName', 'staffRole'])
salary_df = load_csv_or_create(SALARY_CSV, ['hospitalName', 'staffAddress', 'salaryWei'])
reports_df = load_csv_or_create(REPORTS_CSV, ['hospitalName', 'studentAddress', 'cid', 'timestamp', 'points', 'summaryHash'])


# === Web3 helpers ===
def get_contract():
    w3 = Web3(Web3.HTTPProvider(NODE_URL))
    if not w3.is_connected():
        return None, None
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    return w3, contract


def safe_address(addr):
    try:
        return Web3.to_checksum_address(addr)
    except Exception:
        return None


# Fetch Staff from blockchain or CSV fallback
def get_staff_list_blockchain(contract, hospital_name):
    try:
        results = contract.functions.getStaffList(hospital_name).call()
        # results is a tuple of arrays: (addresses[], names[], roles[], salaries[], activeFlags[])
        staff_list = []
        for i in range(len(results[0])):
            staff_list.append({
                'staffAddress': results[0][i],
                'staffName': results[1][i],
                'staffRole': results[2][i],
                'salaryWei': results[3][i],
                'active': results[4][i],
            })
        return staff_list
    except Exception:
        return None


def get_staff_list_csv(hospital_name):
    df = staff_df[staff_df['hospitalName'] == hospital_name]
    sal_df = salary_df[salary_df['hospitalName'] == hospital_name].set_index('staffAddress')
    staff_list = []
    for _, row in df.iterrows():
        sal = sal_df['salaryWei'].get(row['staffAddress'], None)
        staff_list.append({
            'staffAddress': row['staffAddress'],
            'staffName': row['staffName'],
            'staffRole': row['staffRole'],
            'salaryWei': int(sal) if sal is not None else 0,
            'active': True,  # No active column in CSV, assume True
        })
    return staff_list


# Fetch reports blockchain or CSV fallback
def get_reports_blockchain(contract, hospital_name):
    try:
        reports = contract.functions.getAllReports(hospital_name).call()
        parsed = []
        for r in reports:
            parsed.append({
                "studentAddress": r[0],
                "cid": r[1],
                "timestamp": r[2],
                "points": r[3],
                "summaryHash": r[4].hex() if isinstance(r[4], bytes) else r[4]
            })
        return parsed
    except Exception:
        return None


def get_reports_csv(hospital_name):
    df = reports_df[reports_df['hospitalName'] == hospital_name]
    parsed = []
    for _, row in df.iterrows():
        parsed.append({
            "studentAddress": row['studentAddress'],
            "cid": row['cid'],
            "timestamp": int(row['timestamp']),
            "points": int(row['points']),
            "summaryHash": row['summaryHash']
        })
    return parsed


# --- Build and send blockchain transaction helper ---
def build_sign_send_tx(w3, priv_key, tx_function, gas=350000, gas_price_gwei=2):
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


# === Streamlit app ===
def main():
    st.set_page_config(page_title="🏥 Hybrid Hospital Portal", layout="wide")

    use_blockchain = st.sidebar.checkbox("Use Blockchain (Web3)", value=True)
    hospital_name = st.sidebar.text_input("Hospital Name")

    if not hospital_name:
        st.warning("Please enter Hospital Name in sidebar")
        return

    menu = st.sidebar.radio("Mode",
                           ["🏠 Home", "👨‍⚕️ Register Hospital", "👩‍💼 Add Staff", "💳 Set Staff Salary", "🗂 Staff List",
                            "📄 Upload Health Report", "📑 All Health Reports"])

    if use_blockchain:
        w3, contract = get_contract()
        if w3 is None or contract is None:
            st.error("Could not connect to blockchain node. Falling back to CSV mode.")
            use_blockchain = False

    if menu == "🏠 Home":
        st.header("🏥 Welcome to the Hybrid Hospital Portal")
        st.markdown("""
        - Use Blockchain as source of truth if available
        - Fallback to CSV files for off-chain data storage
        - Admin actions require private key for blockchain transactions
        """)

    elif menu == "👨‍⚕️ Register Hospital":
        st.header("Register Hospital")
        with st.form("register_hospital"):
            hospital_input = st.text_input("Hospital Name", value=hospital_name)
            priv = st.text_input("Admin Private Key (0x...) for signing", type="password")
            submit = st.form_submit_button("Register Hospital")

            if submit:
                if not hospital_input or not priv:
                    st.error("Hospital name and private key are required.")
                else:
                    if use_blockchain:
                        try:
                            tx_hash = build_sign_send_tx(
                                w3, priv,
                                contract.functions.registerHospital(hospital_input),
                                gas=350000)
                            st.success(f"Hospital registered! Tx hash: {tx_hash}")
                        except Exception as e:
                            st.error(f"Transaction failed: {e}")
                    else:
                        st.warning(
                            "Register Hospital feature requires Blockchain mode. CSV mode does not support this.")

    elif menu == "👩‍💼 Add Staff":
        st.header("Add Staff")
        with st.form("add_staff"):
            staff_eth_str = st.text_input("Staff Ethereum Address")
            staff_name = st.text_input("Staff Name")
            staff_role = st.selectbox("Staff Role",
                                      ["Radiologist", "Gynecologist", "ENT", "Pediatrician", "Pathologist", "General Physician",
                                       "Nurse", "Admin", "Others"])
            priv = st.text_input("Admin Private Key (0x...) for signing", type="password")
            submit = st.form_submit_button("Add Staff")

            if submit:
                if not staff_eth_str or not staff_name or not staff_role or not priv:
                    st.error("All fields including private key are required.")
                else:
                    staff_eth = safe_address(staff_eth_str)
                    if staff_eth is None:
                        st.error("Invalid Ethereum address for staff.")
                    else:
                        if use_blockchain:
                            try:
                                tx_hash = build_sign_send_tx(
                                    w3, priv,
                                    contract.functions.addStaff(hospital_name, staff_eth, staff_name, staff_role),
                                    gas=350000)
                                st.success(f"Staff added! Tx hash: {tx_hash}")
                            except Exception as e:
                                st.error(f"Transaction failed: {e}")
                        else:
                            # CSV mode: add staff to CSV
                            global staff_df
                            if ((staff_df['hospitalName'] == hospital_name) & (staff_df['staffAddress'].str.lower() == staff_eth.lower())).any():
                                st.warning("Staff already exists in CSV data.")
                            else:
                                new_row = pd.DataFrame([{
                                    'hospitalName': hospital_name,
                                    'staffAddress': staff_eth,
                                    'staffName': staff_name,
                                    'staffRole': staff_role
                                }])
                                staff_df = pd.concat([staff_df, new_row], ignore_index=True)
                                save_csv(staff_df, STAFF_CSV)
                                st.success("Staff added to CSV data.")

    elif menu == "💳 Set Staff Salary":
        st.header("Set Staff Salary")
        with st.form("set_salary"):
            staff_eth_str = st.text_input("Staff Ethereum Address")
            salary_eth = st.number_input("Salary in ETH (per month)", min_value=0.0, step=0.01)
            priv = st.text_input("Admin Private Key (0x...) for signing", type="password")
            submit = st.form_submit_button("Set Salary")

            if submit:
                if not staff_eth_str or salary_eth is None or not priv:
                    st.error("All fields including private key are required.")
                else:
                    staff_eth = safe_address(staff_eth_str)
                    if staff_eth is None:
                        st.error("Invalid Ethereum address for staff.")
                    else:
                        salary_wei = int(salary_eth * 1e18)
                        if use_blockchain:
                            try:
                                tx_hash = build_sign_send_tx(
                                    w3, priv,
                                    contract.functions.setSalary(hospital_name, staff_eth, salary_wei),
                                    gas=250000)
                                st.success(f"Salary set! Tx hash: {tx_hash}")
                            except Exception as e:
                                st.error(f"Transaction failed: {e}")
                        else:
                            global salary_df
                            condition = (salary_df['hospitalName'] == hospital_name) & (
                                    salary_df['staffAddress'].str.lower() == staff_eth.lower())
                            if condition.any():
                                salary_df.loc[condition, 'salaryWei'] = salary_wei
                            else:
                                new_row = pd.DataFrame([{
                                    'hospitalName': hospital_name,
                                    'staffAddress': staff_eth,
                                    'salaryWei': salary_wei
                                }])
                                salary_df = pd.concat([salary_df, new_row], ignore_index=True)
                            save_csv(salary_df, SALARY_CSV)
                            st.success("Salary updated in CSV data.")

    elif menu == "🗂 Staff List":
        st.header("Staff List")
        if use_blockchain:
            if hospital_name:
                staff_list = get_staff_list_blockchain(contract, hospital_name)
                if staff_list is None:
                    st.error("Failed to fetch staff list from blockchain.")
                elif len(staff_list) == 0:
                    st.info("No staff found.")
                else:
                    df = pd.DataFrame(staff_list)
                    df['Salary (ETH)'] = df['salaryWei'].apply(lambda x: Web3.from_wei(x, "ether"))
                    st.dataframe(df[['staffAddress', 'staffName', 'staffRole', 'Salary (ETH)', 'active']].rename(
                        columns={'staffAddress': 'Address', 'staffName': 'Name', 'staffRole': 'Role', 'active': 'Active'}))
        else:
            if hospital_name:
                staff_list = get_staff_list_csv(hospital_name)
                if len(staff_list) == 0:
                    st.info("No staff found in CSV data.")
                else:
                    df = pd.DataFrame(staff_list)
                    df['Salary (ETH)'] = df['salaryWei'].apply(lambda x: x / 1e18)
                    st.dataframe(df[['staffAddress', 'staffName', 'staffRole', 'Salary (ETH)', 'active']].rename(
                        columns={'staffAddress': 'Address', 'staffName': 'Name', 'staffRole': 'Role', 'active': 'Active'}))
            else:
                st.info("Enter hospital name to show staff list.")

    elif menu == "📄 Upload Health Report":
        st.header("Upload Health Report")
        with st.form("upload_report"):
            staff_priv = st.text_input("Staff Private Key (0x...) (for signing)", type="password")
            student_addr_input = st.text_input("Student Ethereum Address")
            ipfs_cid = st.text_input("IPFS CID")
            points = st.number_input("Karma Points", min_value=0, value=10)
            summary_hash = st.text_input("AI Summary Hash (bytes32)", max_chars=66)
            submit = st.form_submit_button("Submit Health Report")

            if submit:
                if not staff_priv or not student_addr_input or not ipfs_cid or not summary_hash:
                    st.error("All fields except points are required.")
                else:
                    student_eth = safe_address(student_addr_input)
                    if student_eth is None:
                        st.error("Invalid Ethereum address for student.")
                    else:
                        if use_blockchain:
                            try:
                                tx_hash = build_sign_send_tx(
                                    w3, staff_priv,
                                    contract.functions.submitHealthReport(hospital_name, student_eth, ipfs_cid, points,
                                                                         summary_hash),
                                    gas=450000)
                                st.success(f"Health report submitted! Tx hash: {tx_hash}")
                            except Exception as e:
                                st.error(f"Transaction failed: {e}")
                        else:
                            global reports_df
                            new_row = pd.DataFrame([{
                                'hospitalName': hospital_name,
                                'studentAddress': student_eth,
                                'cid': ipfs_cid,
                                'timestamp': int(datetime.now().timestamp()),
                                'points': points,
                                'summaryHash': summary_hash
                            }])
                            reports_df = pd.concat([reports_df, new_row], ignore_index=True)
                            save_csv(reports_df, REPORTS_CSV)
                            st.success("Health report added to CSV data.")

    elif menu == "📑 All Health Reports":
        st.header("All Health Reports")
        if hospital_name:
            if use_blockchain:
                reports = get_reports_blockchain(contract, hospital_name)
                if reports is None:
                    st.error("Failed to fetch health reports from blockchain.")
                elif len(reports) == 0:
                    st.info("No health reports found.")
                else:
                    df = pd.DataFrame(reports)
                    df['Timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
                    st.dataframe(df[['studentAddress', 'cid', 'Timestamp', 'points', 'summaryHash']].rename(
                        columns={'studentAddress': 'Student Address', 'cid': 'IPFS CID', 'points': 'Points',
                                 'summaryHash': 'Summary Hash'}))
            else:
                reports = get_reports_csv(hospital_name)
                if len(reports) == 0:
                    st.info("No health reports found in CSV data.")
                else:
                    df = pd.DataFrame(reports)
                    df['Timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
                    st.dataframe(df[['studentAddress', 'cid', 'Timestamp', 'points', 'summaryHash']].rename(
                        columns={'studentAddress': 'Student Address', 'cid': 'IPFS CID', 'points': 'Points',
                                 'summaryHash': 'Summary Hash'}))
        else:
            st.info("Please enter hospital name to load health reports.")


if __name__ == "__main__":
    main()
