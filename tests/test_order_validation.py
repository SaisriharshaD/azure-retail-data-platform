import unittest

from src.read_orders import validate_order


class TestOrderValidation(unittest.TestCase):
    def test_valid_order(self):
        order = {
            "customer_id": "CUST-001",
            "order_amount": "200.00",
        }

        self.assertEqual(validate_order(order), [])

    def test_missing_customer_and_negative_amount(self):
        order = {
            "customer_id": "",
            "order_amount": "-25.00",
        }

        self.assertEqual(
            validate_order(order),
            [
                "Missing customer ID",
                "Order amount must be greater than zero",
            ],
        )

    def test_invalid_amount(self):
        order = {
            "customer_id": "CUST-004",
            "order_amount": "abc",
        }

        self.assertEqual(
            validate_order(order),
            ["Invalid order amount"],
        )

    def test_zero_amount(self):
        order = {
            "customer_id": "CUST-005",
            "order_amount": "0.00",
        }

        self.assertEqual(
            validate_order(order),
            ["Order amount must be greater than zero"],
        )

    def test_whitespace_customer_id(self):
        order = {
            "customer_id": "   ",
            "order_amount": "50.00",
        }

        self.assertEqual(
            validate_order(order),
            ["Missing customer ID"],
        )

    def test_non_finite_amount(self):
        for amount in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(amount=amount):
                order = {
                    "customer_id": "CUST-006",
                    "order_amount": amount,
                }

                self.assertEqual(
                    validate_order(order),
                    ["Order amount must be a finite number"],
                )


if __name__ == "__main__":
    unittest.main()