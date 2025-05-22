import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import plotly.io as pio
from fpdf import fpdf

API_BASE_URL = "http://127.0.0.1:8001"

st.set_page_config(page_title="AI-SOLUTIONS SALES DASHBOARD", layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
        }
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 AI-SOLUTIONS SALES DASHBOARD")

# API Fetch Function
def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except:
        return None

# Metric Renderer
def render_metric(title, value):
    st.metric(label=title, value=value)

# Dashboard Layout
def render_dashboard():
    st.sidebar.markdown("### 🔎 Filter Options")
    start_date = st.sidebar.date_input("Start Date", datetime.now()).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End Date", datetime.now()).strftime("%Y-%m-%d")

    salesperson_filter = st.sidebar.selectbox("Salesperson", ["All", "Alice", "Bob", "Charlie", "Diana"])
    product_filter = st.sidebar.selectbox("Product", ["All", "AI Assistant", "Rapid Prototyping", "Demo Session", "Event Participant Package", "Enterprise AI Package"])
    country_filter = st.sidebar.selectbox("Country", ["All", "USA", "Canada", "UK", "Germany", "France"])

    apply_filter = st.sidebar.button("Apply Filters")

    # Always build params
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if salesperson_filter != "All":
        params["salesperson"] = salesperson_filter
    if product_filter != "All":
        params["product"] = product_filter
    if country_filter != "All":
        params["country"] = country_filter

    if apply_filter:
        with st.spinner("Fetching filtered sales data..."):
            data = fetch_data("/filter-sales", params=params)
            if data and "results" in data and data["results"]:
                df = pd.DataFrame(data["results"])
                st.session_state["filtered_df"] = df  # Store in session
                st.dataframe(df)

    # Only show download if data is available
    if "filtered_df" in st.session_state:
        st.sidebar.download_button(
            label="Download Filtered Data",
            data=st.session_state["filtered_df"].to_csv(index=False),
            file_name="filtered_sales.csv",
            mime="text/csv"
        )
     
    #Download PDF Report ---
