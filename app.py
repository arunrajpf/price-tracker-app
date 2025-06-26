import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Amazon Price Tracker", layout="centered")

st.title("🛒 Amazon Price Tracker")

url = st.text_input("🔗 Enter Amazon Product URL")
target_price = st.number_input("🎯 Enter Your Target Price (₹)", min_value=0)

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

if st.button("Check Price"):
    if url and target_price > 0:
        title, price = get_amazon_price(url)
        if title:
            st.markdown(f"### 🛍️ {title}")
            st.markdown(f"**💰 Current Price:** ₹{price}")
            if price <= target_price:
                st.success("🎉 Hurray! Price has dropped below your target!")
            else:
                st.info("📈 Price is still above your target.")
        else:
            st.error("⚠️ Could not fetch price. Please check the URL.")
    else:
        st.warning("Please enter a valid URL and price.")
