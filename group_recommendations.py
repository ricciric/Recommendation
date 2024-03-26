import random
from recommendations import *
import numpy as np
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
    for users in group_user_item.values():
        for item, rating in users.items():
            if item not in least:
                least[item] = rating
            else:
                if least[item] > rating:
                    least[item] = rating
                
    sorted_item_least = dict(sorted(least.items(), key=lambda x: x[1], reverse=True)) 
    return sorted_item_least     
           
'''Create a group of (size) users, randomly'''
def create_group(user_item_dict, size):
    members = []
    added_members_sim = 0
    added_members_nosim = 0
    user_1 = random.choice(list(user_item_dict.keys()))
    members.append(user_1)
    while len(members) < size:
            user_2 = random.choice(list(user_item_dict.keys()))
            sim = compute_pearson_similarity(user_item_dict, user_1, user_2)
            if sim != None:
                if added_members_sim <= added_members_nosim:
                    if sim > 0.5:
                        added_members_sim += 1
                        members.append(user_2)
                else:
                    if sim < -0.5:
                        added_members_nosim += 1
                        members.append(user_2)
                
    return members


'''Create a group_dictionary from a user_group (list) and predict all the user items' ratings'''
def compute_group_user_pred(user_item_dict, user_group):
    group = {}
    for user in user_group:
        similarities = compute_user_similarities(user_item_dict, user)
        sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
        top_sim = list(sort_sim.keys())[:100]

        group[user] = compute_items_prediction(user_item_dict, user, top_sim)
    
    return group

'''User's satisfaction is equal to the sum of the recommendations ratings divided by the individual user's ratings'''
def compute_user_sat(group, rec, user):
    # Cerca il problema qui
    sorted_user_rec = sorted(group[user].items(), key=lambda x: x[1], reverse=True)
    top_items = sorted_user_rec[:50]
    user_list_sat = sum(score for _, score in sorted_user_rec[:50])  
    group_list_sat = 0
    for item, score in rec.items():
        if item in top_items:
            group_list_sat += score
    
    user_sat = group_list_sat/user_list_sat
    return user_sat
    
    
def compute_group_dis(group, rec):
    max = 0
    min = compute_user_sat(group, rec, next(iter(group)))
    for user in group.keys():
        user_sat = compute_user_sat(group, rec, user)
        print(f"******* USER {user} SAT : {user_sat} ********")
        if user_sat > max:
            max = user_sat
        if user_sat < min:
            min = user_sat
            
    return (max - min)
 
def weighted_recommendations(group, alpha):
    weighted_recommendations = {}
    avg_rec = compute_average_aggregation(group)
    least_rec = compute_leastMisery_aggregation(group)
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
print(group_choice)

# for user_1 in group_choice:
#     user_2 = group_choice[0]
#     if user_1 != user_2:
#         sim = compute_pearson_similarity(json_users, user_1, user_2)
#         print(f"sim {user_1}, {user_2} = {sim}")
    
        
        
group = compute_group_user_pred(json_users, group_choice)
avg_group = compute_average_aggregation(group)
least_group = compute_leastMisery_aggregation(group)
iterations = 3
alpha = 0
# for j in range(iterations):
#     balanced_group = weighted_recommendations(group, alpha)
#     print(f"\nALPHA VALUE ITER_{j} = {alpha}")
#     alpha = compute_group_dis(group, balanced_group)
#     i=1
#     top_ten_items_balanced = list(balanced_group.keys())[:30]
#     print(f"\nWeighted recommendations based on group satisfaction and disagreement [iteration_{j}]:\n")
#     for item in top_ten_items_balanced:
#         if item in json_items:
#             print(f"{i}: {json_items[item]}")
#         i += 1

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
            
# i=1
# top_ten_items_balanced = list(balanced_group.keys())[:10]
# print("\nWeighted recommendations based on group satisfaction and disagreement:\n")
# for item in top_ten_items_balanced:
#     if item in json_items:
#         print(f"{i}: {json_items[item]}")
#     i += 1

