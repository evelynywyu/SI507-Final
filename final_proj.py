import requests
import json
import secrets
from requests_oauthlib import OAuth1
import sqlite3


# API KEYS
API_token = secrets.API_KEY
header = {'authorization': "Bearer " + API_token}


### YELP ###

# Caching data

CACHE_FNAME = 'cache_yelp.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params_d, headers = header):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)


def make_request_using_cache(baseurl, params, headers = header):
    global header
    unique_ident = params_unique_combination(baseurl,params)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params, headers = header)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

# get data from Yelp API

def getYelp(search_term, location = "Ann Arbor", sort_rule = "rating"):
    global API_token
    baseurl = "https://api.yelp.com/v3/businesses/search"
    params = {}
    params['term'] = search_term
    params['location'] = location
    params['sort_by'] = sort_rule
    # params['limit'] = 10
    # params["authorization"] = "Bearer " + API_token
    header = {'authorization': "Bearer " + API_token}

    # response = requests.get(baseurl,params=params, headers = header).text
    response = make_request_using_cache(baseurl,params = params)
    # result = json.loads(response)
    # print(result)

    aggregate_dic = {}

    result_list = []
    for item in response["businesses"]:
        # print(item["name"])
        aggregate_dic[item["name"]] = {}   # create a dic for each business
        aggregate_dic[item["name"]]["name"] = item["name"]
        aggregate_dic[item["name"]]["rating"] = item["rating"]
        aggregate_dic[item["name"]]["lon"] = item["coordinates"]["longitude"]
        aggregate_dic[item["name"]]["lan"] = item["coordinates"]["latitude"]
        result_list.append(aggregate_dic[item["name"]])

    return result_list


### Store search keyword in the database

# Create a database when the user first initiates the program

DBName = 'search.db'

conn = sqlite3.connect(DBName)
cur = conn.cursor()

statement = '''
    DROP TABLE IF EXISTS 'History'
'''
cur.execute(statement)
conn.commit()


# ***** Check ******
# How to create table only at the first time the user initiates the program???
# *****************

create_table_statement = '''
    CREATE TABLE 'History' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'SearchWord' TEXT NOT NULL,
    'NumberOfSearch' INTEGER NOT NULL,
    'LastSearchOn' TEXT NOT NULL
    );
'''
cur.execute(create_table_statement)
conn.commit()

# Save search keyword
def saveSearch(keyword):

    global DBName

    conn = sqlite3.connect(DBName)
    cur = conn.cursor()

    statement = '''
        SELECT SearchWord, NumberOfSearch
        FROM History
    '''

    cur.execute(statement)
    print("This is history")
    print(cur)


    current_dict = {}
    current_list = []
    keyword_list = []
    for row in cur:
        keyword_list.append(row[0])
        current_dict[row[0]] = {}
        current_dict[row[0]]["search_term"] = row[0]
        current_dict[row[0]]["count"] = row[1]
        current_list.append(current_dict[row[0]])

    # print("Current dict:")
    # print(current_dict)
    #
    # print("current_list:")
    # print(current_list)
    #
    # print("keyword_list:")
    # print(keyword_list)

    if keyword not in keyword_list:
        count = 1
        statement = '''
            INSERT INTO 'History' ('Id', 'SearchWord', 'NumberOfSearch', 'LastSearchOn')
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        '''
        insersion = (None, keyword, count, )
        cur.execute(statement, insersion)
        conn.commit()

    else:
        count = str(int(current_dict[keyword]["count"]) + 1)
        statement = '''
            UPDATE History
            SET NumberOfSearch = ?, LastSearchOn = CURRENT_TIMESTAMP
            WHERE SearchWord = ?
        '''
        insersion = (count, keyword)
        cur.execute(statement, insersion)
        conn.commit()

        # if row[0] != None:
        #     if keyword != row[0]:
        #         count = 1
        #         statement = '''
        #             INSERT INTO 'History' ('Id', 'SearchWord', 'NumberOfSearch', 'LastSearchOn')
        #             VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        #         '''
        #         insersion = (None, keyword, count, )
        #
        #         cur.execute(statement, insersion)
        #
        #     else:
        #         count = str(int(row[1]) + 1)
        #         statement = '''
        #             UPDATE History
        #             SET NumberOfSearch = ?, LastSearchOn = CURRENT_TIMESTAMP
        #             WHERE SearchWord = ?
        #         '''
        #         insersion = (count, keyword)
        #         cur.execute(statement, insersion)
        #
        # else:
        #     count = 1
        #     statement = '''
        #         INSERT INTO 'History' ('Id', 'SearchWord', 'NumberOfSearch', 'LastSearchOn')
        #         VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        #     '''
        #     insersion = (None, keyword, count, )
        #
        #     cur.execute(statement, insersion)



    conn.close()

# Return the history

def returnHistory():
    global DBName

    conn = sqlite3.connect(DBName)
    cur = conn.cursor()

    statement = '''
        SELECT SearchWord, NumberOfSearch
        FROM History
        ORDER BY NumberOfSearch DESC
        LIMIT 10
    '''

    cur.execute(statement)

    print("Below are the top 10 keyword you searched in the past: ")
    count = 0
    for row in cur:
        count += 1
        print(count, ") ", row[0], " (the number of search: )", row[1])

    conn.close()


### Interactive command

# help text
instruction_message = '''
    This is instruction messge (To be modified)
'''

initial_command = '''
    *** Welcome to Evelyn's 507 final project! ***

    Please enter a command:

    <search keyword> : Search restaurants based on the keyword
    <trending> : Check out what's the trending search in the past month
    <help> : Read the program instruction
    <exit> : Exit the program

'''

followup_command = '''

    Please enter a command:

    <map> : Show the 10 restaurants on a map
    <reivew restaurants> : See the 10 most recent reviews of the selected restaurant
    <opentable> : Check which restaurants are available for reservation via Open Table
    <search keyword> : Search other restaurants based on the keyword
    <help> : Read the program instruction
    <trending> : Check out what's the trending search in the past month

'''

# function for the follow-up actions (write this function first, because the initial action will use this function)
def secondRun():

    global followup_command

    while True:

        print(followup_command)

        user_input = input("Please enter a command usting the illustrated format.")

        if len(user_input.split()) > 1:
            command = user_input.split()[0]
        else:
            command = user_input

        if command == 'exit':
            print('Exiting the program. Thank you and bye!')
            return


        elif command == 'help':
            print(instruction_message)

        elif command == 'search':
            result = getYelp(user_input.split()[1])
            print("The 10 top ranking restaurants are:")
            num = 0
            for item in result:
                num += 1
                print(num, ') ', item["name"], "has a rating of: ", item["rating"])

        elif command == 'trending':
            # select data from the database
            pass

        elif command == 'map':
            # show map
            pass

        elif command == 'opentable':
            # Retrieve data from opentable API
            pass

        else:
            print("Please enter a valid command.")

# function for the initial command
def play():

    global instruction_message
    global initial_command

    print(initial_command)

    while True:

        user_input == input("Please enter a command usting the illustrated format.")

        if len(user_input.split()) > 1:
            command = user_input.split()[0]
        else:
            command = user_input

        if command == 'exit':
            print('Exiting the program. Thank you and bye!')
            return

        elif command == 'help':
            print(instruction_message)

        elif command == 'search':
            result = getYelp(user_input.split()[1])
            print("The 10 top ranking restaurants are:")
            num = 0
            for item in result:
                num += 1
                print(num, ') ', item["name"], "has a rating of: ", item["rating"])
            secondRun()

        elif command == 'trending':
            # select data from the database
            pass

        else:
            print("Please enter a valid command.")




## Plot 10 restaurants on the map




### test

test = getYelp('Cafe')
print(test)

saveSearch('Cafe')
