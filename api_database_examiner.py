#!/usr/bin/env python3
"""
API-Based Database Examination Script

This script uses the API endpoints to examine all collections and uses AI to analyze relationships.
It creates a comprehensive map of collection structure and relationships.
"""

import asyncio
import json
import aiohttp
import subprocess
import time
import signal
import sys
import os
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.llm_service import llm_service


class DatabaseExaminer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.collections_data = {}
        self.relationship_map = {}
        self.server_process = None
        
    async def start_server_if_needed(self):
        """Check if server is running, start if needed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/database/health", timeout=5) as response:
                    if response.status == 200:
                        print("✅ Server is already running")
                        return True
        except Exception:
            print("🚀 Starting server...")
            
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Wait for server to start
            for i in range(10):  # Wait up to 10 seconds
                try:
                    time.sleep(1)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{self.base_url}/api/database/health", timeout=5) as response:
                            if response.status == 200:
                                print("✅ Server started successfully")
                                return True
                except Exception:
                    continue
            
            print("❌ Failed to start server")
            return False
    
    def cleanup_server(self):
        """Clean up server process"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
    
    async def get_all_collections(self) -> Dict[str, Any]:
        """Get all collections using API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/database/collections") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"❌ Failed to get collections: {response.status}")
                        return {}
        except Exception as e:
            print(f"❌ Error getting collections: {e}")
            return {}
    
    async def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema for a specific collection using API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/database/schema/{collection_name}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"❌ Failed to get schema for {collection_name}: {response.status}")
                        return {}
        except Exception as e:
            print(f"❌ Error getting schema for {collection_name}: {e}")
            return {}
    
    async def analyze_collection_relationships(self, collections_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze relationships between collections"""
        
        # Prepare data for AI analysis
        collection_summaries = {}
        for collection_name, schema_data in collections_info.items():
            if 'schema' in schema_data:
                schema = schema_data['schema']
                collection_summaries[collection_name] = {
                    'document_count': schema.get('document_count', 0),
                    'fields': schema.get('fields', {}),
                    'sample_documents': schema.get('sample_documents', [])[:2]  # Only first 2 samples
                }
        
        # Create prompt for AI analysis
        prompt = f"""
Analyze the following MongoDB collections from a school database and provide a comprehensive relationship analysis.

Database: {settings.DATABASE_NAME}
Collections Data:
{json.dumps(collection_summaries, indent=2)}

Please provide analysis in the following JSON format:
{{
    "collection_purposes": {{
        "collection_name": {{
            "purpose": "What this collection stores and why it exists",
            "main_entities": ["primary entities stored"],
            "business_role": "Role in school management system"
        }}
    }},
    "hierarchy": {{
        "root_collections": ["Independent collections that don't depend on others"],
        "dependent_collections": ["Collections that reference other collections"],
        "relationships": {{
            "collection_name": {{
                "depends_on": ["collections this depends on"],
                "referenced_by": ["collections that reference this"],
                "relationship_type": "one-to-many|many-to-many|one-to-one",
                "foreign_key_fields": ["field names that reference other collections"],
                "description": "How this collection relates to others"
            }}
        }}
    }},
    "data_flow_patterns": {{
        "process_name": {{
            "description": "Business process description",
            "steps": ["Step-by-step data flow"],
            "collections_involved": ["collections used in this process"],
            "typical_queries": ["Common query patterns for this process"]
        }}
    }},
    "field_relationships": {{
        "foreign_keys": {{
            "source_collection.field": "target_collection.field"
        }},
        "lookup_patterns": {{
            "description": "Common lookup patterns between collections"
        }}
    }},
    "query_optimization": {{
        "collection_name": {{
            "primary_indexes": ["fields that should be indexed"],
            "common_filters": ["frequently filtered fields"],
            "join_strategies": ["how to efficiently join with other collections"]
        }}
    }},
    "schema_insights": {{
        "data_consistency": ["observations about data consistency"],
        "naming_patterns": ["patterns in field naming"],
        "potential_improvements": ["suggestions for schema optimization"]
    }}
}}

Focus on practical insights that would help an AI agent understand how to:
1. Navigate between collections efficiently
2. Understand the business logic and data relationships
3. Generate optimal queries for common school management operations
4. Understand the hierarchy and dependencies for complex queries

Be specific about field relationships and provide actionable insights.
"""

        try:
            print("🤖 Using AI to analyze collection relationships...")
            # Use LLM service to analyze relationships
            analysis_response = await llm_service.generate_response(prompt)
            
            # Try to parse as JSON
            try:
                parsed_analysis = json.loads(analysis_response)
                print("✅ AI analysis completed successfully")
                return parsed_analysis
            except json.JSONDecodeError:
                print("⚠️  AI response was not valid JSON, returning raw response")
                return {"raw_analysis": analysis_response}
                
        except Exception as e:
            print(f"❌ Error analyzing relationships: {e}")
            return {"error": str(e)}
    
    async def examine_database(self):
        """Main examination function"""
        print("🔍 Starting API-Based Database Examination...")
        print("=" * 60)
        
        try:
            # Step 1: Start server if needed
            server_running = await self.start_server_if_needed()
            if not server_running:
                print("❌ Cannot proceed without server running")
                return
            
            # Step 2: Get all collections
            print("\n📚 Getting all collections...")
            collections_response = await self.get_all_collections()
            
            if not collections_response.get('success'):
                print(f"❌ Failed to get collections: {collections_response}")
                return
            
            collections_list = collections_response.get('collections', [])
            collections_stats = collections_response.get('stats', {})
            
            print(f"✅ Found {len(collections_list)} collections:")
            for collection in collections_list:
                if not collection.startswith('system.'):
                    count = collections_stats.get(collection, {}).get('document_count', 0)
                    print(f"   • {collection}: {count} documents")
            
            # Step 3: Get schema for each collection
            print("\n🔬 Analyzing collection schemas...")
            collections_info = {}
            
            for collection_name in collections_list:
                if collection_name.startswith('system.'):
                    continue
                    
                print(f"   📋 Analyzing {collection_name}...")
                schema_data = await self.get_collection_schema(collection_name)
                
                if schema_data.get('success'):
                    collections_info[collection_name] = schema_data
                    schema = schema_data.get('schema', {})
                    
                    print(f"      ✅ Documents: {schema.get('document_count', 0)}")
                    print(f"      🔑 Fields: {list(schema.get('fields', {}).keys())}")
                else:
                    print(f"      ❌ Failed to get schema for {collection_name}")
            
            # Step 4: AI Analysis of relationships
            print("\n🤖 Running AI analysis of collection relationships...")
            relationship_analysis = await self.analyze_collection_relationships(collections_info)
            
            # Step 5: Generate comprehensive map
            print("\n📊 Generating comprehensive collection map...")
            collection_map = {
                "metadata": {
                    "database_name": settings.DATABASE_NAME,
                    "examination_method": "API-based with AI analysis",
                    "total_collections": len([c for c in collections_list if not c.startswith('system.')]),
                    "total_documents": sum(
                        stat.get('document_count', 0) 
                        for col, stat in collections_stats.items() 
                        if not col.startswith('system.')
                    ),
                    "examination_timestamp": "2025-09-03",
                    "llm_provider": settings.DEFAULT_LLM_PROVIDER,
                    "llm_model": settings.DEFAULT_LLM_MODEL
                },
                "collections_raw_data": collections_info,
                "collection_statistics": {
                    col: stat for col, stat in collections_stats.items() 
                    if not col.startswith('system.')
                },
                "ai_analysis": relationship_analysis,
                "agent_knowledge_base": self.create_agent_knowledge_base(collections_info, relationship_analysis)
            }
            
            # Save to file
            output_file = 'comprehensive_database_map.json'
            with open(output_file, 'w') as f:
                json.dump(collection_map, f, indent=2, default=str)
            
            print(f"✅ Comprehensive collection map saved to '{output_file}'")
            
            # Step 6: Print summary
            self.print_summary(collection_map)
            
            return collection_map
            
        except Exception as e:
            print(f"❌ Error during examination: {e}")
            return None
        
        finally:
            self.cleanup_server()
    
    def create_agent_knowledge_base(self, collections_info: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured knowledge base for the agent"""
        
        knowledge_base = {
            "collection_catalog": {},
            "relationship_map": {},
            "query_strategies": {},
            "business_logic": {}
        }
        
        # Extract collection catalog
        for collection_name, schema_data in collections_info.items():
            if 'schema' in schema_data:
                schema = schema_data['schema']
                knowledge_base["collection_catalog"][collection_name] = {
                    "purpose": self.get_collection_purpose(collection_name),
                    "document_count": schema.get('document_count', 0),
                    "key_fields": list(schema.get('fields', {}).keys()),
                    "field_types": schema.get('fields', {}),
                    "searchable_fields": self.identify_searchable_fields(schema.get('fields', {})),
                    "sample_structure": schema.get('sample_documents', [{}])[0] if schema.get('sample_documents') else {}
                }
        
        # Extract relationships from AI analysis
        if 'hierarchy' in ai_analysis and 'relationships' in ai_analysis['hierarchy']:
            knowledge_base["relationship_map"] = ai_analysis['hierarchy']['relationships']
        
        # Extract query strategies
        if 'query_optimization' in ai_analysis:
            knowledge_base["query_strategies"] = ai_analysis['query_optimization']
        
        # Extract business logic
        if 'data_flow_patterns' in ai_analysis:
            knowledge_base["business_logic"] = ai_analysis['data_flow_patterns']
        
        return knowledge_base
    
    def get_collection_purpose(self, collection_name: str) -> str:
        """Get the purpose of each collection"""
        purposes = {
            "departments": "Academic departments that organize the school structure",
            "teachers": "Faculty members and their employment details",
            "courses": "Academic courses offered by the school",
            "students": "Students enrolled in the school",
            "enrollments": "Student course enrollment records with grades"
        }
        return purposes.get(collection_name, f"Data storage for {collection_name}")
    
    def identify_searchable_fields(self, fields: Dict[str, str]) -> List[str]:
        """Identify fields that are commonly used for searching"""
        searchable_patterns = ['name', 'title', 'description', 'code', 'id', 'email', 'phone']
        searchable_fields = []
        
        for field_name in fields.keys():
            if any(pattern in field_name.lower() for pattern in searchable_patterns):
                searchable_fields.append(field_name)
        
        return searchable_fields
    
    def print_summary(self, collection_map: Dict[str, Any]):
        """Print a human-readable summary"""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE DATABASE ANALYSIS SUMMARY")
        print("=" * 70)
        
        # Metadata
        metadata = collection_map.get('metadata', {})
        print(f"\n🏫 Database: {metadata.get('database_name', 'Unknown')}")
        print(f"📊 Collections: {metadata.get('total_collections', 0)}")
        print(f"📄 Total Documents: {metadata.get('total_documents', 0)}")
        print(f"🤖 Analysis Method: {metadata.get('examination_method', 'Unknown')}")
        print(f"🧠 LLM Provider: {metadata.get('llm_provider', 'Unknown')}")
        
        # Collections overview
        print(f"\n📚 Collections Overview:")
        knowledge_base = collection_map.get('agent_knowledge_base', {})
        catalog = knowledge_base.get('collection_catalog', {})
        
        for collection_name, info in catalog.items():
            print(f"\n   🗂️  {collection_name.upper()}")
            print(f"      📝 Purpose: {info.get('purpose', 'Unknown')}")
            print(f"      📊 Documents: {info.get('document_count', 0)}")
            print(f"      🔑 Key Fields: {', '.join(info.get('key_fields', [])[:5])}")
            searchable = info.get('searchable_fields', [])
            if searchable:
                print(f"      🔍 Searchable: {', '.join(searchable)}")
        
        # AI Analysis Summary
        ai_analysis = collection_map.get('ai_analysis', {})
        if 'hierarchy' in ai_analysis:
            hierarchy = ai_analysis['hierarchy']
            print(f"\n🔗 Collection Relationships:")
            
            root_collections = hierarchy.get('root_collections', [])
            if root_collections:
                print(f"   🌳 Independent: {', '.join(root_collections)}")
            
            dependent_collections = hierarchy.get('dependent_collections', [])
            if dependent_collections:
                print(f"   📎 Dependent: {', '.join(dependent_collections)}")
        
        # Business processes
        if 'data_flow_patterns' in ai_analysis:
            patterns = ai_analysis['data_flow_patterns']
            print(f"\n💼 Business Processes:")
            for process_name, process_info in patterns.items():
                print(f"   • {process_name}: {process_info.get('description', 'No description')}")
        
        print(f"\n🎯 Agent Knowledge Base Created!")
        print(f"   📚 Collection Catalog: {len(catalog)} collections mapped")
        print(f"   🔗 Relationship Map: Available")
        print(f"   🎯 Query Strategies: Defined")
        print(f"   💼 Business Logic: Documented")
        
        print(f"\n✅ Complete analysis saved to 'comprehensive_database_map.json'")
        print("   This file contains all the information needed for the AI agent")
        print("   to understand your database structure and relationships!")
        print("=" * 70)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Interrupted by user")
    sys.exit(0)


async def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    examiner = DatabaseExaminer()
    try:
        await examiner.examine_database()
    except KeyboardInterrupt:
        print("\n🛑 Examination interrupted")
    finally:
        examiner.cleanup_server()


if __name__ == "__main__":
    asyncio.run(main())
