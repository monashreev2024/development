import unittest
import threading

from DigitalWallet import DigitalWallet


class WalletSecurityQA(unittest.TestCase):

    # ---------------- SETUP ----------------
    def setUp(self):

        self.wallet = DigitalWallet()

        self.wallet.create_account(
            "A101",
            "Mona",
            "1234",
            15000
        )

        self.wallet.create_account(
            "A102",
            "Karthi",
            "5678",
            5000
        )

    # ---------------- TEST 1 ----------------
    # Normal transaction
    def test_normal_transaction(self):

        result, message = self.wallet.deposit(
            "A101",
            1000
        )

        self.assertTrue(result)

        self.assertEqual(
            self.wallet.get_balance("A101"),
            16000
        )

    # ---------------- TEST 2 ----------------
    # Insufficient balance
    def test_insufficient_balance(self):

        result, message = self.wallet.withdraw(
            "A101",
            50000,
            "1234"
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Insufficient balance"
        )

    # ---------------- TEST 3 ----------------
    # Daily transaction limit
    def test_daily_limit(self):

        # Create account with enough balance
        self.wallet.create_account(
            "A103",
            "Daily Limit Test",
            "9999",
            30000
        )

        result, message = self.wallet.withdraw(
            "A103",
            20001,
            "9999"
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Daily transaction limit exceeded"
        )

    # ---------------- TEST 4 ----------------
    # Multiple failed PIN attempts
    def test_multiple_failed_pins(self):

        self.wallet.verify_pin(
            "A101",
            "1111"
        )

        self.wallet.verify_pin(
            "A101",
            "2222"
        )

        self.wallet.verify_pin(
            "A101",
            "3333"
        )

        self.assertEqual(
            self.wallet.accounts["A101"]["failed_pins"],
            3
        )

    # ---------------- TEST 5 ----------------
    # Suspicious transaction
    def test_suspicious_transaction(self):

        result, message = self.wallet.withdraw(
            "A101",
            12000,
            "1234"
        )

        self.assertTrue(result)

        self.assertIn(
            "SUSPICIOUS",
            message
        )

    # ---------------- TEST 6 ----------------
    # Duplicate transaction
    def test_duplicate_transaction(self):

        result1, message1 = self.wallet.transfer(
            "A101",
            "A102",
            1000,
            "1234",
            "TX100"
        )

        result2, message2 = self.wallet.transfer(
            "A101",
            "A102",
            1000,
            "1234",
            "TX100"
        )

        self.assertTrue(result1)

        self.assertFalse(result2)

        self.assertEqual(
            message2,
            "Duplicate transaction"
        )

    # ---------------- TEST 7 ----------------
    # Negative amount
    def test_negative_amount(self):

        result, message = self.wallet.deposit(
            "A101",
            -500
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Amount must be positive"
        )

    # ---------------- TEST 8 ----------------
    # Concurrent transactions
    def test_concurrent_transactions(self):

        def withdraw_money():

            self.wallet.withdraw(
                "A101",
                100,
                "1234"
            )

        threads = []

        for i in range(10):

            thread = threading.Thread(
                target=withdraw_money
            )

            threads.append(thread)

            thread.start()

        for thread in threads:
            thread.join()

        expected_balance = 14000

        self.assertEqual(
            self.wallet.get_balance("A101"),
            expected_balance
        )


# ---------------- RUN TESTS ----------------
if __name__ == "__main__":

    unittest.main(verbosity=2)
