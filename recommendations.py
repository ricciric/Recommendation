import json
import math

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

def create_item_json(data):
    items = {}
    
    with open(data, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            parts = line.strip().split('|')
            item_id = int(parts[0])
            name = parts[1]
            
            items[item_id] = name
    
    return items


# (b) Implement the user-based collaborative filtering approach, using the Pearson correlation function for computing similarities between users

# Get common items between 2 users
def get_common_items(user_item_dict, user1 ,user2):
    return set(user_item_dict[user1].keys()) & set(user_item_dict[user2].keys())


# Compute similarity between two users with Pearson's
def compute_similarity(user_item_dict, x, y):
    common_items = get_common_items(user_item_dict, x, y)
    if len(common_items) > 0:
        
        mean_x = math.fsum(user_item_dict[x][item] for item in user_item_dict[x].keys()) / len(user_item_dict[x].keys())
        mean_y = math.fsum(user_item_dict[y][item] for item in user_item_dict[y].keys()) / len(user_item_dict[y].keys())
        
        num = math.fsum((user_item_dict[x][item] - mean_x) * (user_item_dict[y][item] - mean_y) for item in common_items)
        den_x = math.fsum((user_item_dict[x][item] - mean_x)**2 for item in common_items)
        den_y = math.fsum((user_item_dict[y][item] - mean_y)**2 for item in common_items)
        
        if den_x==0 or den_y==0:
            return 0 
        
        corr_coeff = num / (math.sqrt(den_x) * math.sqrt(den_y))
        return corr_coeff
    
    else:
        return 0
        


# Compute similarities for all the users
def compute_all_users_similiraties(user_item_dict):
    similarities = {}
    for user1 in user_item_dict:
        for user2 in user_item_dict:
            if user1 != user2:
                similarity = compute_similarity(user_item_dict, user1, user2)
                
                if user1 not in similarities:
                    similarities[user1] = {}
                    
                similarities[user1][user2] = similarity
                
    return similarities


# Compute all similarities for just one user
def compute_user_similarities(user_item_dict, user1):
    similarities = {}
    for user2 in user_item_dict:
        if user1 != user2:
            similarity = compute_similarity(user_item_dict, user1, user2)
            similarities[user2] = similarity
    return similarities

# compute the items prediction from a list of similar users                
def compute_items_prediction(user_item_dict, user1, similar_users):
    pred = {}
    mean_1 = 0
    
    items_user1 = set(user_item_dict[user1].keys())
    mean_1 = math.fsum(user_item_dict[user1][item] for item in user_item_dict[user1].keys()) / len(user_item_dict[user1].keys())
    
    for user2 in similar_users:
        items_user2 = set(user_item_dict[user2].keys())
        unrated_items = items_user2 - items_user1
        
        for item in unrated_items:
            if item not in pred.keys():
                pred[item] = compute_prediction(user_item_dict, user1, item, similar_users)
    
    return pred
        

# Compute the prediction for a single item
def compute_prediction(user_item_dict, a, item, similar_users):
    num = 0
    den = 0
    mean_a = math.fsum(user_item_dict[a][i] for i in user_item_dict[a].keys()) / len(user_item_dict[a].keys())
    set = 0
    
    for b in similar_users:
        if item in user_item_dict[b]:
            set += 1
            mean_b = sum(user_item_dict[b][i] for i in user_item_dict[b].keys()) / len(user_item_dict[b].keys())
            similarity = compute_similarity(user_item_dict, a, b)
            num += (similarity * (user_item_dict[b][item] - mean_b))
            den += similarity
    
    if den == 0:
        return mean_a
      
    else:
        prediction = mean_a + (num/den)     
    prediction = min(5, max(1, prediction))
    
    return prediction   
             
     
data_file = "ml-100k/u.data"
item_file = "ml-100k/u.item"

json_users = create_users_json(data_file)
json_items = create_item_json(item_file)


with open('user_item.json', 'w') as json_file:
    json.dump(json_users, json_file, indent=4)
    
print(f"JSON created from file: {data_file}")

with open('item.json', 'w') as json_file:
    json.dump(json_items, json_file, indent=4)
    
print(f"JSON created from file: {item_file}")

# print(json.dumps(compute_user_similarities(json_users, 196), indent=4))
# print(compute_prediction(json_users, 196, 1664))
# print(json.dumps(compute_items_prediction(json_users, 196), indent=4))
similarities = compute_user_similarities(json_users, 196)
sort_sim = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
top_sim = list(sort_sim.keys())[:30]
top_ten_sim = list(sort_sim.keys())[:10]
top_items = dict()
top_items = compute_items_prediction(json_users, 196, top_sim)
sort_items = dict(sorted(top_items.items(), key=lambda item: item[1], reverse=True))
top_ten_items_id = list(sort_items.keys())[:10]
top_ten_items_name = []

for item_id in top_ten_items_id:
    for id, name in json_items.items():
        if(id == item_id):
            top_ten_items_name.append(name)
  
print(top_ten_sim)
i = 1
for name in top_ten_items_name:
    print(f"{i}: {name}")
    i += 1
# for sim in top_ten_sim:
#     print(f"{sim} : {top_ten_sim[sim]}")
# items_predicted = compute_items_prediction(json_users, 196)
# sort_item = dict(sorted(items_predicted.items(), key=lambda item: item[1], reverse=True))
# print(json.dumps(sort_item, indent=4))
# top_ten_items = list(sort_item.keys())[:10]
# for item in top_ten_items:
#     print(f"{item} : {sort_item[item]}")
    

 


