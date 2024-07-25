import streamlit as st
import scraplc as slc
from lrextract import *
import google.generativeai as genai
import os

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

lc = slc.LeetcodeScraper()

st.title("Roast your leetcode profile !")
st.write("Enter a LeetCode username and click the button to process.")

user_name = st.text_input('Enter your leetcode username')


@st.cache_resource
def process_leetcode_username(user_name):
    try:
        data = lc.scrape_user_profile(user_name)
        

        max_lang = get_max_solved_language(data['languageStats'])
        cbatch_rank = extract_contest_badge_and_ranking(data['userPublicProfile'])
        scstreak = extract_todays_solved_count(data['userProfileCalendar'])
        coninfo =extract_contest_info(data['userContestRankingInfo']['userContestRankingHistory'])

        leastcat = find_least_solved_skill(data['skillStats']['matchedUser']['tagProblemCounts'])

        prompt = gen_prompt(max_lang, cbatch_rank, scstreak, coninfo, leastcat)

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)

        dispresp = response.text.strip()
        st.subheader('Roast : ')
        st.caption("beta offend na ho jana lol")
        st.markdown(dispresp)
    except Exception as e:
        st.error(e)

    



if st.button("Process"):
    if user_name:
        
        result = process_leetcode_username(user_name)
        
    else:
        st.error("Please enter a username.")
