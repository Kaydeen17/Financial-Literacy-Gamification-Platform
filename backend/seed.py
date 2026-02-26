from app import create_app, db
from app.models import User, FixedDeposit
from datetime import datetime, timedelta
from decimal import Decimal

app = create_app()

with app.app_context():
    # 1. Get a test user (adjust the username to match your DB)
    user = User.query.filter_by(username="quest_master").first()
    
    if not user:
        print("User not found! Please register a user first.")
    else:
        # 2. Create an "Active" Deposit (Started 1 hour ago)
        fd1 = FixedDeposit(
            user_id=user.user_id,
            principal=Decimal('1000.00'),
            interest_rate=Decimal('0.01'), # 1%
            duration_hours=24,
            start_time=datetime.utcnow() - timedelta(hours=1),
            is_matured=False
        )

        # 3. Create a "Ready to Mature" Deposit (Started 25 hours ago)
        fd2 = FixedDeposit(
            user_id=user.user_id,
            principal=Decimal('5000.00'),
            interest_rate=Decimal('0.03'), # 3%
            duration_hours=24,
            start_time=datetime.utcnow() - timedelta(hours=25),
            is_matured=False
        )

        db.session.add(fd1)
        db.session.add(fd2)
        db.session.commit()
        print("Fixed Deposits seeded! You have one active and one matured.")