
import datetime
import json


def get_max_solved_language(profile_data):
    language_data = profile_data['matchedUser']['languageProblemCount']
    
    if not language_data:
        return "No data available", 0
    
    # Find the language with the maximum problems solved
    max_solved = max(language_data, key=lambda x: x['problemsSolved'])
    max_language_name = max_solved['languageName']
    max_problems_solved = max_solved['problemsSolved']
    
    # Calculate the total number of problems solved
    total_solved = sum(lang['problemsSolved'] for lang in language_data)
    
    return max_language_name, max_problems_solved, total_solved


def extract_contest_badge_and_ranking(profile_data):
    contest_badge = profile_data['matchedUser'].get('contestBadge')
    ranking = profile_data['matchedUser']['profile'].get('ranking')

    if contest_badge is None:
      contest_badge = "No contest badge"
  
      return contest_badge, ranking
    else:
      return (ranking,)
    

def extract_todays_solved_count(profile_data):
    submission_calendar_str = profile_data['matchedUser']['userCalendar']['submissionCalendar']
    submission_calendar = json.loads(submission_calendar_str)
    
    today = datetime.datetime.now().date()
    start_of_today = datetime.datetime.combine(today, datetime.time.min)
    today_timestamp = int(start_of_today.timestamp())
    
    today_solved_count = submission_calendar.get(str(today_timestamp), 0)
    
    return today_solved_count, profile_data['matchedUser']['userCalendar']['streak']


def extract_contest_info(contests):
    participated = False
    highest_ranking = float('inf')  # Initialize to a high number to find the minimum
    
    # Iterate through contests to determine participation and highest ranking
    for contest in contests:
        if contest['attended']:
            participated = True
            if contest['ranking'] < highest_ranking:
                highest_ranking = contest['ranking']
    
    # If not participated, return (False, 0, 0)
    if not participated:
        return (False, 0, 0)
    
    # Determine the latest two contests
    if len(contests) < 2:
        return (highest_ranking, 0)  # Not enough data to calculate rank drop
    
    # Extract ranking from the last two contests
    latest_two = contests[-2:]
    
    # Ensure that we have data for the last two contests
    if len(latest_two) < 2:
        return (highest_ranking, 0)
    
    last_ranking = latest_two[0]['ranking']
    second_last_ranking = latest_two[1]['ranking']
    contest_names = [latest_two[1]['contest']['title'], latest_two[0]['contest']['title']]

    last_rating = latest_two[0]['rating']
    # Calculate rank drop
    rank_drop = second_last_ranking - last_ranking
    
    return (highest_ranking, rank_drop, contest_names[0], contest_names[1], last_rating)


def find_least_solved_skill(skill_stats):
    advanced_skills = skill_stats.get('advanced', [])
    intermediate_skills = skill_stats.get('intermediate', [])
    
    all_skills = advanced_skills + intermediate_skills
    
    if not all_skills:
        return "No skills data available"
    
    # Initialize the skill with the least number of problems solved
    least_solved_skill = min(all_skills, key=lambda x: x['problemsSolved'])
    
    # Determine the category of the skill
    if least_solved_skill in advanced_skills:
        category = 'Advanced'
    else:
        category = 'Intermediate'
    
    return least_solved_skill['tagName'], least_solved_skill['problemsSolved'], category

def gen_prompt(max_lang, cbatch_rank, scstreak, coninfo, leastcat):

  if len(cbatch_rank)==1:
    batch='yes'
    rank=cbatch_rank[0]
  else:
    batch='no'
    rank=cbatch_rank[1]

  if len(coninfo)<5:
    hrank, rdrop, c1, c2, crate = 0, 0, 0, 0, 0
  else:
    hrank, rdrop, c1, c2, crate = coninfo

  today_sc, max_streak = scstreak

  if len(max_lang)<3:
    max_lang, lang_sc, total_sc = 0, 0, 0
  else:
    max_lang, lang_sc, total_sc = max_lang

  if isinstance(leastcat, str):
    least_skl, sc, scategory = 0, 0, 0
  else:
    least_skl, sc, scategory = leastcat

  prompt = f'''
  You are a pro hindi roaster. Generate a roast based on the following leetcode(competetive coding platform) user profile data. Don't mention translation.

  1. **Most Used Language**: {max_lang}, solved {lang_sc} problems, out of a total of {total_sc} solved problems.
  2. **Contest Badge Presence**: {batch}, Highest Ranking in Contest: {hrank}.
  3. **World Ranking**: {rank}.
  4. **Today's Solve Count**: {today_sc}.
  5. **Max Streak**: {max_streak}.
  6. **Contest Details**:
    - **Contest 1**: {c1}
    - **Contest 2**: {c2}
    - **Contest Rating**: {crate}
    - **Rank Drop**: {rdrop}
  7. **Least Solved Skill**: An {scategory} skill named {least_skl}, with {sc} problems solved in that skill.

  **Instructions for Generating Roast:**

  - **For Low Stats Profiles**: If the user’s statistics indicate low performance (e.g., very high world ranking, minimal problems solved, no contest participation), create a roast that is harsh and points out the low performance humorously.

  - **For High Stats Profiles**: If the user’s statistics indicate high performance (e.g., low world ranking, significant problems solved, frequent contest participation, an advanced skill), create a roast with a sarcastic tone that highlights the achievements in a playful and exaggerated manner.

  Use the instructions provided above to craft a roast that fits the performance level of the user. Provide the roast only in hinglish text.
  Focus on making the roast more harsh and funny to entertain. Roast must atleast be 150 words or above. Don't write translations, just the roast!

  '''

  return prompt