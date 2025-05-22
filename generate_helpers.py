import random

# Generate a random IP address
def generate_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

# Generate a random endpoint
def generate_endpoint():
    return random.choice(["/home", "/products", "/checkout", "/api", "/login"])

# Generate a random HTTP method
def generate_http_method():
    return random.choice(["GET", "POST", "PUT", "DELETE"])

# Generate a random status code
def generate_status_code():
    return random.choice([200, 201, 400, 401, 403, 404, 500])

# Generate a random response time in milliseconds
def generate_response_time():
    return round(random.uniform(50, 5000), 2)

# Generate a random user agent
def generate_user_agent():
    return random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ])