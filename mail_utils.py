import json
from datetime import datetime, timedelta
import random
from datetime import date
from bson.objectid import ObjectId
import calendar
from utils import get_points,gen_start_end_date,get_project_shifts
from flask_mail import Mail, Message
from datetime import date
from dateutil.relativedelta import relativedelta, SU
today = datetime.today()
last_monday = today + relativedelta(weekday=SU(-1))


import pymongo
client = pymongo.MongoClient("mongodb+srv://dbChirag:dbChirag123@swatiprodcluster0.bmxsv.mongodb.net/swatiinteriors")


# change this
db = client['swatiinteriors']
LOGS = db['logs']
projects = db['projects']
users = db['users']
attendances = db['attendances']
indents = db['indents']
indent_items = db['indent_items']
salaries = db['salaries']
employee_roles = db['employee_roles']
imeis = db['imeis']




def get_daily_footfall(user_site_preferences):
    today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    user_site_preferences = ['INDIABULLS BLU-PENT HOUSE', 'DLF LIMITED']
    total_footfall_query = [{'$match': {'date': today_date,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)



def convert_to_HTML(element_html):



    styles = '''

            <style>
            #customers {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
            }

            #customers td, #customers th {
            border: 1px solid #ddd;
            padding: 8px;
            }

            #customers tr:nth-child(even){background-color: #f2f2f2;}

            #customers tr:hover {background-color: #ddd;}

            #customers th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: black;
            color: white;
            }
            </style>

            '''

    base_template = '''
    <!DOCTYPE html>
    <html>
    <head>

    {}
    
    <title>Page Title</title>
    </head>
    <body>

    <img src = "https://i.imgur.com/0K0IOfY.png" style="display: flex;justify-content: center;"/>

    <h2>SWATI INTERIOR</h2>

    <p>This mail is from SWATI INTERIOR erp management software </p>

    <h1>1)DAILY FOOTFALL:</h1>

    {}

    <p>Please do not reply</p>

    </body>
    </html>
    '''.format(styles,element_html)

    return base_template



def convert_to_HTML_table(data,column_names):
    headers,table_body = "",""
    for i in range(len(column_names)):
        column_header = "<th>{}</th>".format(column_names[i])
        headers = headers + column_header
        headers_element = "<tr>"+str(headers)+"</tr>"

    for d in data:
        parent_row = ""
        for i in d.keys():
            parent_row = parent_row + "<td>"+str(d[i])+"</td>"
        table_body = table_body + "<tr>"+ parent_row + "</tr>"

    table_HTML = '<table id="customers">{}{}</table>'.format(headers_element,table_body)

    return convert_to_HTML(table_HTML)




def get_yesterday_footfall(user_site_preferences):
    today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d') -timedelta(days=1)
    user_site_preferences = ['INDIABULLS BLU-PENT HOUSE', 'DLF LIMITED']
    total_footfall_query = [{'$match': {'date': today_date,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'}
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)


def get_today_footfall(user_site_preferences):
    today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    user_site_preferences = ['INDIABULLS BLU-PENT HOUSE', 'DLF LIMITED']
    total_footfall_query = [{'$match': {'date': today_date,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'}
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)


def get_week_footfall(user_site_preferences):
    
    total_footfall_query = [{'$match': {'site_name':user_site_preferences[0]}},
                                {"$group": {'_id':{'$week':'$date'},
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'},
                                            }},{'$sort':{'_id':-1}}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)




def get_users_with_null_attendance_weekly_blacklist(user_site_preferences):
    
    total_footfall_query = [{'$match': {'attendance_points':None,
                                        'date': {"$gte": last_monday, "$lte": today},
                                        'site_name':user_site_preferences[0]}},
                                {"$group": {'_id': '$worker_full_name',
                                            'no_of_times_missed_attendance': {'$sum': 1}
                                            }},{'$sort':{'date':-1}}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)




def get_diff_weekly(user_site_preferences):
    report = list()
    for s in user_site_preferences:
    
        total_footfall_query = [{'$match': {'site_name':s}},
                                    {"$group": {'_id':{'$week':'$date'},
                                                'total_worker_footfall': {'$sum': 1},
                                                'average_working_hour_onsite': {'$avg': '$duration'},
                                                }},{'$sort':{'_id':-1}}]

        weekly_footfalls = list(attendances.aggregate(total_footfall_query))
    
    
        
        tw,pw = weekly_footfalls[0]['total_worker_footfall'],weekly_footfalls[1]['total_worker_footfall']
        footfall_status = "dropped" if pw > tw else "hiked"
        report.append({"site":s,
                       "previous_week_footfall":pw,
                       "this_week_footfall":tw,
                       "footfall_status":footfall_status,
                       "change":float(((tw-pw)*100)/pw)})
                      
    return report
    








  



        