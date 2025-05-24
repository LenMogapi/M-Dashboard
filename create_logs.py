import sqlite3
import random
from datetime import datetime, timezone
import geoip2.database
from geoip2.errors import AddressNotFoundError

# Path to your GeoLite2-Country database in the 'data' directory
GEOIP_DB_PATH = "data/GeoLite2-Country.mmdb"

# Function to extract valid IP addresses and countries from the MMDB file
def extract_ip_addresses_and_countries_from_mmdb():
    ip_country_map = []
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            for i in range(1, 256):
                for j in range(1, 256):
                    ip = f"192.0.{i}.{j}"  # Replace with public IP ranges if needed
                    try:
                        response = reader.country(ip)
                        if response.country.iso_code:  # Check if a country is associated with the IP
                            ip_country_map.append((ip, response.country.iso_code))
                    except AddressNotFoundError:
                        continue
    except Exception as e:
        print(f"Error reading MMDB file: {e}")
    return ip_country_map

# Generate random data for the weblogs table
def generate_weblog_entry(ip, country, log_id):
    current_time = datetime.now(timezone.utc)
    return {
        "id": log_id,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "access_time": current_time.strftime("%H:%M:%S"),
        "ip": ip,
        "country": country,
        "endpoint": random.choice(["/home", "/about", "/products", "/services", "/contact"]),
        "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
        "status_code": random.choice([200, 201, 400, 404, 500]),
        "response_time_ms": random.randint(50, 5000),
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ])
    }

# Generate random data for the sales_metrics table
def generate_sales_metric_entry(log_id, country, endpoint):
    current_time = datetime.now(timezone.utc)
    return {
        "id": log_id,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "product": random.choice(["AI Assistant", "Rapid Prototyping", "Demo Session", "Event Participant Package", "Enterprise AI Package"]),
        "salesperson": random.choice(["Alice", "Bob", "Charlie", "Diana"]),
        "revenue": random.randint(100, 1000),
        "profit": random.randint(10, 500),
        "country": country,
        "endpoint": endpoint
    }

# Generate random data for the leads table
def generate_lead_entry(log_id):
    current_time = datetime.now(timezone.utc)
    return {
        "id": log_id,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "lead_source": random.choice(["Website", "Social Media", "Email Campaign", "Referral"]),
        "lead_status": random.choice(["New", "Contacted", "Closed"])
    }

# Function to reset and restructure the database
def reset_and_restructure_database():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    # Delete existing data
    cursor.execute("DROP TABLE IF EXISTS weblogs")
    cursor.execute("DROP TABLE IF EXISTS sales_metrics")
    cursor.execute("DROP TABLE IF EXISTS leads")

    # Create the tables with matching schemas
    cursor.execute("""
    CREATE TABLE weblogs (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        access_time TEXT,
        ip TEXT,
        country TEXT,
        endpoint TEXT,
        method TEXT,
        status_code INTEGER,
        response_time_ms INTEGER,
        user_agent TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE sales_metrics (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        product TEXT,
        salesperson TEXT,
        revenue INTEGER,
        profit INTEGER,
        country TEXT,
        endpoint TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE leads (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        lead_source TEXT,
        lead_status TEXT
    )
    """)

    conn.commit()
    conn.close()

# Function to save logs to the database
def save_logs_to_db(logs, table_name):
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    for log in logs:
        try:
            if table_name == "weblogs":
                cursor.execute("""
                    INSERT INTO weblogs (id, timestamp, access_time, ip, country, endpoint, method, status_code, response_time_ms, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log["id"],
                    log["timestamp"],
                    log["access_time"],
                    log["ip"],
                    log["country"],
                    log["endpoint"],
                    log["method"],
                    log["status_code"],
                    log["response_time_ms"],
                    log["user_agent"]
                ))
            elif table_name == "sales_metrics":
                cursor.execute("""
                    INSERT INTO sales_metrics (id, timestamp, product, salesperson, revenue, profit, country, endpoint)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log["id"],
                    log["timestamp"],
                    log["product"],
                    log["salesperson"],
                    log["revenue"],
                    log["profit"],
                    log["country"],
                    log["endpoint"]
                ))
            elif table_name == "leads":
                cursor.execute("""
                    INSERT INTO leads (id, timestamp, lead_source, lead_status)
                    VALUES (?, ?, ?, ?)
                """, (
                    log["id"],
                    log["timestamp"],
                    log["lead_source"],
                    log["lead_status"]
                ))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting log {log['id']} into {table_name}: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Step 1: Reset and restructure the database
    reset_and_restructure_database()

    # Step 2: Extract IP addresses and countries from the MMDB file
    ip_country_map = extract_ip_addresses_and_countries_from_mmdb()
    if not ip_country_map:
        print("No IP addresses or countries were extracted from the MMDB file. Exiting.")
        exit()

    # Step 3: Generate logs
    num_logs = 100
    weblogs = []
    sales_metrics = []
    leads = []
    for log_id in range(1, num_logs + 1):
        ip, country = random.choice(ip_country_map)
        endpoint = random.choice(["/home", "/about", "/products", "/services", "/contact"])
        
        # Generate logs for each table
        weblog_entry = generate_weblog_entry(ip, country, log_id)
        sales_metric_entry = generate_sales_metric_entry(log_id, country, endpoint)
        lead_entry = generate_lead_entry(log_id)
        
        weblogs.append(weblog_entry)
        sales_metrics.append(sales_metric_entry)
        leads.append(lead_entry)

    # Step 4: Save logs to the database
    save_logs_to_db(weblogs, "weblogs")
    save_logs_to_db(sales_metrics, "sales_metrics")
    save_logs_to_db(leads, "leads")

    print(f"Generated {len(weblogs)} weblogs, {len(sales_metrics)} sales metrics, and {len(leads)} leads, and saved them to the database.")
    
