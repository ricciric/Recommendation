import random
from recommendations import *
import math
import json

'''
Compute the average aggregation of a group of users, return a dict item:avg(rating) in descending order
'''
def compute_average_aggregation(group_user_item):
    avg = {}
    count = {}
    for user, ratings in group_user_item.items():
        for item, rating in ratings.items():
            if item not in avg:
                avg[item] = rating
                count[item] = 1
            else:
                avg[item] += rating
                count[item] += 1
                
    for item, tot_rating in avg.items():
        counter = count[item]
        avg[item] = tot_rating / counter if counter > 1 else tot_rating
    
    sorted_item_averages = dict(sorted(avg.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_item_averages
     
def compute_leastMisery_aggregation(group_user_item):
    least = {}
    for user, ratings in group_user_item.items():
        for item, rating in ratings.items():
            if item not in least:
                least[item] = rating
            else:
                if least[item] > rating:
                    least[item] = rating
    
    sorted_item_least = dict(sorted(least.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_item_least           
            
'''Create a group of 3 users, randomly'''
def create_group(user_item_dict, size):
    members = random.sample(list(user_item_dict.keys()), size)
    return members


'''Create a group_dictionary from a user_group (list) and predict all the user items' ratings'''
def compute_group_user_pred(user_item_dict, user_group):
    group = {}
    for user in user_group:
        similarities = compute_user_similarities(user_item_dict, user)
        sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
        top_sim = list(sort_sim.keys())[:30]
        user_group_copy = user_group[:]
        user_group_copy.remove(user)
        group[user] = compute_items_prediction(user_item_dict, user, top_sim + user_group_copy)
    
    return group

'''User's satisfaction is equal to the sum of the recommendations ratings divided by the individual user's ratings'''
def compute_user_sat(group, avg_rec, user):
    user_total_rating = 0
    group_total_rating = sum(avg_rec[item] for item in avg_rec)
    for user_1, ratings in group.items():
        for item, rating in ratings.items():
            if user_1 == user:
                user_total_rating += rating
         
    return group_total_rating/user_total_rating
    
    
def compute_group_satisfaction(group, avg_rec):
    tot = 0
    max_user_sat = 0
    for user in group.keys():
        user_sat = compute_user_sat(group, avg_rec, user)
        if user_sat>max_user_sat:
            max_user_sat = user_sat
        tot += user_sat

    return (tot/len(group))/max_user_sat
    
def compute_group_dis(group, avg_rec):
    max = 0
    min = compute_user_sat(group, avg_rec, next(iter(group)))
    for user in group.keys():
        user_sat = compute_user_sat(group, avg_rec, user)
        if user_sat > max:
            max = user_sat
        if user_sat < min:
            min = user_sat
    return (max - min)/max
 
def weighted_recommendations(group, avg_rec, least_rec):
    alpha = compute_group_dis(group, avg_rec)
    group_sat = compute_group_satisfaction(group, avg_rec)
    group_dis = compute_group_dis(group, avg_rec)
    weighted_recommendations = {}
    
    for user, ratings in group.items():
        for item, rating in ratings.items():
            # Formula took from Sequential group recommendations based on satisfaction and disagreement scores article
            weighted_recommendations[item] = (1-alpha)*avg_rec[item]+alpha*least_rec[item] 
    
    sort = dict(sorted(weighted_recommendations.items(), key=lambda x: x[1], reverse=True))
    return sort


# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)
    
group_choice = create_group(json_users, 3)
# print(group_choice)
group = compute_group_user_pred(json_users, group_choice)
avg_group = compute_average_aggregation(group)
least_group = compute_leastMisery_aggregation(group)
balanced_group = weighted_recommendations(group, avg_group, least_group)

i=1
top_ten_items_id_avg = list(avg_group.keys())[:10]
print("Average group ratings:\n")
for item in top_ten_items_id_avg:
    if item in json_items:
        print(f"{i}: {json_items[item]}")
    i += 1

i=1
top_ten_items_id_least = list(least_group.keys())[:10]
print("\nLeast Misery group ratings:\n")
for item in top_ten_items_id_least:
    if item in json_items:
        print(f"{i}: {json_items[item]}")
    i += 1
            
i=1
top_ten_items_balanced = list(balanced_group.keys())[:10]
print("\nWeighted recommendations based on group satisfaction and disagreement:\n")
for item in top_ten_items_balanced:
    if item in json_items:
        print(f"{i}: {json_items[item]}")
    i += 1

