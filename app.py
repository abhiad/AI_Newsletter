import streamlit as st
import requests
import re
import base64
from database import (
    save_user,
    get_subscribed_users,
    is_user_subscribed,
    update_subscription_status,
)
import smtplib
from email.message import EmailMessage


# --- Helper Functions ---
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def get_news(api_key):
    url = 'https://newsapi.org/v2/everything'
    topics = "AI, Machine Learning, Data Science"
    params = {
        'apiKey': api_key,
        'q': topics,
        'language': 'en',
        'pageSize': 10,
        'sortBy': 'publishedAt'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"❌ API Error: {response.status_code}")
        return []
    return response.json().get('articles', [])


def send_email(receiver_email, news_articles, topic):
    sender_email = "abhayaiagent@gmail.com"
    sender_password = "exksejtmqfoeuecf"  # App-specific password

    # Encode email for secure unsubscribe link
    encoded_email = base64.urlsafe_b64encode(receiver_email.encode()).decode()
    unsubscribe_url = f" http://localhost:8501/?action=unsubscribe&email={encoded_email}"

    # Generate HTML content for the email
    html_content = f"""
    <html>
    <head>
        <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        h2 {{ text-align: center; }}
        .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); width: 90%; max-width: 500px; margin: 0 auto; }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 5px; }}
        .card h3 {{ font-size: 16px; margin: 10px 0; }}
        .card p {{ font-size: 14px; color: #555; }}
        .card .meta {{ font-size: 12px; color: #888; }}
        .card a {{ display: inline-block; margin-top: 10px; padding: 8px 12px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; }}
        .unsubscribe {{ text-align: center; margin-top: 20px; font-size: 12px; color: #888; }}
        .unsubscribe a {{ color: #007BFF; }}
        </style>
    </head>
    <body>
        <h2>Tech News Digest on {topic}</h2>
        <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center" style="max-width: 650px;">
    """

    # Process articles one by one in a single column layout
    for i in range(min(10, len(news_articles))):
        article = news_articles[i]
        title = article['title']
        desc = article['description'] or "No description available."
        url = article['url']
        source = article['source']['name'] if article['source'] else "Unknown"
        date = article['publishedAt'][:10] if 'publishedAt' in article else "Unknown Date"
        image_url = article.get('urlToImage', '')

        html_content += '<tr><td style="padding: 15px;">'
        html_content += f"""
        <div class="card">
            <img src="{image_url}" alt="News Image" onerror="this.src='https://via.placeholder.com/600x300?text=No+Image'" style="width: 100%; height: 200px; object-fit: cover; border-radius: 5px;">
            <h3>{title}</h3>
            <p>{desc}</p>
            <p class="meta">Source: {source} | Date: {date}</p>
            <a href="{url}">Read More</a>
        </div>
        """
        html_content += '</td></tr>'

    html_content += f"""
        </table>
        <p class="unsubscribe">
            If you wish to unsubscribe from this newsletter, <a href="{unsubscribe_url}">click here</a>.
        </p>
    </body>
    </html>
    """

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = f"Your Tech News Digest on {topic}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Your email client does not support HTML emails. Please view this email in a browser.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False


# --- Streamlit UI ---
st.set_page_config(page_title="Tech Newsletter", page_icon="📰")

# Handle unsubscribe requests from email links
query_params = st.query_params
if "action" in query_params and query_params["action"][0] == "unsubscribe" and "email" in query_params:
    try:
        # Decode the email from the parameter
        encoded_email = query_params["email"][0]
        email = base64.urlsafe_b64decode(encoded_email.encode()).decode()

        # Check if the user exists and is currently subscribed
        if is_user_subscribed(email):
            # Update subscription status using existing function
            if update_subscription_status(email, False):
                st.success(f"✅ You have been successfully unsubscribed from our newsletter.")
            else:
                st.error("❌ Unable to process your request. Please try again later.")
        else:
            st.info("📧 This email is not currently subscribed to our newsletter.")

        # Stop further execution of the app
        st.stop()
    except Exception as e:
        st.error(f"❌ Invalid unsubscribe link: {str(e)}")

st.title("📰 AI/Tech Weekly Newsletter")
st.subheader("Curated updates on the latest in technology")

# Sidebar
st.sidebar.header("📧 Sign In")
user_email = st.sidebar.text_input("Enter your email:")
authenticated = False

if user_email and is_valid_email(user_email):
    subscribed = is_user_subscribed(user_email)

    # Toggle subscription
    if subscribed:
        st.sidebar.success("✅ Subscribed")
        st.sidebar.success("Already Subscribed!")
    else:
        if st.sidebar.button("✅ Subscribe"):
            save_user(user_email, True)
            subscribed = True
            st.sidebar.success("Subscribed successfully!")

    authenticated = True
else:
    st.sidebar.info("Enter a valid email to access news")

# Main content
if authenticated:
    api_key = "0a6927cd3408421aa01e13e3b6976cd7"

    if api_key:
        articles = get_news(api_key)
        if articles:
            topic = "AI, Machine Learning, Data Science"
            st.write(f"### 📰 Latest News on {topic}")
            for article in articles:
                st.markdown(f"#### {article['title']}")
                st.write(article.get('description', 'No description available.'))
                st.write(f"**Source:** {article['source']['name']} | **Date:** {article['publishedAt'][:10]}")
                st.markdown(f"[Read more →]({article['url']})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], width=300)
                st.markdown("---")

            if st.button("✉️ Send Newsletter to Subscribers"):
                users = get_subscribed_users()
                count = 0
                for email in users:
                    if send_email(email, articles, topic):
                        count += 1
                st.success(f"✅ Sent to {count} subscribers.")
