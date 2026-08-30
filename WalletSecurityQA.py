import unittest
import threading

from DigitalWallet import DigitalWallet


class WalletSecurityQA(unittest.TestCase):

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

    # 1. NORMAL TRANSACTION
    def test_normal_transaction(self):
        result, message = self.wallet.deposit("A101", 1000)

        self.assertTrue(result)
        self.assertEqual(
            self.wallet.get_balance("A101"),
            16000
        )

    # 2. INSUFFICIENT BALANCE
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

    # 3. DAILY LIMIT
    def test_daily_limit(self):

        result, message = self.wallet.withdraw(
            "A101",
            20001,
            "1234"
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Daily transaction limit exceeded"
        )

    # 4. MULTIPLE FAILED PINS
    def test_multiple_failed_pins(self):

        self.wallet.verify_pin("A101", "1111")
        self.wallet.verify_pin("A101", "2222")
        self.wallet.verify_pin("A101", "3333")

        self.assertEqual(
            self.wallet.accounts["A101"]["failed_pins"],
            3
        )

    # 5. SUSPICIOUS TRANSACTION
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

    # 6. DUPLICATE TRANSACTION
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

    # 7. NEGATIVE AMOUNT
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

    # 8. CONCURRENT TRANSACTIONS
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

        # Initial balance = 15000
        # 10 withdrawals × 100 = 1000
        expected_balance = 14000

        self.assertEqual(
            self.wallet.get_balance("A101"),
            expected_balance
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
