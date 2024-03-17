from recommendations import *
import math
import json

'''
Average aggregation is the average 
of an item rating or a predicted one,
in a group of users with that item
r*(g,i) = AVG{r*(u,i)}
where r: predicted score of the item for the group
g: group
i: item
u: user
'''
def compute_average_aggregation(group_user_item):
    return

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
    print(group.keys())
    
    


# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)
    
user = "196"    
group_sim = create_group(json_users, user)
create_group_pred(json_users, group_sim)
    

