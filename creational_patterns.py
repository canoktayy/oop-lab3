from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Type
import json


# ============================================================
# 1) FACTORY PATTERN
# ============================================================

class PaymentProcessor(ABC):
    @abstractmethod
    def validate(self, details: dict) -> bool:
        pass

    @abstractmethod
    def process(self, amount: float, details: dict) -> dict:
        pass


class CreditCardProcessor(PaymentProcessor):
    def validate(self, details: dict) -> bool:
        card_number = details.get("card_number")
        cvv = details.get("cvv")
        return bool(card_number and len(card_number) == 16 and cvv and len(cvv) == 3)

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": "Invalid credit card details"}

        fee = amount * 0.029
        total = amount + fee
        return {
            "success": True,
            "method": "credit_card",
            "amount": total,
            "fee": fee,
        }


class BankTransferProcessor(PaymentProcessor):
    def validate(self, details: dict) -> bool:
        iban = details.get("iban")
        return bool(iban and len(iban) >= 15)

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": "Invalid bank transfer details"}

        fee = 1.50
        total = amount + fee
        return {
            "success": True,
            "method": "bank_transfer",
            "amount": total,
            "fee": fee,
        }


class PayPalProcessor(PaymentProcessor):
    def validate(self, details: dict) -> bool:
        email = details.get("email")
        return bool(email and "@" in email)

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": "Invalid PayPal details"}

        fee = amount * 0.034 + 0.30
        total = amount + fee
        return {
            "success": True,
            "method": "paypal",
            "amount": total,
            "fee": fee,
        }


