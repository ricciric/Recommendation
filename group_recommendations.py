import random
from recommendations import compute_items_prediction, compute_pearson_similarity, compute_user_similarities, compute_prediction
import numpy as np
import json
import matplotlib.pyplot as plt


'''
Compute the average aggregation of a group of users, return a dict item:avg(rating) in descending order
'''
def average_aggregation(ratings):
    agg = {}
    if isinstance(list(ratings.values())[0], dict):  # Check if input is of the form {user: {item: rating}}
        for user in ratings.keys():
            for item in ratings[user].keys():
                if item not in agg:
                    agg[item] = []
                agg[item].append(ratings[user][item])
    else:  # Input is of the form {item: rating}
        for item in ratings.keys():
            agg[item] = [ratings[item]]
    
    for item in agg.keys():
        agg[item] = sum(agg[item]) / len(agg[item])
        
    sorted_item_avg = dict(sorted(agg.items(), key=lambda x: x[1], reverse=True)) 
    return sorted_item_avg

def average_item_aggregation(item, group_ratings):
    ratings = [rating for i, rating in group_ratings.items() if i == item]
    if ratings:
        return sum(ratings) / len(ratings)
    else:
        return None  

def leastMisery_aggregation(ratings):
    least = {}
    if isinstance(list(ratings.values())[0], dict):  # Check if input is of the form {user: {item: rating}}
        for user in ratings.keys():
            for item in ratings[user].keys():
                if item not in least:
                    least[item] = ratings[user][item]
                else:
                    if least[item] > ratings[user][item]:
                        least[item] = ratings[user][item]
    else:  # Input is of the form {item: rating}
        for item in ratings.keys():
            if item not in least:
                least[item] = ratings[item]
            else:
                if least[item] > ratings[item]:
                    least[item] = ratings[item]
                
    sorted_item_least = dict(sorted(least.items(), key=lambda x: x[1], reverse=True)) 
    return sorted_item_least   

def least_misery_item_aggregation(item, group_ratings):
    ratings = [rating for i, rating in group_ratings.items() if i == item]
    if ratings:
        return min(ratings)
    else:
        return None

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
                        print(f"Added user {user_2} with similarity {sim}")
                else:
                    if sim < -0.5:
                        added_members_nosim += 1
                        members.append(user_2)
                        print(f"Added user {user_2} with similarity {sim}")
                
    return members


'''Create a group_dictionary from a user_group (list) and predict all the user items' ratings'''
def compute_group_user_pred(user_item_dict, user_group):
    group = {}

    for user in user_group:
        percentage = 0
        similarities = compute_user_similarities(user_item_dict, user)
        sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
        top_sim = list(sort_sim.keys())[:100]
        group[user] = user_item_dict[user]
        top_sim.extend(user_group)
        group[user] = compute_items_prediction(user_item_dict, user, top_sim)
        for item in group[user]:
            if group[user][item] == 5:
                percentage += (group[user][item])
        print(f"Percentage of rating 5 in user {user}: {percentage/100}")

    return group

'''User's satisfaction is equal to the sum of the recommendations ratings divided by the individual user's ratings'''
def compute_user_sat(group, rec, user, max_recommendations=20):
    user_ratings = []
    for item, rating in group[user].items():
        user_ratings.append(rating)
    
    sort_ratings = sorted(user_ratings, reverse=True)[:max_recommendations]
    user_list_sat = sum(rating for rating in sort_ratings)

    sorted_rec = dict(sorted(rec.items(), key=lambda item: item[1], reverse=True))
    top_rec_items = list(sorted_rec.keys())[:max_recommendations]
    
    group_list_sat = 0
    for item in top_rec_items:
        if item in group[user]:
            group_list_sat += group[user][item]
    
     
    user_sat = group_list_sat/user_list_sat
    return user_sat
    
    
def compute_group_dis(group, rec, iteration):
    max = 0
    min = np.inf
    for user in group:
        user_sat = compute_user_sat(group, rec, user)
        user_sat = user_sat 
        if user_sat > max:
            max = user_sat
        if user_sat < min:
            min = user_sat
            
    return (max - min)
 
def compute_overall_group_sat(group, rec, iteration):
    group_sat = 0
    cardinality = len(group.keys())
    for user in group:
        user_sat = compute_user_sat(group, rec, user)
        user_sat = user_sat / iteration
        group_sat += user_sat
    
    return group_sat/cardinality

def compute_group_sat(group, rec):
    group_sat = 0
    for user in group:
        user_sat = compute_user_sat(group, rec, user)
        group_sat += user_sat
    
    return group_sat/len(group.keys())


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
                    sat += abs(compute_user_sat(group, temp, users[i]) - compute_user_sat(group, temp, users[j]))
            
            if sat < min:
                min = sat
                best_item = item
        
        items.remove(best_item)
        candidate_set.append(best_item)
    
    return candidate_set

