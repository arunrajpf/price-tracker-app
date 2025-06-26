import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Central App Email Config ===
FROM_EMAIL = "arunrajpf@gmail.com"  # your app's sender email
FROM_PASSWORD = "your-app-password-here"  # your Gmail app password

st.set_page_config(page_title="Amazon Price Tracker", layout="centered")
st.title("🛒 Amazon Price Tracker")

url = st.text_input("🔗 Enter Amazon Product URL")
target_price = st.number_input("🎯 Enter Your Target Price (₹)", min_value=0)
recipient_email = st.text_input("📧 Enter Your Email to Get Alerts")
send_email = st.checkbox("📩 Send me an email alert if price drops")

def get_amazon_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        title = soup.find(id="productTitle").get_text().strip()
        price_tag = soup.find("span", {"class": "a-price-whole"})
        if not price_tag:
            return None, None
        price = int(re.sub(r"[^\d]", "", price_tag.get_text()))
        return title, price
    except Exception as e:
        return None, None

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

if st.button("Check Price"):
    if url and target_price > 0:
        title, price = get_amazon_price(url)
        if title:
            st.markdown(f"### 🛍️ {title}")
            st.markdown(f"**💰 Current Price:** ₹{price}")
            if price <= target_price:
                st.success("🎉 Hurray! Price has dropped below your target!")
                if send_email and recipient_email:
                    message = f"""🎯 Price Drop Alert!

Product: {title}
Current Price: ₹{price}
Target Price: ₹{target_price}

Link: {url}"""
                    send_email_alert(recipient_email, "🔥 Amazon Price Drop Alert!", message)
            else:
                st.info("📈 Price is still above your target.")
        else:
            st.error("⚠️ Could not fetch product price. Check URL.")
    else:
        st.warning("Please fill all fields properly.")
