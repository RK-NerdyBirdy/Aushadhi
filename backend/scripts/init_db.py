"""
Database initialization script
Creates tables and sample data
"""

from app.database import Base, engine, SessionLocal
from app.models import *
from app.core.security import hash_password
import uuid
from datetime import datetime, timedelta


def init_db():
    """Initialize database with tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_sample_data():
    """Seed database with sample data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        from app.models.organization import Organization
        existing = db.query(Organization).first()
        if existing:
            print("✓ Sample data already exists")
            return
        
        print("Seeding sample data...")
        
        # Create organization
        org = Organization(
            organization_id="HOSP001",
            organization_name="Apollo Hospital Delhi",
            organization_type="Tertiary Hospital"
        )
        db.add(org)
        db.flush()
        
        # Create user
        user = User(
            user_id="USR001",
            organization_id="HOSP001",
            user_name="Dr. Sharma",
            user_email="admin@hospital.com",
            user_password=hash_password("password123"),
            user_role="hospital_admin",
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create medicine master data
        medicines = [
            MedicineInfo(
                organization_id="HOSP001",
                medicine_id="MED001",
                medicine_name="Paracetamol 500mg",
                medicine_price=5.00,
                cold_storage=False,
                abc_category="A",
                ved_category="V",
                salt_composition="Paracetamol",
                pack_size="100"
            ),
            MedicineInfo(
                organization_id="HOSP001",
                medicine_id="MED002",
                medicine_name="Amoxicillin 250mg",
                medicine_price=8.50,
                cold_storage=False,
                abc_category="A",
                ved_category="V",
                salt_composition="Amoxicillin Trihydrate",
                pack_size="100"
            ),
            MedicineInfo(
                organization_id="HOSP001",
                medicine_id="MED003",
                medicine_name="Metformin 500mg",
                medicine_price=3.00,
                cold_storage=False,
                abc_category="A",
                ved_category="V",
                salt_composition="Metformin HCL",
                pack_size="100"
            ),
            MedicineInfo(
                organization_id="HOSP001",
                medicine_id="MED004",
                medicine_name="Amlodipine 5mg",
                medicine_price=4.50,
                cold_storage=False,
                abc_category="A",
                ved_category="V",
                salt_composition="Amlodipine Besylate",
                pack_size="100"
            ),
            MedicineInfo(
                organization_id="HOSP001",
                medicine_id="MED005",
                medicine_name="Insulin Glargine 100IU",
                medicine_price=3000.00,
                cold_storage=True,
                abc_category="A",
                ved_category="V",
                salt_composition="Insulin Glargine",
                pack_size="10"
            ),
        ]
        
        for med in medicines:
            db.add(med)
        db.flush()
        
        # Create stock data
        stocks = [
            HospitalStock(
                organization_id="HOSP001",
                medicine_id="MED001",
                medicine_name="Paracetamol 500mg",
                medicine_quantity=3500,
                medicine_expiry=datetime.utcnow().date() + timedelta(days=365)
            ),
            HospitalStock(
                organization_id="HOSP001",
                medicine_id="MED002",
                medicine_name="Amoxicillin 250mg",
                medicine_quantity=1200,
                medicine_expiry=datetime.utcnow().date() + timedelta(days=180)
            ),
            HospitalStock(
                organization_id="HOSP001",
                medicine_id="MED003",
                medicine_name="Metformin 500mg",
                medicine_quantity=8500,
                medicine_expiry=datetime.utcnow().date() + timedelta(days=400)
            ),
            HospitalStock(
                organization_id="HOSP001",
                medicine_id="MED004",
                medicine_name="Amlodipine 5mg",
                medicine_quantity=2200,
                medicine_expiry=datetime.utcnow().date() + timedelta(days=240)
            ),
            HospitalStock(
                organization_id="HOSP001",
                medicine_id="MED005",
                medicine_name="Insulin Glargine 100IU",
                medicine_quantity=45,
                medicine_expiry=datetime.utcnow().date() + timedelta(days=90)
            ),
        ]
        
        for stock in stocks:
            db.add(stock)
        db.flush()
        
        # Create sample usage data
        from datetime import datetime
        base_date = datetime.utcnow().date() - timedelta(days=30)
        
        usage_data = [
            (0, "MED001", 350, "Outpatient"),
            (0, "MED002", 120, "Emergency"),
            (0, "MED003", 280, "Outpatient"),
            (1, "MED001", 420, "Emergency"),
            (1, "MED003", 310, "Outpatient"),
            (2, "MED002", 85, "IPD"),
            (3, "MED004", 150, "Outpatient"),
            (4, "MED005", 5, "Emergency"),
        ]
        
        for i in range(30):
            for offset, med_id, qty, dept in usage_data:
                usage = HospitalUsage(
                    organization_id="HOSP001",
                    usage_date=base_date + timedelta(days=i),
                    medicine_id=med_id,
                    medicine_name="Medicine",
                    quantity_consumed=qty,
                    department=dept
                )
                db.add(usage)
        
        db.commit()
        print("✓ Sample data created successfully")
        print("\n  Default Login:")
        print("  Email: admin@hospital.com")
        print("  Password: password123")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding data: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Hospital Drug Inventory System - DB Setup")
    print("=" * 50)
    
    init_db()
    seed_sample_data()
    
    print("\n✓ Database initialization complete!")
    print("\nNext steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Login with credentials above")
