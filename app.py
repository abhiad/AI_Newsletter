import streamlit as st
import requests
import re
from database import (
    save_user,
    get_subscribed_users,
    is_user_subscribed,
    update_subscription_status,
    init_db
)
import smtplib
from email.message import EmailMessage
 
import schedule
import time
from threading import Thread
 
# Initialize the database tables
init_db()
 
# --- Helper Functions ---
#def is_valid_email(email):
#    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
 
# --- Helper Functions ---
# def is_valid_email(email):
#     pattern = r"^[a-zA-Z0-9._%+-]+@volkswagen\.co\.in$"
#     return re.match(pattern, email)


# --- Helper Functions ---
def is_valid_email(email):
   return re.match(r"[^@]+@[^@]+\.[^@]+", email)
 
def get_news(api_key, categories):
    url = 'https://newsapi.org/v2/everything'
    query = " OR ".join(categories)  # Combine selected categories with OR for filtering
    params = {
        'apiKey': api_key,
        'q': query,
        'language': 'en',
        'pageSize': 12,
        'sortBy': 'publishedAt'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"❌ API Error: {response.status_code}")
        return []
    return response.json().get('articles', [])
 
 
def send_email(receiver_email, news_articles, categories):
    sender_email = "abhayaiagent@gmail.com"
    sender_password = "exksejtmqfoeuecf"  # App-specific password
 
    category_list = ", ".join(categories)
    html_content = f"""
    <html>
    <head>
        <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; }}
        h2 {{ text-align: center; color: #333; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 900px; margin: 0 auto; }}
        .news-card {{ 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            margin: 10px; 
            padding: 15px; 
            background-color: #fff; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            height: 450px; 
            width: 280px;
            position: relative;
        }}
        .news-card h3 {{ font-size: 16px; margin: 0 0 10px 0; color: #333; }}
        .news-card .content {{ 
            height: 340px;
            overflow: hidden;
        }}
        .news-card p {{ font-size: 14px; color: #555; margin-bottom: 10px; }}
        .news-card .card-footer {{ 
            position: absolute;
            bottom: 15px;
            left: 15px;
            right: 15px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}
        .news-card .meta {{ font-size: 12px; color: #888; margin-bottom: 12px; }}
        .news-card a {{ 
            display: inline-block; 
            padding: 8px 15px; 
            background-color: #007BFF; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px; 
            font-weight: bold;
            float: right;
        }}
        .news-card img {{ width: 100%; height: 150px; object-fit: cover; border-radius: 4px; margin-bottom: 10px; }}
        .unsubscribe {{ text-align: center; margin-top: 30px; padding: 10px; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <h2>Tech News Digest on {category_list}</h2>
        <table cellspacing="0" cellpadding="0" border="0" align="center">
    """
 
    # Process articles in groups of 3 (3 columns per row)
    for i in range(0, len(news_articles), 3):
        html_content += '<tr>'
        
        # For each row, add up to 3 cells
        for j in range(3):
            if i + j < len(news_articles):
                article = news_articles[i + j]
                title = article['title']
                desc = article.get('description', 'No description available.')[:150] + "..." if article.get('description') else "No description available."
                url = article['url']
                source = article['source']['name'] if article.get('source') else "Unknown"
                date = article.get('publishedAt', '')[:10] if article.get('publishedAt') else "Unknown Date"
                image_url = article.get('urlToImage', '')
                
                # Create a card in each cell with fixed footer
                html_content += f"""
                <td width="33%" style="vertical-align: top;">
                    <div class="news-card">
                        <div class="content">
                            {f'<img src="{image_url}" alt="{title}" />' if image_url else ''}
                            <h3>{title}</h3>
                            <p>{desc}</p>
                        </div>
                        <div class="card-footer">
                            <p class="meta">Source: {source} | Date: {date}</p>
                            <a href="{url}" target="_blank">Read More</a>
                        </div>
                    </div>
                </td>
                """
            else:
                # Empty cell if fewer than 3 articles remain
                html_content += '<td width="33%"></td>'
                
        html_content += '</tr>'
 
    html_content += f"""
        </table>
        <div class="unsubscribe">
            If you wish to unsubscribe from this newsletter, <a href="http://example.com/unsubscribe?email={receiver_email}">click here</a>.
        </div>
    </body>
    </html>
    """
 
    msg = EmailMessage()
    msg['Subject'] = f"Your Tech News Digest on {category_list}"
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
 
