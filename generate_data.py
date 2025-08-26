#!/usr/bin/env python3
"""
Data Generation Script for Text-to-MQL Demo

This script generates sample data for the school database including:
- Departments (Computer Science, Mathematics, etc.)
- Teachers with specializations
- Courses with descriptions
- Students with GPAs
- Enrollments with grades

Usage:
    python generate_data.py
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.data_generator import DataGenerator
from app.core.database import db_manager


async def main():
    """Main function to generate sample data"""
    print("🚀 Starting Text-to-MQL Sample Data Generation...")
    
    try:
        # Connect to database
        print("📊 Connecting to MongoDB...")
        await db_manager.connect_to_mongo()
        print("✅ Connected to MongoDB successfully!")
        
        # Initialize data generator
        generator = DataGenerator()
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        await generator.clear_all_data()
        print("✅ Existing data cleared!")
        
        # Generate new sample data
        print("🏗️  Generating sample data...")
        await generator.generate_all_data()
        print("✅ Sample data generated successfully!")
        
        # Create indexes
        print("📝 Creating database indexes...")
        await db_manager.create_indexes()
        print("✅ Database indexes created!")
        
        print("\n🎉 Data generation completed successfully!")
        print("\n📈 Generated Data Summary:")
        print(f"   • {len(generator.departments_data)} Departments")
        print(f"   • {len(generator.teachers_data)} Teachers") 
        print(f"   • {len(generator.courses_data)} Courses")
        print(f"   • {len(generator.students_data)} Students")
        print(f"   • {len(generator.enrollments_data)} Enrollments")
        print("\n💡 Your database is now ready for Text-to-MQL queries!")
        
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        sys.exit(1)
        
    finally:
        # Close database connection
        await db_manager.close_mongo_connection()
        print("📋 Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
