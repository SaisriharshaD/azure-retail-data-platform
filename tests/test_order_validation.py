import unittest

from src.read_orders import validate_order


class TestOrderValidation(unittest.TestCase):
    def test_valid_order(self):
        order = {"customer_id": "CUST-001", "order_amount": "200.00"}

        self.assertEqual(validate_order(order), [])

    def test_missing_customer_and_negative_amount(self):
        order = {"customer_id": "", "order_amount": "-25.00"}

        self.assertEqual(
            validate_order(order),
            [
                "Missing customer ID",
                "Order amount must be greater than zero",
            ],
        )

    def test_invalid_amount(self):
        order = {"customer_id": "CUST-004", "order_amount": "abc"}

        self.assertEqual(
            validate_order(order),
            ["Invalid order amount"],
        )


if __name__ == "__main__":
    unittest.main()