from fastapi import FastAPI, HTTPException, Query
from sqlite3 import connect
from typing import Optional
from datetime import datetime, timezone
import asyncio
import random
# Database connection
DB_FILE = "logs.db"

app = FastAPI()

# Helper function to query the SQLite da
def query_database(query: str, params: tuple = ()):
    """
    Execute a query on the SQLite database and return the results.
    """
    try:
        with connect(DB_FILE) as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Background task to generate and insert sales, lead, and web logs
async def generate_logs():
    """
    Continuously generate and insert random logs into the database.
    """
    while True:
        sales_logs = []
        lead_logs = []
        web_logs = []

        # Generate sales logs
        for _ in range(3):
            sales_logs.append((
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                random.choice(["AI Assistant", "Rapid Prototyping", "Demo Session", "Event Participant Package", "Enterprise AI Package"]),
                random.choice(["Alice", "Bob", "Charlie", "Diana"]),
                random.randint(100, 1000),
                random.randint(10, 500),
                random.choice(["USA", "Canada", "UK", "Germany", "France"]),
                random.choice(["/home", "/about", "/products", "/services", "/demo"])
            ))

        # Generate lead logs
        for _ in range(2):
            lead_logs.append((
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                random.choice(["Website", "Social Media", "Email Campaign", "Referral"]),
                random.choice(["New", "Contacted", "Closed"])
            ))

        # Generate web logs
        for _ in range(3):
            web_logs.append((
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",  # Random IP
                random.choice(["/home", "/about", "/products", "/services", "/demo"]),
                random.choice(["GET", "POST"]),
                random.choice([200, 404, 500]),
                random.randint(100, 1000),
                random.choice(["Mozilla/5.0", "curl/7.64.1", "PostmanRuntime/7.28.4"])
            ))

        # Insert logs into the database
        try:
            with connect(DB_FILE) as connection:
                cursor = connection.cursor()

                # Insert sales logs
                cursor.executemany("""
                    INSERT INTO sales_metrics (timestamp, product, salesperson, revenue, profit, country, endpoint)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, sales_logs)

                # Insert lead logs
                cursor.executemany("""
                    INSERT INTO leads (timestamp, lead_source, lead_status)
                    VALUES (?, ?, ?)
                """, lead_logs)

                # Insert web logs
                cursor.executemany("""
                    INSERT INTO weblogs (timestamp, ip, endpoint, method, status_code, response_time_ms, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, web_logs)

                connection.commit()
            print(f"Inserted {len(sales_logs)} sales logs, {len(lead_logs)} lead logs, and {len(web_logs)} web logs.")
        except Exception as e:
            print(f"Error during log insertion: {e}")

        await asyncio.sleep(10)

@app.on_event("startup")
async def start_log_generation():
    """
    Start the background task to generate logs when the application starts.
    """
    asyncio.create_task(generate_logs())

@app.get("/filter-sales", summary="Filter sales metrics by date, salesperson, product, and country")
def filter_sales(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    salesperson: Optional[str] = Query(None, description="Salesperson name (e.g., Alice, Bob)"),
    product: Optional[str] = Query(None, description="Product name (e.g., AI Assistant)"),
    country: Optional[str] = Query(None, description="Country name (e.g., USA, UK)"),
):
    """
    Filters the sales_metrics table based on the provided query parameters.
    """
    # Build SQL query dynamically based on filters
    query = "SELECT timestamp, product, salesperson, revenue, profit, country FROM sales_metrics WHERE 1=1"
    params = []

    if start_date:
        query += " AND timestamp >= ?"
        params.append(f"{start_date} 00:00:00")
    if end_date:
        query += " AND timestamp <= ?"
        params.append(f"{end_date} 23:59:59")
    if salesperson:
        query += " AND salesperson = ?"
        params.append(salesperson)
    if product:
        query += " AND product = ?"
        params.append(product)
    if country:
        query += " AND country = ?"
        params.append(country)

    query += " ORDER BY timestamp DESC"

    results = query_database(query, tuple(params))
    columns = ["timestamp", "product", "salesperson", "revenue", "profit", "country"]
    filtered_data = [dict(zip(columns, row)) for row in results]

    return {"results": filtered_data}

# API Endpoints for KPIs
@app.get("/kpis/total-revenue")
def get_total_revenue():
    """
    Fetch the total revenue from sales metrics.
    """
    query = "SELECT SUM(revenue) FROM sales_metrics"
    result = query_database(query)
    total_revenue = result[0][0] if result and result[0][0] else 0
    return {"total_revenue": total_revenue}

@app.get("/kpis/total-sales-profit")
def get_total_sales_profit():
    """
    Fetch the total profit from sales metrics.
    """
    query = "SELECT SUM(profit) FROM sales_metrics"
    result = query_database(query)
    total_sales_profit = result[0][0] if result and result[0][0] else 0
    return {"total_sales_profit": total_sales_profit}

@app.get("/kpis/profit-per-salesperson")
def get_profit_per_salesperson():
    """
    Fetch total profit grouped by salesperson.
    """
    query = """
    SELECT salesperson, SUM(profit) AS total_profit
    FROM sales_metrics
    GROUP BY salesperson
    ORDER BY total_profit DESC
    """
    results = query_database(query)
    return {"profit_per_salesperson": [{"salesperson": row[0], "total_profit": row[1]} for row in results]}

@app.get("/kpis/profit-per-product")
def get_profit_per_product():
    """
    Fetch total profit grouped by product.
    """
    query = """
    SELECT product, SUM(profit) AS total_profit
    FROM sales_metrics
    GROUP BY product
    ORDER BY total_profit DESC
    """
    results = query_database(query)
    return {"profit_per_product": [{"product": row[0], "total_profit": row[1]} for row in results]}

@app.get("/kpis/sales-per-country")
def get_sales_per_country():
    """
    Fetch total revenue grouped by country.
    """
    query = """
    SELECT country, SUM(revenue) AS total_revenue
    FROM sales_metrics
    GROUP BY country
    ORDER BY total_revenue DESC
    """
    results = query_database(query)
    return {"sales_per_country": [{"country": row[0], "total_revenue": row[1]} for row in results]}

@app.get("/kpis/demo-requests")
def get_demo_requests():
    """
    Fetch the count of demo requests.
    """
    query = """
    SELECT COUNT(*) AS demo_requests
    FROM sales_metrics
    WHERE endpoint = "/demo"
    """
    result = query_database(query)
    demo_requests = result[0][0] if result else 0
    return {"demo_requests": demo_requests}

@app.get("/kpis/product-sales-per-country")
def get_product_sales_per_country(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Fetch total sales aggregated by country and product.
    Optional date range filters can be applied.
    """
    query = """
    SELECT country, product, SUM(revenue) AS total_revenue
    FROM sales_metrics
    WHERE 1=1
    """
    params = []
    query += " GROUP BY country, product ORDER BY country, total_revenue DESC"
    results = query_database(query, tuple(params))
    return {
        "product_sales_per_country": [
            {"country": row[0], "product": row[1], "total_revenue": row[2]} for row in results
        ]
    }

@app.get("/kpis/best-salesperson")
def get_best_salesperson(
    start_date: Optional[str] = Query(None),  # Format: YYYY-MM-DD
    end_date: Optional[str] = Query(None)     # Format: YYYY-MM-DD
):
    """
    Fetch the best salesperson ranked by total revenue and profit.
    Optional date range filters can be applied.
    """
    query = """
    SELECT salesperson, SUM(revenue) AS total_revenue, SUM(profit) AS total_profit
    FROM sales_metrics
    WHERE 1=1
    """
    params = []
    query += " GROUP BY salesperson ORDER BY total_revenue DESC LIMIT 1"

    # Execute the query and fetch results
    try:
        result = query_database(query, tuple(params))
        if result:
            best_salesperson = result[0]
            return {
                "salesperson": best_salesperson[0],
                "total_revenue": best_salesperson[1],
                "total_profit": best_salesperson[2]
            }
        else:
            # Return a default response if no salesperson data is found
            return {
                "salesperson": None,
                "total_revenue": 0,
                "total_profit": 0,
                "message": "No sales data available for the given criteria."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching best salesperson: {e}")

@app.get("/kpis/most-sold-product")
def get_most_sold_product(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Fetch the most sold product based on total revenue.
    Optional date range filters can be applied.
    """
    query = """
    SELECT product, SUM(revenue) AS total_revenue
    FROM sales_metrics
    WHERE 1=1
    """
    params = []
    query += " GROUP BY product ORDER BY total_revenue DESC LIMIT 1"
    result = query_database(query, tuple(params))
    if result:
        return {
            "product": result[0][0],
            "total_revenue": result[0][1]
        }
    print(f"DEBUG - Query Results: {result}")
    return {"product": None, "total_revenue": 0}

@app.get("/kpis/conversion-rate")
def get_conversion_rate(
    start_date: str = Query(None),  # Format: YYYY-MM-DD
    end_date: str = Query(None)     # Format: YYYY-MM-DD
):
    """
    Calculate the conversion rate based on leads turning into sales.
    Optional date range filters can be applied.
    """
    # Fetch the total number of leads
    lead_query = """
    SELECT COUNT(*) FROM leads
    WHERE 1=1
    """
    lead_params = []

    total_leads = query_database(lead_query, tuple(lead_params))[0][0]

    # Fetch the total number of sales
    sales_query = """
    SELECT COUNT(*) FROM sales_metrics
    WHERE 1=1
    """
    sales_params = []
    total_sales = query_database(sales_query, tuple(sales_params))[0][0]

    # Calculate conversion rate
    if total_leads == 0:
        conversion_rate = 0
    else:
        conversion_rate = (total_sales / total_leads) * 100

    return {
        "total_leads": total_leads,
        "total_sales": total_sales,
        "conversion_rate": round(conversion_rate, 2)  # Rounded to two decimal places
    }

@app.get("/kpis/total-revenue-profit-salesperson")
def get_total_revenue_profit_salesperson(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Fetch total revenue and profit per salesperson.
    Optional date range filters can be applied.
    """
    query = """
    SELECT salesperson, SUM(revenue) AS total_revenue, SUM(profit) AS total_profit
    FROM sales_metrics
    WHERE 1=1
    """
    params = []

    query += " GROUP BY salesperson ORDER BY total_revenue DESC"

    try:
        results = query_database(query, tuple(params))
        return [
            {"salesperson": row[0], "total_revenue": row[1], "total_profit": row[2]}
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

@app.get("/kpis/total-revenue-profit-product")
def get_total_revenue_profit_product(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Fetch total revenue and profit per product.
    Optional date range filters can be applied.
    """
    query = """
    SELECT product, SUM(revenue) AS total_revenue, SUM(profit) AS total_profit
    FROM sales_metrics
    WHERE 1=1
    """
    params = []

    query += " GROUP BY product ORDER BY total_revenue DESC"

    try:
        results = query_database(query, tuple(params))
        return [
            {"product": row[0], "total_revenue": row[1], "total_profit": row[2]}
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

@app.get("/kpis/total-website-visits")
def total_website_visits(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    query = "SELECT COUNT(*) FROM weblogs WHERE 1=1"
    params = []
    
    result = query_database(query, tuple(params))
    return {"total_website_visits": result[0][0]}

@app.get("/kpis/unique-visitors")
def unique_visitors(
    
):
    query = "SELECT COUNT(DISTINCT ip) FROM weblogs WHERE 1=1"
    params = []
    
    result = query_database(query, tuple(params))
    return {"unique_visitors": result[0][0]}

@app.get("/kpis/top-landing-pages")
def top_landing_pages(
    limit: int = Query(5, description="Number of top landing pages to return"),
    
):
    query = "SELECT endpoint, COUNT(*) as visits FROM weblogs WHERE 1=1"
    params = []
    
    query += " GROUP BY endpoint ORDER BY visits DESC LIMIT ?"
    params.append(limit)
    result = query_database(query, tuple(params))
    return {"top_landing_pages": [{"endpoint": row[0], "visits": row[1]} for row in result]}

@app.get("/kpis/demo-requests")
def demo_requests():
    
    query = "SELECT COUNT(*) FROM weblogs WHERE endpoint = '/demo'"
    params = []
    
    result = query_database(query, tuple(params))
    return {"demo_requests": result[0][0]}

@app.get("/kpis/leads-generated")
def leads_generated(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = "SELECT COUNT(*) FROM leads WHERE 1=1"
    params = []
    if start_date:
        query += " AND date(timestamp) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(timestamp) <= date(?)"
        params.append(end_date)
    result = query_database(query, tuple(params))  # Only pass params if there are ?
    return {"leads_generated": result[0][0]}

@app.get("/kpis/leads-by-source")
def leads_by_source(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = "SELECT lead_source, COUNT(*) as count FROM leads WHERE 1=1"
    params = []
    
    query += " GROUP BY lead_source ORDER BY count DESC"
    rows = query_database(query, tuple(params))
    return {"leads_by_source": [{"lead_source": row[0], "count": row[1]} for row in rows]}

@app.get("/kpis/leads-by-status")
def leads_by_status(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = "SELECT lead_status, COUNT(*) as count FROM leads WHERE 1=1"
    params = []
    if end_date:
        query += " AND date(timestamp) <= date(?)"
        params.append(end_date)
    query += " GROUP BY lead_status ORDER BY count DESC"
    rows = query_database(query, tuple(params))
    return {"leads_by_status": [{"lead_status": row[0], "count": row[1]} for row in rows]}

@app.get("/kpis/lead-conversion-rate")
def lead_conversion_rate(
    
):
    total_query = "SELECT COUNT(*) FROM leads WHERE 1=1"
    converted_query = "SELECT COUNT(*) FROM leads WHERE lead_status = 'Closed'"
    params = []
    params_converted = []
    
    total = query_database(total_query, tuple(params))[0][0]
    converted = query_database(converted_query, tuple(params_converted))[0][0]
    rate = (converted / total) * 100 if total > 0 else 0
    return {"lead_conversion_rate": round(rate, 2)}

@app.get("/kpis/leads-by-day")
def leads_by_day(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = """
        SELECT date(timestamp) as date, COUNT(*) as count
        FROM leads
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND date(timestamp) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(timestamp) <= date(?)"
        params.append(end_date)
    query += " GROUP BY date(timestamp) ORDER BY date(timestamp)"
    rows = query_database(query, tuple(params))
    return {"leads_by_day": [{"date": row[0], "count": row[1]} for row in rows]}

# Health Check Endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint to confirm the API is running.
    """
    return {"status": "API is running"}