from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

#database file to connect with supabase
if not url or not key or url.startswith("your_"):
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not set. Using mock data.")
    class MockSupabase:
        class Table:
            def insert(self, data):
                class InsertQuery:
                    def execute(self):
                        return type('Result', (), {'data': [data]})()
                return InsertQuery()
        
        def table(self, name):
            return self.Table()
        
        def rpc(self, name, params):
            class RpcQuery:
                def execute(self):
                    return type('Result', (), {'data': []})()
            return RpcQuery()
    
    supabase = MockSupabase()
else:
    supabase: Client = create_client(url, key)

