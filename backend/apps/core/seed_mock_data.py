"""
Seed script for ConstructOS: Populates the database with comprehensive mock data for all major models.
Run with: python manage.py runscript seed_mock_data
"""
import random
from django.utils import timezone
from backend.apps.core.factories import (
    UserFactory, AccountFactory, ContactFactory, LeadFactory, OpportunityFactory,
    PipelineStageFactory, WarehouseFactory, ProductFactory, StockItemFactory,
    EmployeeFactory, PayrollRecordFactory, InvoiceFactory, ProjectFactory,
    EquipmentFactory, SafetyInspectionFactory, TransactionFactory,
    ChatRoomFactory, RoomMembershipFactory, MessageFactory
)

def run():
    # Users
    users = [UserFactory.create_system_admin(), UserFactory.create_executive(), UserFactory.create_finance_manager(),
             UserFactory.create_hr_specialist(), UserFactory.create_sales_rep(), UserFactory.create_operations_specialist(),
             UserFactory.create_site_manager(), UserFactory.create_field_worker(), UserFactory.create_warehouse_clerk(),
             UserFactory.create_subcontractor(), UserFactory.create_client()]
    # Accounts
    accounts = [AccountFactory() for _ in range(10)]
    # Contacts
    contacts = [ContactFactory(account=random.choice(accounts)) for _ in range(20)]
    # Pipeline stages
    stages = [PipelineStageFactory() for _ in range(5)]
    # Leads
    leads = [LeadFactory(owner=random.choice(users)) for _ in range(10)]
    # Opportunities
    opportunities = [OpportunityFactory(account=random.choice(accounts), stage=random.choice(stages), owner=random.choice(users)) for _ in range(10)]
    # Warehouses
    warehouses = [WarehouseFactory() for _ in range(3)]
    # Products
    products = [ProductFactory() for _ in range(10)]
    # Stock items
    stock_items = [StockItemFactory(product=random.choice(products), warehouse=random.choice(warehouses)) for _ in range(20)]
    # Employees
    employees = [EmployeeFactory() for _ in range(10)]
    # Payroll records
    payrolls = [PayrollRecordFactory(employee=random.choice(employees)) for _ in range(10)]
    # Invoices
    invoices = [InvoiceFactory(account=random.choice(accounts)) for _ in range(10)]
    # Projects
    projects = [ProjectFactory(manager=random.choice(users), account=random.choice(accounts)) for _ in range(5)]
    # Equipment
    equipment = [EquipmentFactory(warehouse=random.choice(warehouses)) for _ in range(5)]
    # Safety inspections
    inspections = [SafetyInspectionFactory(project=random.choice(projects)) for _ in range(5)]
    # Transactions
    transactions = [TransactionFactory(project=random.choice(projects)) for _ in range(10)]
    # Chat rooms
    chat_rooms = [ChatRoomFactory() for _ in range(5)]
    # Room memberships
    memberships = [RoomMembershipFactory(room=random.choice(chat_rooms), user_id=random.choice(users).id) for _ in range(20)]
    # Messages
    messages = [MessageFactory(room=random.choice(chat_rooms), sender_id=random.choice(users).id) for _ in range(50)]
    print("Mock data seeded successfully.")
