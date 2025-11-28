"""
Seed script for ConstructOS: Populates the database with comprehensive mock data using Django factories.
Run with: python manage.py runscript seed_mock_data
"""

from backend.apps.core.factories import (
    UserFactory, AccountFactory, ContactFactory, LeadFactory, OpportunityFactory, PipelineStageFactory,
    WarehouseFactory, ProductFactory, StockItemFactory, EmployeeFactory, PayrollRecordFactory,
    InvoiceFactory, ProjectFactory, EquipmentFactory, SafetyInspectionFactory, TransactionFactory
)

from backend.apps.crm.models import Account, Contact, Lead, Opportunity, PipelineStage
from backend.apps.erp.models import Warehouse, Product, StockItem, Invoice, InvoiceLineItem, Employee, PayrollRecord
from backend.apps.construction.models import Project, Transaction, Equipment, SafetyInspection
from backend.apps.chat.models import ChatRoom, RoomMembership, Message
from backend.apps.core.models import User


def run():
    print("Seeding mock data for ConstructOS...")
    # Create Users for all roles
    roles = [
        'system_admin', 'finance_manager', 'sales_rep', 'operations_specialist',
        'site_manager', 'hr_specialist', 'warehouse_clerk', 'field_worker',
        'subcontractor', 'client', 'executive'
    ]
    users = [UserFactory(role=role) for role in roles]
    print(f"Created {len(users)} users with all roles.")

    # Create Accounts
    accounts = [AccountFactory() for _ in range(10)]
    print(f"Created {len(accounts)} accounts.")

    # Create Contacts for each Account
    contacts = []
    for account in accounts:
        for _ in range(3):
            contact = ContactFactory(account=account)
            contacts.append(contact)
    print(f"Created {len(contacts)} contacts.")

    # Create Leads
    leads = [LeadFactory() for _ in range(10)]
    print(f"Created {len(leads)} leads.")

    # Create Opportunities
    opportunities = [OpportunityFactory() for _ in range(10)]
    print(f"Created {len(opportunities)} opportunities.")

    # Create Warehouses
    warehouses = [WarehouseFactory() for _ in range(5)]
    print(f"Created {len(warehouses)} warehouses.")

    # Create Products
    products = [ProductFactory() for _ in range(10)]
    print(f"Created {len(products)} products.")

    # Create StockItems
    stock_items = [StockItemFactory(product=products[i%10], warehouse=warehouses[i%5]) for i in range(20)]
    print(f"Created {len(stock_items)} stock items.")

    # Create Employees
    employees = [EmployeeFactory() for _ in range(10)]
    print(f"Created {len(employees)} employees.")

    # Create PayrollRecords
    payroll_records = [PayrollRecordFactory(employee=employees[i%10]) for i in range(20)]
    print(f"Created {len(payroll_records)} payroll records.")

    # Create Invoices
    invoices = [InvoiceFactory(account=accounts[i%10]) for i in range(10)]
    print(f"Created {len(invoices)} invoices.")

    # Create Projects
    projects = [ProjectFactory(account=accounts[i%10], manager=users[i%11]) for i in range(10)]
    print(f"Created {len(projects)} projects.")

    # Create Equipment
    equipment = [EquipmentFactory(warehouse=warehouses[i%5]) for i in range(10)]
    print(f"Created {len(equipment)} equipment items.")

    # Create SafetyInspections
    inspections = [SafetyInspectionFactory(project=projects[i%10]) for i in range(10)]
    print(f"Created {len(inspections)} safety inspections.")

    # Create Transactions
    transactions = [TransactionFactory(project=projects[i%10]) for i in range(20)]
    print(f"Created {len(transactions)} transactions.")

    # Create ChatRooms
    chat_rooms = [ChatRoom.objects.create(name=f"Room {i}", room_type="public") for i in range(5)]
    print(f"Created {len(chat_rooms)} chat rooms.")

    # Create RoomMemberships
    memberships = []
    for i, room in enumerate(chat_rooms):
        for user in users:
            membership = RoomMembership.objects.create(room=room, user_id=user.id, user_email=user.email, user_name=user.username)
            memberships.append(membership)
    print(f"Created {len(memberships)} room memberships.")

    # Create Messages
    messages = []
    for i, room in enumerate(chat_rooms):
        for user in users:
            message = Message.objects.create(room=room, sender_id=user.id, sender_email=user.email, sender_name=user.username, message_type='text', content=f"Hello from {user.username} in {room.name}")
            messages.append(message)
    print(f"Created {len(messages)} messages.")

    print("Mock data seeding complete. All major models and relationships covered.")
