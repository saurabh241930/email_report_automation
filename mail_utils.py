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
from datetime import date
from dateutil.relativedelta import relativedelta, SU
today = datetime.today()
yesterday = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d') -timedelta(days=1)
last_monday = today + relativedelta(weekday=SU(-1))
current_month_text = datetime.now().strftime('%B')

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




def report_template(element_html):



    styles = '''

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

            '''

    base_template = '''
    <!DOCTYPE html>
    <html>
    <head>
    
    <style>{}</style>

    
    
    <title>Page Title</title>
    </head>
    <body>

    <img src = "https://i.imgur.com/0K0IOfY.png" style="display: flex;justify-content: center;"/>

    <h2>SWATI INTERIOR</h2>

    <p>This mail is consist of software generated weekly summarized attendance report from SWATI INTERIOR erp management software,you will recieve this auto-generated at every end of the week of your corresponding project</p>

    {}

    <p>More features incoming soon</p>

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
            d[i] = int(d[i]) if type(d[i]) == float else d[i]
            parent_row = parent_row + "<td>"+str(d[i])+"</td>"
        table_body = table_body + "<tr>"+ parent_row + "</tr>"

    table_HTML = '<table id="customers">{}{}</table>'.format(headers_element,table_body)

    return table_HTML




def get_daily_footfall(user_site_preferences):
    today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    user_site_preferences = ['INDIABULLS BLU-PENT HOUSE', 'DLF LIMITED']
    total_footfall_query = [{'$match': {'date': today_date,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)





def get_yesterday_footfall(user_site_preferences):
    total_footfall_query = [{'$match': {'date': yesterday,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'}
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)


def get_yesterday_blacklist(user_site_preferences):
    today = datetime.today()
    query = [{'site_name':{'$in':user_site_preferences},'attendance_points':None,'date': yesterday}]
    return list(attendances.find(query))


def pre_process_footfall_history(footfall_list):
    out = list()
    for i in footfall_list:
        i["average_working_hour_onsite"] = "No data available" if i["average_working_hour_onsite"] == None else str(int(i["average_working_hour_onsite"]))
        out.append(i)
        
    return out
    

def get_today_footfall(user_site_preferences):
    today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    total_footfall_query = [{'$match': {'date': today_date,'site_name':{'$in':user_site_preferences}}},
                                {"$group": {'_id': '$site_name',
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'}
                                            }}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)


def get_all_week_footfall(user_site_preferences):
    
    total_footfall_query = [{'$match': {'site_name':user_site_preferences[0]}},
                                {"$group": {'_id':{'$week':'$date'},
                                            'total_worker_footfall': {'$sum': 1},
                                            'average_working_hour_onsite': {'$avg': '$duration'},
                                            }},{'$sort':{'_id':-1}}]

    total_footfall_project_wise_data = attendances.aggregate(total_footfall_query)
    return list(total_footfall_project_wise_data)



def get_week_footfall(user_site_preferences):
    out = list()
    for s in user_site_preferences:
    
        query = [{'$match': {'site_name':s,'date': {"$gte": last_monday, "$lte": today}}},
                                    {"$group": {'_id':{'$dateToString': { 'format': "%Y-%m-%d", 'date': "$date"}},
                                                'total_worker_footfall': {'$sum': 1},
                                                'average_working_hour_onsite': {'$avg': '$duration'},
                                                }},{'$sort':{'_id':1}}]
        
        out.append({str(s):list(attendances.aggregate(query))})

    return out


def get_users_with_null_attendance_weekly_blacklist(user_site_preferences):
    out = []
    for s in user_site_preferences:
        query = [{'$match': {'attendance_points':None,
                                            'date': {"$gte": last_monday, "$lte": today},
                                            'site_name':s}},
                                    {"$group": {'_id': '$worker_full_name',
                                                'no_of_times_missed_attendance': {'$sum': 1}
                                                }},{'$sort':{'date':-1}}]

        out.append({s:list(attendances.aggregate(query))})
        
    return out


def get_diff_weekly(user_site_preferences):
    report = list()
    for s in user_site_preferences:
    
        total_footfall_query = [{'$match': {'site_name':s}},
                                    {"$group": {'_id':{'$week':'$date'},
                                                'total_worker_footfall': {'$sum': 1},
                                                'average_working_hour_onsite': {'$avg': '$duration'},
                                                }},{'$sort':{'_id':-1}}]

        weekly_footfalls = list(attendances.aggregate(total_footfall_query))
        try:
            tw,pw = weekly_footfalls[0]['total_worker_footfall'],weekly_footfalls[1]['total_worker_footfall']
            footfall_status = "dropped" if pw > tw else "hiked"
            report.append({"site":s,
                           "previous_week_footfall":pw,
                           "this_week_footfall":tw,
                           "footfall_status":footfall_status,
                           "change":float(((tw-pw)*100)/pw)})
        except IndexError:
            continue   
    return report





def gen_week_summary(user_site_preferences):
    
    week_summary = get_diff_weekly(user_site_preferences)
    week_blacklist_list = get_users_with_null_attendance_weekly_blacklist(user_site_preferences)
    week_footfall = get_week_footfall(user_site_preferences)
    
    out = "<h1>WEEKLY ATTENDANCE SUMMARY REPORT</h1><br><br"
    
    out = out + "<p>1).Below is the list of comparison of this week footfall & its previous week footfall of total footfall along with dropped/hiked percentage</p>"
    week_summary_table_HTML = convert_to_HTML_table(week_summary,
                                              column_names=["Site","Footfall(last week)",
                                                            "Footfall(this week)","Comparison Indicator","Net change in %"])
    out = out+"<br><br>"
    out = out + week_summary_table_HTML
    out = out + "<p style='font-size:23px;color:red'>2).Below is the list of all individual worker who has has note completed attendance across sites</p>"

    for l in week_blacklist_list:
        
        key = list(l.keys())[0]
        if len(l[key]) == 0:
            continue
        out = out + "<p><strong><span style='color:red;font-size:21px'>{}:<br></span></strong>List of worker with incompleted attendance</p>".format(key)
        week_blacklist_table_HTML = convert_to_HTML_table(l[key],column_names=["Worker/Employee name","No. of times attendance not completed(this week)"])
        out = out + week_blacklist_table_HTML
        
    out = out+"<br><br>"
        
    out = out + "<p style='font-size:23px;color:blue'>3).Following is the list of footfall over this week along with average shift hour of that specific day in week</p>"
    for l in week_footfall:
        key = list(l.keys())[0]
        if len(l[key]) == 0:
            out = out + "<p><strong><span style='color:blue;font-size:21px'>{}:<br></span></strong>No data recorded for this site this week</p>".format(key)
            continue
        out = out + "<p><strong><span style='color:blue;font-size:21px'>{}:<br></span></strong>Footfall history over this week</p>".format(key)
        week_footfall_table_HTML = convert_to_HTML_table(pre_process_footfall_history(l[key]),
                                                          column_names=["Week Date","Footfall","Average shift hour duration"])
        out = out + week_footfall_table_HTML
        
    out = out+"<br><br>"
    
    
    return report_template(out)
    
