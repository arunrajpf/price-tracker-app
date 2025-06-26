import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === App Email Config ===
FROM_EMAIL = "arunrajpf@gmail.com"  # your Gmail address
FROM_PASSWORD = "your-app-password-here"  # your Gmail app password (not regular password)

st.set_page_config(page_title="Amazon Price Tracker", layout="centered")
st.title("🛒 Amazon Price Tracker")

# UI inputs
url = st.text_input("🔗 Enter Amazon Product URL")
target_price = st.number_input("🎯 Enter Your Target Price (₹)", min_value=0)
recipient_email = st.text_input("📧 Enter Your Email to Get Alerts")
send_email = st.checkbox("📩 Send me an email alert if price drops")

# Function to fetch product price from Amazon
def get_amazon_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        title_tag = soup.find(id="productTitle")
        if not title_tag:
            return None, None

        title = title_tag.get_text().strip()
        price = None

        # Try several possible price locations
        selectors = [
            ("span", {"class": "a-price-whole"}),
            ("span", {"id": "priceblock_dealprice"}),
            ("span", {"id": "priceblock_ourprice"}),
            ("span", {"id": "priceblock_saleprice"})
        ]

        for tag, attrs in selectors:
            price_tag = soup.find(tag, attrs)
            if price_tag:
                price_str = price_tag.get_text().strip().replace(",", "")
                price = int(re.sub(r"[^\d]", "", price_str))
                break

        return title, price if price else None

    except Exception as e:
        print(f"Error fetching price: {e}")
        return None, None

# Email sender
def send_email_alert(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        st.success("📧 Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

# Main action
if st.button("Check Price"):
    if url and target_price > 0:
        title, price = get_amazon_price(url)
        if title and price:
            st.markdown(f"### 🛍️ {title}")
            st.markdown(f"**💰 Current Price:** ₹{price}")
            if price <= target_price:
                st.success("🎉 Hurray! Price has dropped below your target!")
                if send_email and recipient_email:
                    body = f"""🎯 Price Drop Alert!

Product: {title}
Current Price: ₹{price}
Target Price: ₹{target_price}

Link: {url}"""
                    send_email_alert(recipient_email, "🔥 Amazon Price Drop Alert!", body)
            else:
                st.info("📈 Price is still above your target.")
        else:
            st.error("⚠️ Could not fetch product price. Check URL.")
    else:
        st.warning("Please fill in all fields.")
