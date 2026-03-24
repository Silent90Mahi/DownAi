#!/usr/bin/env python3
"""
SHG Platform Database Seeder
Command-line tool to populate database with dummy data

Usage:
    python seed_database.py                                    # Seed with defaults
    python seed_database.py --users 500 --products 2000   # Custom quantities
    python seed_database.py --orders-only                    # Seed only specific data
    python seed_database.py --clear                           # Clear existing data first
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.services.data_generator import seed_all_data, DataGenerator


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Seed SHG Platform Database with Dummy Data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed with default quantities (1000 users, 5000 products, 10000 orders)
  python seed_database.py

  # Seed with custom quantities
  python seed_database.py --users 500 --products 2000 --orders 5000

  # Seed only users (for testing)
  python seed_database.py --users-only

  # Clear existing data first
  python seed_database.py --clear

  # Show progress and statistics
  python seed_database.py --verbose
        """
    )

    # Data quantities
    parser.add_argument(
        '--users', '-u',
        type=int,
        default=1000,
        help='Number of users to generate (default: 1000)'
    )

    parser.add_argument(
        '--products', '-p',
        type=int,
        default=5000,
        help='Number of products to generate (default: 5000)'
    )

    parser.add_argument(
        '--orders', '-o',
        type=int,
        default=10000,
        help='Number of orders to generate (default: 10000)'
    )

    # Data selection
    parser.add_argument(
        '--users-only',
        action='store_true',
        help='Generate only users'
    )

    parser.add_argument(
        '--products-only',
        action='store_true',
        help='Generate only products (requires users to exist)'
    )

    parser.add_argument(
        '--orders-only',
        action='store_true',
        help='Generate only orders (requires users and products to exist)'
    )

    # Options
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before seeding'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be seeded without actually doing it'
    )

    return parser.parse_args()


def clear_database(db: Session, verbose: bool = False):
    """Clear existing data from database"""
    if verbose:
        print("Clearing existing data...")

    from app import models

    # Define deletion order (respecting foreign keys)
    tables_to_clear = [
        models.OrderItem,
        models.Order,
        models.BulkRequestItem,
        models.BulkRequestParticipant,
        models.BulkRequest,
        models.CoinTransaction,
        models.TrustHistory,
        models.Notification,
        models.ChatHistory,
        models.BuyerRequirement,
        models.MarketData,
        models.AnalyticsData,
        models.Material,
        models.Buyer,
        models.Supplier,
        models.Product,
        models.User
    ]

    for table in tables_to_clear:
        try:
            count = db.query(table).count()
            db.query(table).delete()
            if verbose:
                print(f"  ✓ Cleared {count} records from {table.__tablename__}")
        except Exception as e:
            if verbose:
                print(f"  ✗ Error clearing {table.__tablename__}: {e}")

    db.commit()
    if verbose:
        print("✓ Database cleared")


def show_plan(args):
    """Show what will be seeded without doing it"""
    print("=" * 60)
    print("SEEDING PLAN")
    print("=" * 60)
    print()
    print(f"Users:           {args.users}")
    print(f"Products:        {args.products}")
    print(f"Orders:          {args.orders}")
    print()

    if args.users_only:
        print("Mode: Users only")
    elif args.products_only:
        print("Mode: Products only")
    elif args.orders_only:
        print("Mode: Orders only")
    else:
        print("Mode: All data")

    if args.clear:
        print("Clear existing data: Yes")
    else:
        print("Clear existing data: No")

    print()
    print("This will also generate:")
    print("  - Suppliers: 500")
    print("  - Buyers: 300")
    print("  - Materials: 2,000")
    print("  - Bulk Requests: 100")
    print("  - Trust History: 10,000")
    print("  - Coin Transactions: 50,000")
    print("  - Notifications: 5,000")
    print("  - Market Data: 500")
    print("  - Analytics Data: 365 (days)")
    print("  - Chat History: 1,000")
    print()
    print("=" * 60)


async def main():
    """Main entry point"""
    args = parse_arguments()

    if args.dry_run:
        show_plan(args)
        return

    print("=" * 60)
    print("Ooumph SHG Platform - Database Seeder")
    print("=" * 60)
    print()

    # Clear database if requested
    if args.clear:
        confirm = input("Are you sure you want to clear all existing data? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return

        db = SessionLocal()
        try:
            clear_database(db, verbose=args.verbose)
        finally:
            db.close()
        print()

    # Seed data
    db = SessionLocal()
    try:
        if args.users_only:
            print(f"Generating {args.users} users only...")
            from app.services.data_generator import seed_users_only
            await seed_users_only(db, args.users)

        elif args.products_only:
            print(f"Generating {args.products} products only...")
            from app.services.data_generator import seed_products_only
            await seed_products_only(db, args.products)

        elif args.orders_only:
            print(f"Generating {args.orders} orders only...")
            from app.services.data_generator import seed_orders_only
            await seed_orders_only(db, args.orders)

        else:
            print(f"Seeding complete dataset:")
            print(f"  Users: {args.users}")
            print(f"  Products: {args.products}")
            print(f"  Orders: {args.orders}")
            print()

            result = await seed_all_data(
                db,
                users=args.users,
                products=args.products,
                orders=args.orders
            )

            print()
            print("=" * 60)
            print("SEEDING SUMMARY")
            print("=" * 60)
            for key, value in result.items():
                print(f"  {key.replace('_', ' ').title()}: {value:,}")
            print()

        print("=" * 60)
        print("✓ DATA SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("You can now start the application with:")
        print("  cd backend && uvicorn app.main:app --reload")

    except KeyboardInterrupt:
        print("\n✗ Seeding interrupted by user")
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
