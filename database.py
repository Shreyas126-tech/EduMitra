import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Use absolute path to find .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv() 

def get_engine():
    url_str = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")
    if not url_str:
        # Fallback to hardcoded string only for this specific test case
        url_str = "postgresql://postgres.pulynoizvzqapnfvwajj:RcGiPFWEFPNbktpK@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
    
    if url_str.startswith("postgres://"):
        url_str = url_str.replace("postgres://", "postgresql://", 1)

    try:
        # Robust URL parsing using manual extraction
        # Handle the ?sslmode=require part
        clean_url = url_str.split("?")[0]
        
        # scheme://user:pass@host:port/dbname
        scheme_part, rest = clean_url.split("://")
        user_pass, host_db = rest.split("@")
        user, password = user_pass.split(":", 1)
        host_port, dbname = host_db.split("/", 1)
        
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
            
        print(f"📡 Database connection initialized for host: {host}")
        
        # Build URL object manually to avoid rfc1738 parsing errors
        url_obj = URL.create(
            drivername=scheme_part,
            username=user,
            password=urllib.parse.unquote(password), # Ensure password is unquoted if it was already encoded
            host=host,
            port=port,
            database=dbname,
            query={"sslmode": "require"}
        )
        
        return create_engine(url_obj, poolclass=NullPool)
    except Exception as e:
        print(f"⚠️ Manual URL creation failed: {e}. Falling back to string parse...")
        return create_engine(url_str, poolclass=NullPool)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
