### For detailed project description and changes, please refer to "SI 507 - Final project proposal"

1. Data source
1) Fusion API:
- Please put your API keys in the "secrets.py" file
- Example of content in secrest.py:
  (PI_KEY = "")

2) https://www.allrecipes.com/
- No API key required
- Use getRecipeCategory() and getMostMade() in the final_proj.py file to crawl the website

2. Code structure:
1) final_proj.py
- This is the Model file
- First part of the file is about searching Restaurant (via Yelp API), including: i) cache and ii) getYelp(): retrieve data from Yelp based on search keywords
- Second part of the file is about Database, including: i) create the database/table for the new user, ii) saveSearch(): save the search kewword, and iii) returnHistory(): return a user's search history
- Last part of the file is about searching Recipes (via crawling allrecipes website), including: i) getRecipeCategory(): list all the categories and sub-categories of recipes, and ii) getMostMade(): display the most made recipe of the day upon user's choice.

2) app.py
- This is the file contains all the flasks
- The structure of the "website" is as below
* Homepage (index) --> choose to search for restaurants (restaurants.html) or for recipes (recipecategory.html)
* Main page for restaurant --> search with keyword (searchrestaurant.html) or display history (history.html)
* Result page of search (result.html) --> show results on the map (plotly) or see reviews (review.html)
* Main page for recipes (recipecategory.html) --> choose a category to display most made recipes of the day (mostmade.html)

3) all the templates (html files) are in the templates folder

4) each html file has a linked css file in the static folder

5) I also provided one unit testing (file_proj_test.py)

3. User guide:
1) Activate a virtual environment
2) Install flask
3) install requirements.txt
4) type "python app.py" in the command line
5) Go to 127.0.0.1