class PaymentFactory:
    _processors: Dict[str, Type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        processor_class = self._processors.get(payment_type)
        if processor_class is None:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return processor_class()


# ============================================================
# 2) BUILDER PATTERN
# ============================================================

@dataclass
class Employee:
    first_name: str
    last_name: str
    email: str
    department: str
    position: str
    salary: float
    start_date: str
    manager_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    has_parking: bool = False
    has_laptop: bool = False
    has_vpn_access: bool = False
    has_admin_rights: bool = False
    office_location: Optional[str] = None
    contract_type: str = "permanent"


class EmployeeBuilder:
    def __init__(self) -> None:
        self._employee_data: Dict[str, Any] = {
            "first_name": None,
            "last_name": None,
            "email": None,
            "department": None,
            "position": None,
            "salary": None,
            "start_date": None,
            "manager_id": None,
            "phone": None,
            "address": None,
            "emergency_contact": None,
            "has_parking": False,
            "has_laptop": False,
            "has_vpn_access": False,
            "has_admin_rights": False,
            "office_location": None,
            "contract_type": "permanent",
        }

    def with_name(self, first_name: str, last_name: str) -> "EmployeeBuilder":
        self._employee_data["first_name"] = first_name
        self._employee_data["last_name"] = last_name
        return self

    def with_email(self, email: str) -> "EmployeeBuilder":
        self._employee_data["email"] = email
        return self

    def with_job(
        self,
        department: str,
        position: str,
        salary: float,
        start_date: str = "2024-01-01",
    ) -> "EmployeeBuilder":
        self._employee_data["department"] = department
        self._employee_data["position"] = position
        self._employee_data["salary"] = salary
        self._employee_data["start_date"] = start_date
        return self

    def with_manager(self, manager_id: int) -> "EmployeeBuilder":
        self._employee_data["manager_id"] = manager_id
        return self

    def with_contact_info(
        self,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        emergency_contact: Optional[str] = None,
    ) -> "EmployeeBuilder":
        self._employee_data["phone"] = phone
        self._employee_data["address"] = address
        self._employee_data["emergency_contact"] = emergency_contact
        return self

    def with_equipment(
        self,
        laptop: bool = False,
        parking: bool = False,
    ) -> "EmployeeBuilder":
        self._employee_data["has_laptop"] = laptop
        self._employee_data["has_parking"] = parking
        return self

    def with_access(
        self,
        vpn: bool = False,
        admin: bool = False,
    ) -> "EmployeeBuilder":
        self._employee_data["has_vpn_access"] = vpn
        self._employee_data["has_admin_rights"] = admin
        return self

    def with_office(self, office_location: str) -> "EmployeeBuilder":
        self._employee_data["office_location"] = office_location
        return self

    def with_contract_type(self, contract_type: str) -> "EmployeeBuilder":
        self._employee_data["contract_type"] = contract_type
        return self

    def _validate(self) -> None:
        if not self._employee_data["first_name"] or not self._employee_data["last_name"]:
            raise ValueError("Name is required")
        if not self._employee_data["email"] or "@" not in self._employee_data["email"]:
            raise ValueError("Valid email is required")
        if self._employee_data["salary"] is None or self._employee_data["salary"] < 0:
            raise ValueError("Salary cannot be negative")
        if not self._employee_data["department"] or not self._employee_data["position"]:
            raise ValueError("Job information is required")
        if not self._employee_data["start_date"]:
            raise ValueError("Start date is required")

    def build(self) -> Employee:
        self._validate()
        return Employee(**self._employee_data)


class DeveloperBuilder(EmployeeBuilder):
    def __init__(self, first_name: str, last_name: str, email: str) -> None:
        super().__init__()
        (
            self.with_name(first_name, last_name)
            .with_email(email)
            .with_job("Engineering", "Senior Developer", 75000, "2024-01-15")
            .with_equipment(laptop=True, parking=False)
            .with_access(vpn=True, admin=True)
            .with_office("Paris HQ")
            .with_contract_type("permanent")
        )


class InternBuilder(EmployeeBuilder):
    def __init__(self, first_name: str, last_name: str, email: str, manager_id: int) -> None:
        super().__init__()
        (
            self.with_name(first_name, last_name)
            .with_email(email)
            .with_job("Marketing", "Intern", 15000, "2024-02-01")
            .with_manager(manager_id)
            .with_equipment(laptop=True, parking=False)
            .with_access(vpn=False, admin=False)
            .with_office("Paris HQ")
            .with_contract_type("internship")
        )


# ============================================================
# 3) SINGLETON PATTERN
# ============================================================

class ConfigManager:
    _instance: Optional["ConfigManager"] = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        with open("config.json", "r", encoding="utf-8") as f:
            self._config = json.load(f)

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        return cls()

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config

        for part in keys:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value


def connect_database() -> None:
    config = ConfigManager.get_instance()
    db_host = config.get("database.host")
    db_port = config.get("database.port")
    print(f"Connecting to database at {db_host}:{db_port}")


def send_email(to: str, subject: str) -> None:
    config = ConfigManager.get_instance()
    smtp_host = config.get("email.smtp_host")
    sender = config.get("email.sender")
    print(f"Sending email to {to} with subject '{subject}' from {sender} via {smtp_host}")


def process_platform_payment(amount: float) -> None:
    config = ConfigManager.get_instance()
    api_key = config.get("payment.api_key")
    environment = config.get("payment.environment")
    print(f"Processing {amount}€ in {environment} mode with key {api_key}")


def start_application() -> None:
    config = ConfigManager.get_instance()
    app_name = config.get("app.name")
    debug = config.get("app.debug")
    print(f"Starting {app_name} (debug={debug})")


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    print("========== FACTORY PATTERN ==========")
    factory = PaymentFactory()

    cc_processor = factory.get_processor("credit_card")
    print(
        cc_processor.process(
            100.0,
            {
                "card_number": "1234567890123456",
                "expiry": "12/25",
                "cvv": "123",
            },
        )
    )

    bank_processor = factory.get_processor("bank_transfer")
    print(
        bank_processor.process(
            100.0,
            {
                "iban": "FR7630006000011234567890189",
                "bic": "BNPAFRPP",
            },
        )
    )

    paypal_processor = factory.get_processor("paypal")
    print(
        paypal_processor.process(
            100.0,
            {
                "email": "user@example.com",
            },
        )
    )

    print("\n========== BUILDER PATTERN ==========")
    employee = (
        EmployeeBuilder()
        .with_name("John", "Doe")
        .with_email("john.doe@company.com")
        .with_job("Engineering", "Senior Developer", 75000, "2024-01-15")
        .with_equipment(laptop=True, parking=False)
        .with_access(vpn=True, admin=True)
        .with_office("Paris HQ")
        .with_contract_type("permanent")
        .build()
    )
    print(asdict(employee))

    dev = DeveloperBuilder("Alice", "Martin", "alice.martin@company.com").build()
    print(asdict(dev))

    intern = InternBuilder("Jane", "Smith", "jane.smith@company.com", 42).build()
    print(asdict(intern))

    print("\n========== SINGLETON PATTERN ==========")
    # config.json dosyasının aynı klasörde olması gerekir
    start_application()
    connect_database()
    send_email("user@test.com", "Welcome")
    process_platform_payment(99.99)

    config1 = ConfigManager.get_instance()
    config2 = ConfigManager.get_instance()
    print(f"Same singleton instance? {config1 is config2}")