# Function to send newsletters to all subscribed users
def send_weekly_newsletter():
    api_key = "0a6927cd3408421aa01e13e3b6976cd7"
    users = get_subscribed_users()
    for user in users:
        email = user['email']
        categories = user['categories']
        if categories:
            articles = get_news(api_key, categories)
            if articles:
                send_email(email, articles, categories)
 
# Schedule the newsletter to be sent every Friday at 9 AM
schedule.every().friday.at("09:00").do(send_weekly_newsletter)
 
# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
 
# Start the scheduler in a separate thread
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
 
# --- Streamlit UI ---
st.set_page_config(page_title="Tech Newsletter", page_icon="📰")
st.title("📰 Tech Weekly Newsletter")
 
# Sidebar
st.sidebar.header("📧 Sign In")
user_email = st.sidebar.text_input("Enter your email:")
categories = [
    "AI", "Machine Learning", "Data Science", "Deep Learning", "Neural Networks",
    "Natural Language Processing", "Computer Vision", "Robotics", "Big Data", "Analytics",
    "Cloud Computing", "Edge AI", "Automation", "Chatbots", "Artificial General Intelligence",
    "AI Ethics", "Generative AI", "Tech Startups", "Quantum Computing", "Internet of Things",
    "Cybersecurity", "DevOps", "Software Engineering", "Programming", "Blockchain", "Web3",
    "Augmented Reality", "Virtual Reality", "Fintech", "Digital Transformation",
    "5G Technology", "Mobile Technology", "Operating Systems",
    "Distributed Systems", "Open Source", "Tech Innovation", "Computing Hardware",
    "Tech Policy", "Data Privacy", "Data Engineering", "API Development"
]
selected_categories = st.sidebar.multiselect("Select your preferred categories:", categories)
authenticated = False
 
if user_email:
    if is_valid_email(user_email):
        subscribed = is_user_subscribed(user_email)
 
        if subscribed:
            st.sidebar.success("✅ Subscribed")
            if st.sidebar.button("❌ Unsubscribe"):
                update_subscription_status(user_email, False)
                st.sidebar.warning("Unsubscribed")
                subscribed = False
        else:
            if st.sidebar.button("✅ Subscribe"):
                save_user(user_email, True)
                subscribed = True
                st.sidebar.success("Subscribed successfully!")
 
                # Automatically send the newsletter upon subscription
                api_key = "0a6927cd3408421aa01e13e3b6976cd7"
                if selected_categories:
                    articles = get_news(api_key, selected_categories)
                    if articles:
                        if send_email(user_email, articles, selected_categories):
                            st.toast("✅ Newsletter sent to your email!")  # Use st.toast if available
                            st.sidebar.success("✅ Newsletter sent to your email!")
                else:
                    st.sidebar.error("❌ Please select at least one category.")
 
        authenticated = True
    else:
        st.sidebar.error("❌ Invalid email address.")
else:
    st.sidebar.info("Enter a valid email to access news")
 
# Main content
if authenticated:
    api_key = "0a6927cd3408421aa01e13e3b6976cd7"
 
    if api_key and selected_categories:
        articles = get_news(api_key, selected_categories)
        if articles:
            for article in articles:
                st.markdown(f"#### {article['title']}")
                st.write(article.get('description', 'No description available.'))
                st.write(f"**Source:** {article['source']['name']} | **Date:** {article['publishedAt'][:10]}")
                st.markdown(f"[Read more →]({article['url']})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], width=300)
                st.markdown("---")
        else:
            st.error("❌ No articles found for the selected categories.")
 