'''Compute the items prediction from a list of similar users'''          
def compute_items_prediction_sequential(user_item_dict, user1, similar_users, recommendations):
    pred = {}

    # Get all items rated by any user in the group
    all_items = set().union(*[set(user_item_dict[user].keys()) for user in similar_users])

    for item in all_items:
        if not recommendations:
            if item not in user_item_dict[user1]:
                pred[item] = compute_prediction(user_item_dict, user1, item, similar_users)
            else:
                pred[item] = user_item_dict[user1][item]
        else:
            if item not in user_item_dict[user1] and item not in recommendations:
                pred[item] = compute_prediction(user_item_dict, user1, item, similar_users)
            else:
                # If the item is already in the recommendations, skip it
                continue
    return pred

def hybrid_2(user_item_dict, group, iterations):
    previous_rec = []
    update = {}
    alpha_values = []
    for i in range(1, iterations + 1):
        aggregated_recommendations = {}
        recommendations = {}
        for user in group:
            similarities = compute_user_similarities(user_item_dict, user)
            sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
            top_sim = list(sort_sim.keys())[:100]
            individual_recommendations = compute_items_prediction_sequential(user_item_dict, user, top_sim, previous_rec)
            
            for item, rating in individual_recommendations.items():
                aggregated_recommendations[item] = rating
                
        if i == 1:
            alpha = 0
        else:
            alpha = compute_group_dis(group, update, i)
            update = {}
            
        for item in aggregated_recommendations:
            if item not in recommendations:
               recommendations[item] = 0
               
            recommendations[item] += (1-alpha) * average_item_aggregation(item, aggregated_recommendations) + alpha * least_misery_item_aggregation(item, aggregated_recommendations)
            
        update = recommendations.copy()
        recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1], reverse=True))
        group_sat = compute_group_sat(group, recommendations)
        overall_group_sat = compute_overall_group_sat(group, recommendations, i)
        alpha_values.append(alpha)
        
        # Printing info.
        print(f"\n****************** VALUES {i}******************")
        print(f"Alpha value: {float(alpha)}")
        print(f"Group satisfaction: {group_sat}")
        print(f"Overall group satisfaction: {overall_group_sat}")
        for user in group.keys():
            user_sat = compute_user_sat(group, recommendations, user)
            print(f"User satisfaction for user {user}: {user_sat}")
        print("\n********************************************")
        previous_rec += print_top_ten(recommendations, json_items, 10)
    
    iterations = range(1, iterations + 1)
    fig = plt.figure(facecolor='white')    
    ax = fig.add_subplot()
    ax.plot(iterations, alpha_values, marker='o')
    ax.set_title('Alpha Values over Iterations')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Alpha Value')
    ax.set_xticks(iterations)
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_facecolor('white')
    ax.set_ylim(0, 1)
    ax.set_xlim(1, iterations[-1])
    plt.grid(False)
    plt.tight_layout()
    plt.show()
        
               


def print_top_ten(rec, items, size=10):
    i=1
    top_ten_items_id = list(rec.keys())[:size]
    for item in top_ten_items_id:
        if item in items:
            print(f"{i}: {items[item]}")
        i += 1
    return top_ten_items_id

# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)
    
group_choice = create_group(json_users, 3)
print(group_choice)     
        
group = compute_group_user_pred(json_users, group_choice)
avg_group = average_aggregation(group)
least_group = leastMisery_aggregation(group)
borda_group = bordaCount_aggregation(group)
# hybrid_2(json_users, group, 5)
# sequential_group = sequential_recommendations(group, avg_group)

top_ten_items_id_borda = list(borda_group.keys())[:10]
for user in group.keys():
        user_sat = compute_user_sat(group, borda_group, user)
        print(f"User satisfaction for user {user}: {user_sat}")
print("\nBorda Count aggregation group ratings:\n")
print_top_ten(borda_group, json_items)

i=1
top_ten_items_id_avg = list(avg_group.keys())[:10]
for user in group.keys():
        user_sat = compute_user_sat(group, avg_group, user)
        print(f"User satisfaction for user {user}: {user_sat}")
print("\nAverage group ratings:\n")
print_top_ten(avg_group, json_items)

i=1
top_ten_items_id_least = list(least_group.keys())[:10]
for user in group.keys():
        user_sat = compute_user_sat(group, least_group, user)
        print(f"User satisfaction for user {user}: {user_sat}")
print("\nLeast Misery group ratings:\n")
print_top_ten(least_group, json_items)
            
            
# i=1
# print("\nSequential recommendantion ratings:\n")
# for item in sequential_group:
#     if item in json_items:
#         print(f"{i}: {json_items[item]}")
#     i += 1