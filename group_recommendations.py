import random
from recommendations import *
import numpy as np
import json

'''
Compute the average aggregation of a group of users, return a dict item:avg(rating) in descending order
'''
def average_aggregation(group_user_item):
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
     
def leastMisery_aggregation(group_user_item):
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

def bordaCount_aggregation(group_user_item):
    temp = group_user_item.copy()
    for user, items in temp.items():
        sorted_keys = sorted(items, key=items.get)
        temp[user] = {k: items[k] for k in sorted_keys}
    group_score = {}
    temp2 = temp.copy()
    for user, items in temp.items():
        i = 1
        for item in items:
            temp2[user][item] = i
            i+=1
    for user, items in temp2.items():
        for item in items:
            if item not in group_score:
                group_score[item] = temp2[user][item]
            group_score[item] += temp2[user][item]
    sorted_scores = dict(sorted(group_score.items(), key=lambda item: item[1], reverse=True))
    return sorted_scores
            
           
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
def compute_user_sat(group, rec, user, k=10):
    items = {}
    user_list_sat = 0
    
    for item, rating in group[user].items():
        items[item] = rating
    sort_items = dict(sorted(items.items(), key=lambda item: item[1], reverse=True))
    top_items = {key: sort_items[key] for key in list(sort_items)[:k]}
    
    for i, r in top_items.items():
        user_list_sat += r
    
    group_list_sat = 0
    i=0
    for item, score in rec.items():
        if i == k:
            break
        group_list_sat += score
        i+=1
        
    

    user_sat = group_list_sat/user_list_sat
    return user_sat
    
    
def compute_group_dis(group, rec):
    max = 0
    min = np.inf
    for user in group.keys():
        user_sat = compute_user_sat(group, rec, user)
        if user_sat > max:
            max = user_sat
        if user_sat < min:
            min = user_sat
            
    return (max - min)
 
def weighted_recommendations(group, alpha):
    weighted_recommendations = {}
    avg_rec = average_aggregation(group)
    least_rec = leastMisery_aggregation(group)
    for user, ratings in group.items():
        for item, rating in ratings.items():
            # Formula took from Sequential group recommendations based on satisfaction and disagreement scores article
            weighted_recommendations[item] = (1-alpha)*avg_rec[item]+alpha*least_rec[item] 
    
    
    sort = dict(sorted(weighted_recommendations.items(), key=lambda x: x[1], reverse=True))
    return sort

# group of users and items, reccomendation (aggregation), number of items in the returned list
def sequential_recommendations(group, rec, k=10):
    users = list(group.keys())
    items = list(rec.keys())
    candidate_set = [items.pop(0)]
    
    for h in range(k-1):
        min = np.inf
        best_item = None
        
        for item in items:
            sat = 0
            temp = candidate_set.copy()
            temp.append(item)
            
            for i in range(0, len(users)):
                for j in range(i+1, len(users)):
                    sat += abs(compute_user_sat(group, rec, users[i]) - compute_user_sat(group, rec, users[j]))
            
            if sat < min:
                min = sat
                best_item = item
        
        items.remove(best_item)
        candidate_set.append(best_item)
    
    return candidate_set

def sequential_hybrid_recommendations(group, iterations):
    items = set()
    
    for user in group:
        for item, rating in group[user].items():
            items.add(item)
            
    alpha = 0
    for i in range(0, iterations):
    
        avg_rec = average_aggregation(group)
        least_rec = leastMisery_aggregation(group)
        rec = {}
        
        for item in items:
            rec[item] = (1-alpha)*avg_rec[item]+alpha*least_rec[item] 
        
        print(f"\nALPHA VALUE: {alpha}")
        sort = dict(sorted(rec.items(), key=lambda x: x[1], reverse=True))
        print_top_ten(sort, json_items)
        alpha = compute_group_dis(group, rec)
        
        


def print_top_ten(rec, items):
    i=1
    top_ten_items_id = list(rec.keys())[:10]
    for item in top_ten_items_id:
        if item in items:
            print(f"{i}: {items[item]}")
        i += 1

# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)
    
group_choice = create_group(json_users, 3)
print(group_choice)

for user_1 in group_choice:
    user_2 = group_choice[0]
    if user_1 != user_2:
        sim = compute_pearson_similarity(json_users, user_1, user_2)
        print(f"sim {user_1}, {user_2} = {sim}")
    
        
        
group = compute_group_user_pred(json_users, group_choice)
avg_group = average_aggregation(group)
least_group = leastMisery_aggregation(group)
borda_group = bordaCount_aggregation(group)
hybrid_group = sequential_hybrid_recommendations(group, 3)

# sequential_group = sequential_recommendations(group, avg_group)

# print("\nBorda Count aggregation group ratings:\n")
# print_top_ten(borda_group, json_items)

# i=1
# top_ten_items_id_avg = list(avg_group.keys())[:50]
# print("\nAverage group ratings:\n")
# print_top_ten(avg_group, json_items)

# i=1
# top_ten_items_id_least = list(least_group.keys())[:10]
# print_top_ten(least_group, json_items)
            
# i=1
# top_ten_items_balanced = list(balanced_group.keys())[:10]
# print("\nWeighted recommendations based on group satisfaction and disagreement:\n")
# print_top_ten(balanced_group, json_items)

# i=1
# print("\nSequential recommendantion ratings:\n")
# for item in sequential_group:
#     if item in json_items:
#         print(f"{i}: {json_items[item]}")
#     i += 1