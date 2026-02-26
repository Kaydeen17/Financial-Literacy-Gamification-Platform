from app import create_app, db
from app.models import AvailableStock, AvailableBond

app = create_app()

def seed_assets():
    print("Seeding Investment Assets...")

    # --- 10 STOCKS ---
    stocks = [
        AvailableStock(
            company_name="Blue Mountain Tech", ticker="BMT", current_price=150.25,
            roe_percentage=18.5, debt_to_equity=0.45, profit_margin=12.0,
            moat_description="Strong brand loyalty and high switching costs in cloud infrastructure.",
            intrinsic_value=165.00
        ),
        AvailableStock(
            company_name="Caribbean Logistics Corp", ticker="CLC", current_price=45.50,
            roe_percentage=12.0, debt_to_equity=1.20, profit_margin=8.5,
            moat_description="Dominant port access and established shipping routes.",
            intrinsic_value=42.00
        ),
        AvailableStock(
            company_name="Island Energy Solutions", ticker="IES", current_price=88.10,
            roe_percentage=15.2, debt_to_equity=0.80, profit_margin=20.0,
            moat_description="Regulated monopoly on solar grid distribution.",
            intrinsic_value=95.00
        ),
        AvailableStock(
            company_name="Reggae Retailers Ltd", ticker="RRL", current_price=12.30,
            roe_percentage=8.0, debt_to_equity=0.30, profit_margin=4.2,
            moat_description="Large physical footprint, but facing e-commerce competition.",
            intrinsic_value=10.50
        ),
        AvailableStock(
            company_name="FinQuest Bank Group", ticker="FQB", current_price=210.00,
            roe_percentage=22.5, debt_to_equity=2.10, profit_margin=25.0,
            moat_description="High regulatory barriers and massive low-cost deposit base.",
            intrinsic_value=230.00
        ),
        AvailableStock(
            company_name="Tropic Pharma", ticker="TPH", current_price=65.40,
            roe_percentage=25.0, debt_to_equity=0.15, profit_margin=30.0,
            moat_description="Proprietary patents on local herbal medicines.",
            intrinsic_value=85.00
        ),
        AvailableStock(
            company_name="Coastal Real Estate", ticker="CRE", current_price=34.20,
            roe_percentage=10.5, debt_to_equity=1.50, profit_margin=15.0,
            moat_description="Prime beachfront property holdings that cannot be replicated.",
            intrinsic_value=30.00
        ),
        AvailableStock(
            company_name="NextGen Telecom", ticker="NGT", current_price=115.00,
            roe_percentage=14.0, debt_to_equity=1.10, profit_margin=11.0,
            moat_description="Scale advantage with the only 6G fiber network in the region.",
            intrinsic_value=105.00
        ),
        AvailableStock(
            company_name="Global Grain Co", ticker="GGC", current_price=55.00,
            roe_percentage=9.0, debt_to_equity=0.60, profit_margin=6.0,
            moat_description="Low cost producer with global distribution contracts.",
            intrinsic_value=58.00
        ),
        AvailableStock(
            company_name="Cyber Shield Inc", ticker="CSI", current_price=190.00,
            roe_percentage=30.2, debt_to_equity=0.05, profit_margin=35.0,
            moat_description="Mission-critical software; extremely high customer retention.",
            intrinsic_value=215.00
        )
    ]

    # --- 5 BONDS ---
    bonds = [
        AvailableBond(
            issuer_name="Government of Jamaica", face_value=1000.00, 
            coupon_rate=0.0850, maturity_hours=72, risk_rating="A"
        ),
        AvailableBond(
            issuer_name="FinQuest Infrastructure", face_value=500.00, 
            coupon_rate=0.0625, maturity_hours=48, risk_rating="AA"
        ),
        AvailableBond(
            issuer_name="Kingston Municipal Bond", face_value=100.00, 
            coupon_rate=0.0450, maturity_hours=24, risk_rating="AAA"
        ),
        AvailableBond(
            issuer_name="High-Yield Tech Note", face_value=1000.00, 
            coupon_rate=0.1200, maturity_hours=120, risk_rating="B"
        ),
        AvailableBond(
            issuer_name="Green Energy Green Bond", face_value=500.00, 
            coupon_rate=0.0700, maturity_hours=36, risk_rating="AA"
        )
    ]

    try:
        db.session.add_all(stocks)
        db.session.add_all(bonds)
        db.session.commit()
        print(f"Successfully seeded {len(stocks)} stocks and {len(bonds)} bonds!")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding assets: {e}")

if __name__ == "__main__":
    with app.app_context():
        seed_assets()