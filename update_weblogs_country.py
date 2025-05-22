import sqlite3
import geoip2.database

# Path to your SQLite database
DATABASE_PATH = "./logs.db"

# Path to the GeoLite2 database
GEOIP_DB_PATH = "data/GeoLite2-Country.mmdb"

# Function to convert IP address to country
def ip_to_country(ip_address):
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.country(ip_address)
            return response.country.name  # Returns the country name
    except geoip2.errors.AddressNotFoundError:
        return "Unknown Country"
    except Exception as e:
        return f"Error: {str(e)}"

# Update the `weblogs` table
def update_weblogs_with_country():
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Query all IP addresses in `weblogs` where country is NULL
    cursor.execute("SELECT id, ip FROM weblogs WHERE country IS NULL")
    rows = cursor.fetchall()

    for row in rows:
        weblog_id, ip_address = row
        country = ip_to_country(ip_address)  # Convert IP to country
        cursor.execute("UPDATE weblogs SET country = ? WHERE id = ?", (country, weblog_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_weblogs_with_country()
    print("Weblogs table updated with country names.")