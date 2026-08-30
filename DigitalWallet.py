import threading
from datetime import datetime, timedelta


class DigitalWallet:
    def __init__(self):
        self.accounts = {}
        self.lock = threading.Lock()

        # Fraud detection settings
        self.large_transaction_limit = 10000
        self.daily_transaction_limit = 20000

    # ---------------- ACCOUNT CREATION ----------------
    def create_account(self, account_id, name, pin, initial_balance=0):
        if initial_balance < 0:
            return False, "Initial balance cannot be negative"

        if account_id in self.accounts:
            return False, "Account already exists"

        self.accounts[account_id] = {
            "name": name,
            "pin": str(pin),
            "balance": initial_balance,
            "transactions": [],
            "failed_pins": 0
        }

        return True, "Account created successfully"

    # ---------------- PIN VERIFICATION ----------------
    def verify_pin(self, account_id, pin):
        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]

        if account["pin"] == str(pin):
            account["failed_pins"] = 0
            return True

        account["failed_pins"] += 1
        return False

    # ---------------- DEPOSIT ----------------
    def deposit(self, account_id, amount):
        if amount <= 0:
            return False, "Amount must be positive"

        with self.lock:
            if account_id not in self.accounts:
                return False, "Account not found"

            account = self.accounts[account_id]
            account["balance"] += amount

            self._record_transaction(
                account_id,
                "DEPOSIT",
                amount,
                True
            )

            return True, "Deposit successful"

    # ---------------- WITHDRAWAL ----------------
    def withdraw(self, account_id, amount, pin):
        if amount <= 0:
            return False, "Amount must be positive"

        with self.lock:
            if account_id not in self.accounts:
                return False, "Account not found"

            if not self.verify_pin(account_id, pin):
                return False, "Invalid PIN"

            account = self.accounts[account_id]

            if account["balance"] < amount:
                return False, "Insufficient balance"

            if self.daily_limit_exceeded(account_id, amount):
                return False, "Daily transaction limit exceeded"

            suspicious = self.is_suspicious(account_id, amount)

            account["balance"] -= amount

            self._record_transaction(
                account_id,
                "WITHDRAW",
                amount,
                True,
                suspicious
            )

            if suspicious:
                return True, "Withdrawal successful - SUSPICIOUS TRANSACTION FLAGGED"

            return True, "Withdrawal successful"

    # ---------------- MONEY TRANSFER ----------------
    def transfer(self, sender_id, receiver_id, amount, pin, transaction_id=None):
        if amount <= 0:
            return False, "Amount must be positive"

        with self.lock:
            if sender_id not in self.accounts:
                return False, "Sender account not found"

            if receiver_id not in self.accounts:
                return False, "Receiver account not found"

            if sender_id == receiver_id:
                return False, "Cannot transfer to same account"

            if transaction_id:
                if self.transaction_exists(transaction_id):
                    return False, "Duplicate transaction"

            if not self.verify_pin(sender_id, pin):
                return False, "Invalid PIN"

            sender = self.accounts[sender_id]
            receiver = self.accounts[receiver_id]

            if sender["balance"] < amount:
                return False, "Insufficient balance"

            if self.daily_limit_exceeded(sender_id, amount):
                return False, "Daily transaction limit exceeded"

            suspicious = self.is_suspicious(sender_id, amount)

            sender["balance"] -= amount
            receiver["balance"] += amount

            self._record_transaction(
                sender_id,
                "TRANSFER OUT",
                amount,
                True,
                suspicious,
                transaction_id
            )

            self._record_transaction(
                receiver_id,
                "TRANSFER IN",
                amount,
                True,
                False,
                transaction_id
            )

            if suspicious:
                return True, "Transfer successful - SUSPICIOUS TRANSACTION FLAGGED"

            return True, "Transfer successful"

    # ---------------- TRANSACTION HISTORY ----------------
    def transaction_history(self, account_id):
        if account_id not in self.accounts:
            return []

        return self.accounts[account_id]["transactions"]

    # ---------------- BALANCE VERIFICATION ----------------
    def get_balance(self, account_id):
        if account_id not in self.accounts:
            return None

        return self.accounts[account_id]["balance"]

    # ---------------- DAILY LIMIT ----------------
    def daily_limit_exceeded(self, account_id, amount):
        account = self.accounts[account_id]

        today = datetime.now().date()

        total = 0

        for transaction in account["transactions"]:
            if transaction["success"]:
                if transaction["type"] in ["WITHDRAW", "TRANSFER OUT"]:
                    if transaction["time"].date() == today:
                        total += transaction["amount"]

        return total + amount > self.daily_transaction_limit

    # ---------------- FRAUD DETECTION ----------------
    def is_suspicious(self, account_id, amount):
        account = self.accounts[account_id]

        now = datetime.now()

        # Rule 1: More than 5 transactions in 10 minutes
        recent_transactions = 0

        for transaction in account["transactions"]:
            if transaction["success"]:
                if now - transaction["time"] <= timedelta(minutes=10):
                    recent_transactions += 1

        if recent_transactions >= 5:
            return True

        # Rule 2: Large transaction
        if amount > self.large_transaction_limit:
            return True

        # Rule 3: Multiple failed PIN attempts
        if account["failed_pins"] >= 3:
            return True

        # Rule 4: Unusual transaction amount
        successful_amounts = [
            t["amount"]
            for t in account["transactions"]
            if t["success"]
        ]

        if len(successful_amounts) >= 3:
            average = sum(successful_amounts) / len(successful_amounts)

            if amount > average * 5:
                return True

        return False

    # ---------------- RECORD TRANSACTION ----------------
    def _record_transaction(
        self,
        account_id,
        transaction_type,
        amount,
        success,
        suspicious=False,
        transaction_id=None
    ):
        self.accounts[account_id]["transactions"].append({
            "id": transaction_id,
            "type": transaction_type,
            "amount": amount,
            "time": datetime.now(),
            "success": success,
            "suspicious": suspicious
        })

    # ---------------- DUPLICATE CHECK ----------------
    def transaction_exists(self, transaction_id):
        for account in self.accounts.values():
            for transaction in account["transactions"]:
                if transaction["id"] == transaction_id:
                    return True

        return False


# ---------------- SIMPLE DEMO ----------------
if __name__ == "__main__":

    wallet = DigitalWallet()

    print(wallet.create_account("A101", "Mona", "1234", 15000))
    print(wallet.create_account("A102", "Karthi", "5678", 5000))

    print("\nDeposit:")
    print(wallet.deposit("A101", 2000))

    print("\nWithdrawal:")
    print(wallet.withdraw("A101", 1000, "1234"))

    print("\nTransfer:")
    print(wallet.transfer(
        "A101",
        "A102",
        2000,
        "1234",
        "TX001"
    ))

    print("\nBalance:")
    print("A101:", wallet.get_balance("A101"))
    print("A102:", wallet.get_balance("A102"))

    print("\nTransaction History:")
    for transaction in wallet.transaction_history("A101"):
        print(transaction)
      