# Allow user to select which metrics to export
    st.sidebar.markdown("### 📥 Download Report")
    selected_metrics = st.sidebar.multiselect(
        "Select Metrics to Export",
        ["Total Revenue", "Total Profit", "Best Salesperson", "Most Sold Product", "Sales by Country"]
    )
    if st.sidebar.button("Download PDF Report"):
        pdf = fpdf.FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title
        pdf.cell(200, 10, "Sales Dashboard Report", ln=True, align='C')

        # Add selected metrics
        for metric in selected_metrics:
            if metric == "Total Revenue":
                total_revenue = fetch_data("/kpis/total-revenue")
                pdf.cell(200, 10, f"Total Revenue: ${total_revenue['total_revenue']:,}" if total_revenue else "N/A", ln=True)
            elif metric == "Total Profit":
                total_profit = fetch_data("/kpis/total-sales-profit")
                pdf.cell(200, 10, f"Total Profit: ${total_profit['total_sales_profit']:,}" if total_profit else "N/A", ln=True)
            elif metric == "Best Salesperson":
                best_salesperson = fetch_data("/kpis/best-salesperson")
                pdf.cell(200, 10, f"Best Salesperson: {best_salesperson['salesperson']}" if best_salesperson else "N/A", ln=True)
            elif metric == "Most Sold Product":
                most_sold_product = fetch_data("/kpis/most-sold-product")
                pdf.cell(200, 10, f"Most Sold Product: {most_sold_product['product']}" if most_sold_product else "N/A", ln=True)
            elif metric == "Sales by Country":
                sales_per_country = fetch_data("/kpis/sales-per-country")
                if sales_per_country and "sales_per_country" in sales_per_country:
                    sales_by_country_str = "\n".join([f"{row['country']}: ${row['total_revenue']:,}" for row in sales_per_country["sales_per_country"]])
                    pdf.multi_cell(0, 10, f"Sales by Country:\n{sales_by_country_str}", align='L')
                else:
                    pdf.multi_cell(0, 10, "Sales by Country: N/A", align='L')

        # Save the PDF to a file
        pdf_file_path = "sales_dashboard_report.pdf"
        pdf.output(pdf_file_path)

        # Provide download link
        with open(pdf_file_path, "rb") as f:
            st.sidebar.download_button(
                label="Download PDF Report",
                data=f,
                file_name=pdf_file_path,
                mime="application/pdf"
            )

            #Download CSV Report
    st.sidebar.markdown("### 📥 Download CSV Report")
    if st.sidebar.button("Download CSV Report"):
        # Fetch the data again
        data = fetch_data("/filter-sales", params=params)
        if data and "results" in data and data["results"]:
            df = pd.DataFrame(data["results"])
            csv_file_path = "sales_dashboard_report.csv"
            df.to_csv(csv_file_path, index=False)

            # Provide download link
            with open(csv_file_path, "rb") as f:
                st.sidebar.download_button(
                    label="Download CSV Report",
                    data=f,
                    file_name=csv_file_path,
                    mime="text/csv"
                )





    # Fetch data from the API
    total_revenue = fetch_data("/kpis/total-revenue")
    total_profit = fetch_data("/kpis/total-sales-profit")
    profit_per_salesperson = fetch_data("/kpis/profit-per-salesperson")
    sales_per_country = fetch_data("/kpis/sales-per-country")
    product_sales_per_country = fetch_data("/kpis/product-sales-per-country", params={"start_date": start_date, "end_date": end_date})
    best_salesperson = fetch_data("/kpis/best-salesperson", params={"start_date": start_date, "end_date": end_date})
    most_sold_product = fetch_data("/kpis/most-sold-product", params={"start_date": start_date, "end_date": end_date})
    conversion_rate_data = fetch_data("/kpis/conversion-rate", params={"start_date": start_date, "end_date": end_date})
    product_data = fetch_data("/kpis/total-revenue-profit-product", params={"start_date": start_date, "end_date": end_date})
    website_visits_data = fetch_data("/kpis/total-website-visits", params={"start_date": start_date, "end_date": end_date})
    unique_visitors_data = fetch_data("/kpis/unique-visitors", params={"start_date": start_date, "end_date": end_date})
    demo_requests_data = fetch_data("/kpis/demo-requests", params={"start_date": start_date, "end_date": end_date})
    top_landing_pages_data = fetch_data("/kpis/top-landing-pages", {**params, "limit": 5})
    leads_generated_data = fetch_data("/kpis/leads-generated", params)
    leads_by_source_data = fetch_data("/kpis/leads-by-source", params)
    leads_by_status_data = fetch_data("/kpis/leads-by-status", params)
    lead_conversion_rate_data = fetch_data("/kpis/lead-conversion-rate", params)
    

    # Set the background color
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #101916;

            }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Set the font color
    st.markdown(
        """
        <style>
            .stApp {
                color: #CDD8EB;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container():
            st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color: #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>💰 Total Revenue</div>
                    <div style='font-size: 20px; font-weight: bold;'>{f"${total_revenue['total_revenue']:,}" if total_revenue else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
                
            )
           
    with col2:
        with st.container():
            st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color: #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>💵 Total Profit</div>
                    <div style='font-size: 20px; font-weight: bold;'>{f"${total_profit['total_sales_profit']:,}" if total_profit else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col3:
        with st.container():
            st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color: #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>👤 Best Salesperson</div>
                    <div style='font-size: 20px; font-weight: bold;'>{best_salesperson['salesperson'] if best_salesperson else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col4:
        with st.container():
            st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color: #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>🔥 Most Sold Product</div> 
                    <div style='font-size: 20px; font-weight: bold;'>{most_sold_product['product'] if most_sold_product else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Row 2
    col1, col2, col3 = st.columns(3)
    with col1:
     st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color: #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>🌐 Total Website Visits</div>
                    <div style='font-size: 20px; font-weight: bold;'>{f"{website_visits_data['total_website_visits']:,}" if website_visits_data and 'total_website_visits' in website_visits_data else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        st.markdown(
                f"""
                <div style='
                    border: 1px solid #061007;
                    border-radius: 1px;
                    padding: 1px;
                    margin-bottom: 8px;
                    background-color:   #061007;
                    color: #D1CFC9;
                    text-align: center;
                    width: 100%;
                '>
                    <div style='font-size: 14px; margin-bottom: 4px;'>📈 Unique Visitors</div>
                    <div style='font-size: 20px; font-weight: bold;'>{f"{unique_visitors_data['unique_visitors']:,}" if unique_visitors_data else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col3:
        st.markdown(
            f"""
            <div style='
                border: 1px solid #061007;
                border-radius: 1px;
                padding: 1px;
                margin-bottom: 8px;
                background-color:   #061007;
                color: #D1CFC9;
                text-align: center;
                width: 100%;
            '>
                <div style='font-size: 14px; margin-bottom: 4px;'>📊 Demo Requests</div>
                <div style='font-size: 20px; font-weight: bold;'>{f"{demo_requests_data['demo_requests']:,}" if demo_requests_data else "N/A"}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

#row 3
    col1, col2, col3 = st.columns(3)
    with col1:
     if top_landing_pages_data:
        with st.container():
         df_pages = pd.DataFrame(top_landing_pages_data["top_landing_pages"])
         fig = px.bar(df_pages, x="endpoint", y="visits", labels={"endpoint": "Page", "visits": "Visits"})
         fig.update_layout(
            paper_bgcolor="#061007",
            plot_bgcolor="#061007",
            font_color="#D1CFC9",
            height=285,
            margin=dict(l=35, r=35, t=35, b=0),
            xaxis_title="Landing Page",
            yaxis_title="Visits",
            xaxis_tickangle=-45,
            xaxis_tickmode="array",
            title="📈 Top Landing Pages",
        )
        st.plotly_chart(fig, use_container_width=True)
     else:
        st.info("No landing page data available for the selected period.")

    


    with col2:
        if sales_per_country:
            with st.container():
                df = pd.DataFrame(sales_per_country["sales_per_country"])
                fig = px.choropleth(
                    df,
                    locations="country",
                    locationmode="country names",
                    color="total_revenue",
                    template="none",  # disable default styles
                    color_continuous_scale=px.colors.sequential.Plasma,
                    scope="world"
                )
                fig.update_layout(
                    geo=dict(
                        bgcolor='rgba(0,0,0,0)',  # this is key
                        showframe=False,
                        showcoastlines=True
                    ),
                    paper_bgcolor="#061007",
                    plot_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False,
                    showlegend=False,
                    height=285,
                    margin=dict(l=5, r=5, t=0, b=0),
                    font_color="#D1CFC9"
                )
                st.plotly_chart(fig, use_container_width=True)

    with col3:
        if lead_conversion_rate_data and isinstance(lead_conversion_rate_data.get("lead_conversion_rate"), (int, float, float)):
         import plotly.graph_objects as go
         lead_conversion_rate = lead_conversion_rate_data["lead_conversion_rate"]
         fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            
            value=lead_conversion_rate,
            number={'suffix': "%"},
            number_font_size=50,
            title={'text': "Conversion Rate"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "mediumseagreen"},
                   'steps': [
                       {'range': [0, 40], 'color': "#1e202c"},
                       {'range': [40, 70], 'color': "#60519b"},
                       {'range': [70, 100], 'color': "#bfc0d1"}
                   ]}
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#061007",
            plot_bgcolor="#061007",
            font_color="#D1CFC9",
            height=285,
            margin=dict(l=35, r=35, t=15, b=0)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)




    # Row 4
    col1, col2, col3 = st.columns(3)
    with col1:
     if profit_per_salesperson:
        with st.container():
            df = pd.DataFrame(profit_per_salesperson["profit_per_salesperson"])
            df = df.sort_values("total_profit", ascending=False)  # Funnel needs descending order
            fig = px.funnel(
                df,
                y="salesperson",
                x="total_profit",
                title="💰 Profit per Salesperson",
                template="plotly_dark",
            )
            fig.update_layout(
                paper_bgcolor="#061007",
                plot_bgcolor="#061007",
                height=285,
                font_color="#D1CFC9",
                margin=dict(l=5, r=5, t=35, b=0),
                showlegend=False,
                
            )
            st.plotly_chart(fig, use_container_width=True)

    
    with col2:
     if leads_by_source_data:
        df_source = pd.DataFrame(leads_by_source_data["leads_by_source"])
        fig_source = px.pie(df_source, names="lead_source", values="count", hole=0.45, title="Leads by Source",
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_source.update_traces(marker_line_width=1.5, marker_line_color="black", showlegend=False)
        fig_source.update_layout(paper_bgcolor="#061007", plot_bgcolor="#061007", height=285, font_color="#D1CFC9", 
                                 margin=dict(l=35, r=35, t=30, b=0))
        st.plotly_chart(fig_source, use_container_width=True)
     else:
        st.info("No data for Leads by Source in this period.")

    with col3:
        if product_sales_per_country and "product_sales_per_country" in product_sales_per_country:
            with st.container():
                df = pd.DataFrame(product_sales_per_country["product_sales_per_country"])
                if not df.empty:
                    fig = px.bar(df, x="country", y="total_revenue", color="product", title="📦 Product Sales by Country", template="plotly_dark", barmode="stack")
                    fig.update_layout(showlegend=False, paper_bgcolor="#061007", plot_bgcolor="#061007", height=285, font_color="#D1CFC9", 
                                  margin=dict(l=25, r=25, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)

    # Row 5
    col1, col2 = st.columns(2)
    with col1:
        if product_data:
            with st.container():
                df = pd.DataFrame(product_data)
                fig = px.bar(df, x="product", y=["total_revenue", "total_profit"], barmode="group", template="plotly_dark", title="📦 Product Revenue and Profit")
                fig.update_layout(showlegend=False, paper_bgcolor="#061007", plot_bgcolor="#061007", height=310, font_color="#D1CFC9",
                                  margin=dict(l=5, r=5, t=35, b=0), xaxis_title="Products")
                st.plotly_chart(fig, use_container_width=True)
    with col2:
     if leads_by_status_data:
        df_status = pd.DataFrame(leads_by_status_data["leads_by_status"])
        fig_funnel = go.Figure(go.Funnel(
            y=df_status["lead_status"],
            x=df_status["count"],
            textinfo="value+percent previous",
            marker={"color": ["#3498db", "#f1c40f", "#2ecc71", "#e74c3c"]}
        ))
        fig_funnel.update_layout(title="Leads by Status (Funnel)", height=310,
                                paper_bgcolor="#061007",
                                plot_bgcolor="#061007",
                                font_color="#D1CFC9",
                                margin=dict(l=5, r=5, t=35, b=0))
        st.plotly_chart(fig_funnel, use_container_width=True)
     else:
        st.info("No data for Leads by Status in this period.")

# --- Timeline (Leads Generated Over Time): Area Chart ---
def render_leads_by_day(params):
    leads_by_day = fetch_data("/kpis/leads-by-day", params)
    leads_by_day = leads_by_day.get("leads_by_day", []) if leads_by_day else []
    if leads_by_day:
        df_day = pd.DataFrame(leads_by_day)
        fig_area = px.area(df_day, x="date", y="count", title="Leads Generated Over Time",
                           markers=True, line_shape="spline", color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No data for Leads per Day in this period.")

# --- Download PDF Report ---
# Allow user to select which metrics to export


# Auto-refresh every 10 seconds
while True:
    render_dashboard()
    # Use the same params as in render_dashboard
    params = {}
    # Optionally, set default params or retrieve from session state if needed
    render_leads_by_day(params)
    time.sleep(10)
    st.rerun()
