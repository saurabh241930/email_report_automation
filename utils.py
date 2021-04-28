import pymongo
import json
from datetime import datetime, timedelta
import random
from datetime import date
from bson.objectid import ObjectId
import pymongo
import csv
import calendar



client = pymongo.MongoClient("mongodb+srv://dbChirag:dbChirag123@swatiprodcluster0.bmxsv.mongodb.net/swatiinteriors")

db = client['swatiinteriors']
projects = db['projects']
users = db['users']
attendances = db['attendances']
indents = db['indents']
indent_items = db['indent_items']
salaries = db['salaries']



def gen_start_end_date(month,year):
    start_date = str(year)+"-"+str(month)+"-01"
    end_date = str(year)+"-"+str(month)+"-" + str(calendar.monthrange(int(year), int(month))[1])
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    return start_date,end_date



def get_project_shifts(site_name):
    project_found = projects.find_one({"project_name": site_name})
    first_shift = project_found["shift_1_hour"]
    first_and_half_shift = project_found["shift_1_5_hour"]
    second_shift = project_found["shift_2_hour"]
    second_and_half_shift = project_found["shift_2_5_hour"]
    third_shift = project_found["shift_3_hour"]
    third_and_half_shift = project_found["shift_3_5_hour"]
    fourth_shift = project_found["shift_4_hour"]
    max_total_shift = first_shift + first_and_half_shift + second_shift + second_and_half_shift + third_shift + third_and_half_shift + fourth_shift
    return first_shift,first_and_half_shift,second_shift,second_and_half_shift,third_shift,third_and_half_shift,fourth_shift,max_total_shift



def get_points(shift_time,
               worker_single_shift_time,
               worker_one_and_half_shift_time,
               worker_double_shift_time,
               worker_two_and_half_shift_time,
               worker_tripple_shift_time,
               worker_tripple_and_half_shift_time,
               worker_fourth_shift_time,
               minimum_hr_threshold_in_min):

    hrs, minutes = [int(str(shift_time).split(":")[0]),
                    int(str(shift_time).split(":")[1])]


    if int(minutes) > int(minimum_hr_threshold_in_min):
        hrs = hrs+1

#     0.0 - 1.0
    if hrs <= worker_single_shift_time:
        return (hrs/worker_single_shift_time), hrs


#     1.0 - 1.5
    if worker_single_shift_time < hrs <= (worker_single_shift_time +
                                          worker_one_and_half_shift_time):
        extra = hrs-worker_single_shift_time
        return (1+((extra*0.5)/worker_one_and_half_shift_time)), hrs


#    1.5 - 2.0
    if (worker_single_shift_time +
        worker_one_and_half_shift_time) < hrs <= (worker_single_shift_time +
                                                  worker_one_and_half_shift_time +
                                                  worker_double_shift_time):
        extra = hrs-(worker_single_shift_time + worker_one_and_half_shift_time)
        return (1.5+((extra*0.5)/worker_double_shift_time)), hrs


#    2.0 - 2.5
    if (worker_single_shift_time +
        worker_one_and_half_shift_time +
        worker_double_shift_time) < hrs <= (worker_single_shift_time +
                                            worker_one_and_half_shift_time +
                                            worker_double_shift_time +
                                            worker_two_and_half_shift_time):
        extra = hrs-(worker_single_shift_time +
                     worker_one_and_half_shift_time + worker_double_shift_time)
        return (2.0+((extra*0.5)/worker_two_and_half_shift_time)), hrs


#    2.5 - 3.0
    if (worker_single_shift_time +
        worker_one_and_half_shift_time +
        worker_double_shift_time +
        worker_two_and_half_shift_time) < hrs <= (worker_single_shift_time +
                                                  worker_one_and_half_shift_time +
                                                  worker_double_shift_time +
                                                  worker_two_and_half_shift_time +
                                                  worker_tripple_shift_time):
        extra = hrs-(worker_single_shift_time + worker_one_and_half_shift_time +
                     worker_double_shift_time + worker_two_and_half_shift_time)
        return (2.5+((extra*0.5)/worker_tripple_shift_time)), hrs


#    3.0 - 3.5
    if (worker_single_shift_time +
        worker_one_and_half_shift_time +
        worker_double_shift_time +
        worker_two_and_half_shift_time +
        worker_tripple_shift_time) < hrs <= (worker_single_shift_time +
                                             worker_one_and_half_shift_time +
                                             worker_double_shift_time +
                                             worker_two_and_half_shift_time +
                                             worker_tripple_shift_time +
                                             worker_tripple_and_half_shift_time):
        extra = hrs-(worker_single_shift_time + worker_one_and_half_shift_time +
                     worker_double_shift_time + worker_two_and_half_shift_time + worker_tripple_shift_time)
        return (3.0+((extra*0.5)/worker_tripple_and_half_shift_time)), hrs


#    3.5 - 4.0
    if (worker_single_shift_time +
        worker_one_and_half_shift_time +
        worker_double_shift_time +
        worker_two_and_half_shift_time +
        worker_tripple_shift_time +
        worker_tripple_and_half_shift_time) < hrs <= (worker_single_shift_time +
                                                      worker_one_and_half_shift_time +
                                                      worker_double_shift_time +
                                                      worker_two_and_half_shift_time +
                                                      worker_tripple_shift_time +
                                                      worker_tripple_and_half_shift_time +
                                                      worker_fourth_shift_time):
        extra = hrs-(worker_single_shift_time + worker_one_and_half_shift_time + worker_double_shift_time + worker_two_and_half_shift_time + worker_tripple_shift_time +
                     worker_tripple_and_half_shift_time)

        return (3.5+((extra*0.5)/worker_fourth_shift_time)), hrs

    #   only 4.0
    if  hrs > (worker_single_shift_time +
                worker_one_and_half_shift_time +
                worker_double_shift_time +
                worker_two_and_half_shift_time +
                worker_tripple_shift_time +
                worker_tripple_and_half_shift_time +
                worker_fourth_shift_time):

        return 4, hrs