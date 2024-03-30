import json
import math

'''Utility function for creating a json file for the users ratings'''
def create_users_json(data):
    user_item = {}
    
    with open(data, 'r') as file:
        for line in file:
            user_id, item_id, rank, timeStamp  = map(int, line.strip().split('\t'))
            
            if user_id in user_item:
                user_item[user_id][item_id] = rank
            else:
                user_item[user_id] = {item_id:rank}
    
    
    return user_item

'''Utility function for creating a json file for the items' names [Aesthetic]'''
def create_item_json(data):
    items = {}
    
    with open(data, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            parts = line.strip().split('|')
            item_id = int(parts[0])
            name = parts[1]
            
            items[item_id] = name
    
    return items


'''Get common items between 2 users'''
def get_common_items(user_item_dict, user1 ,user2):
    return set(user_item_dict[user1].keys()) & set(user_item_dict[user2].keys())


'''Compute similarity between two users with Pearson's'''
def compute_pearson_similarity(user_item_dict, x, y):
    common_items = get_common_items(user_item_dict, x, y)
    if len(common_items) > 0:
        
        mean_x = math.fsum(user_item_dict[x][item] for item in user_item_dict[x].keys()) / len(user_item_dict[x].keys())
        mean_y = math.fsum(user_item_dict[y][item] for item in user_item_dict[y].keys()) / len(user_item_dict[y].keys())
        
        num = math.fsum((user_item_dict[x][item] - mean_x) * (user_item_dict[y][item] - mean_y) for item in common_items)
        den_x = math.fsum((user_item_dict[x][item] - mean_x)**2 for item in common_items)
        den_y = math.fsum((user_item_dict[y][item] - mean_y)**2 for item in common_items)
        
        if den_x==0 or den_y==0:
            return None
        
        corr_coeff = num / (math.sqrt(den_x) * math.sqrt(den_y))
        return corr_coeff
    
    else:
        return None
    
    
'''Compute spearman similarity'''
def compute_spearman_similarity(user_item_dict, x, y):
    common_items = set(user_item_dict[x].keys()) & set(user_item_dict[y].keys())
    n = len(common_items)
    if n > 0:
        # Get the ranks for each user
        ranked_x = [user_item_dict[x][item] for item in common_items]
        ranked_y = [user_item_dict[y][item] for item in common_items]
        
        # Compute the difference in ranks for each pair of items in common
        differences = [ranked_x[i] - ranked_y[i] for i in range(n)]
        squared_differences = [diff**2 for diff in differences]
        sum_squared_differences = sum(squared_differences)

        
        # Compute the Spearman correlation coefficient
        spearman_corr_coeff = 1 - (6 * sum_squared_differences) / (n * (n**2 - 1))
        return spearman_corr_coeff
    else:
        return 0
     

'''Compute similarities for all the users [not used, just for testing]'''
def compute_all_users_similiraties(user_item_dict):
    similarities = {}
    for user1 in user_item_dict:
        for user2 in user_item_dict:
            if user1 != user2:
                similarity = compute_pearson_similarity(user_item_dict, user1, user2)
                
                if user1 not in similarities:
                    similarities[user1] = {}
                    
                similarities[user1][user2] = similarity
                
    return similarities


'''Compute all similarities for just one user'''
def compute_user_similarities(user_item_dict, user1):
    similarities = {}
    for user2 in user_item_dict:
        if user1 != user2:
            similarity = compute_pearson_similarity(user_item_dict, user1, user2)
            if similarity == None:
                continue
            else: 
                similarities[user2] = similarity
    return similarities


'''Compute the items prediction from a list of similar users'''                
# def compute_items_prediction(user_item_dict, user1, similar_users):
#     pred = {}
    
#     items_user1 = set(user_item_dict[user1].keys())
    
#     for user2 in similar_users:
#         if user2 != user1:
#             items_user2 = set(user_item_dict[user2].keys())
#             unrated_items = items_user2 - items_user1

#             for item in unrated_items:
#                 if item not in pred:
#                     pred[item] = compute_prediction(user_item_dict, user1, item, similar_users)
    
#     for item in items_user1:
#         pred[item] = user_item_dict[user1][item]
    
#     return pred

def compute_items_prediction(user_item_dict, user1, similar_users):
    pred = {}

    # Get all items rated by any user in the group
    all_items = set().union(*[set(user_item_dict[user].keys()) for user in similar_users])

    for item in all_items:
        if item not in user_item_dict[user1]:
            pred[item] = compute_prediction(user_item_dict, user1, item, similar_users)
        else:
            pred[item] = user_item_dict[user1][item]
    
    return pred
        

'''Compute the prediction for a single item based on the similar users'''
def compute_prediction(user_item_dict, a, item, similar_users):
    num = 0
    den = 0
    mean_a = math.fsum(user_item_dict[a][i] for i in user_item_dict[a].keys()) / len(user_item_dict[a].keys())
    set = 0
    
    for b in similar_users:
        if item in user_item_dict[b]:
            set += 1
            mean_b = sum(user_item_dict[b][i] for i in user_item_dict[b].keys()) / len(user_item_dict[b].keys())
            similarity = compute_pearson_similarity(user_item_dict, a, b)
            num += (similarity * (user_item_dict[b][item] - mean_b))
            den += similarity
    
    if den == 0:
        return 0
      
    else:
        prediction = mean_a + (num/den)    
     
    prediction = min(5, max(1, prediction))
    
    return prediction   
             
''' 
Json creation
# Reading the two data files [u.data], [u.item]
data_file = "ml-100k/u.data"
item_file = "ml-100k/u.item"

json_users = create_users_json(data_file)
json_items = create_item_json(item_file)

with open('user_item.json', 'w') as json_file:
    json.dump(json_users, json_file, indent=4)
    
print(f"JSON created from file: {data_file}")

with open('item.json', 'w') as json_file:
    json.dump(json_items, json_file, indent=4)
    
print(f"JSON created from file: {item_file}\n")
'''

# Json reading
with open('user_item.json', 'r') as json_file:
    json_users = json.load(json_file)
    
with open('item.json', 'r') as json_file:
    json_items = json.load(json_file)

user = "100"
user_2 = "19"
 
similarities = compute_user_similarities(json_users, user)
# Sorting and extracting the top ten user and items
sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
top_sim = list(sort_sim.keys())[:50]
top_ten_sim = list(sort_sim.keys())[:10]
# Compute item pred. between a user and his 30 most similar users
top_items = compute_items_prediction(json_users, user, top_sim)
sort_items = dict(sorted(top_items.items(), key=lambda item: item[1], reverse=True))
top_ten_items_id = list(sort_items.keys())[:10]
top_ten_items_name = []

for item_id in top_ten_items_id:
    for id, name in json_items.items():
        if(id == item_id):
            top_ten_items_name.append(name)
  
print(f"Top ten users similarities for user {user}: {top_ten_sim}\n")
i = 1
print(f"Top ten movies recommendations for user {user}:\n")
for name in top_ten_items_name:
    print(f"{i}: {name}")
    i += 1

print(f"\nComputing Pearson's and Spearman's correlation coefficents for users: [{user}, {user_2}]\n")
print(f"\tPearson: {compute_pearson_similarity(json_users, user, user_2)}")
print(f"\tSpearman: {compute_spearman_similarity(json_users, user, user_2)}\n")

    

 


