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
            
'''Create a group of 3 users, including the input user'''
def create_group(user_item_dict, user):
    similarities = compute_user_similarities(json_users, user)

    sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
    top_sim = list(sort_sim.keys())[:30]
    top_two_sim = list(sort_sim.keys())[:2]
    group = top_two_sim
    group.append(user)
    return group


'''Create a group_dictionary from a user_group (list) and predict all the user items' ratings'''
def create_group_pred(user_item_dict, user_group):
    group = {}
    for user in user_group:
        similarities = compute_user_similarities(user_item_dict, user)
        sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
        top_sim = list(sort_sim.keys())[:30]
        group[user] = compute_items_prediction(user_item_dict, user, top_sim)
    
    return group
    
    
    


# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)
    
user = "196"    
group_sim = create_group(json_users, user)
group = create_group_pred(json_users, group_sim)
avg_group = compute_average_aggregation(group)
least_group = compute_leastMisery_aggregation(group)
top_ten_items_id_avg = list(avg_group.keys())[:10]
top_ten_items_id_least = list(least_group.keys())[:10]

i=1
print("Average group ratings:\n")
for item in top_ten_items_id_avg:
    if item in json_items:
        print(f"{i}: {json_items[item]}")
    i += 1

i=1
print("\nLeast Misery group ratings:\n")
for item in top_ten_items_id_least:
    if item in json_items:
        print(f"{i}: {json_items[item]}")
    i += 1
            
    

