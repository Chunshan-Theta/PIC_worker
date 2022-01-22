import json
user_data, story_data = {}, {}
with open("./util/dots_vec.json") as json_file:
    user_data = json.load(json_file)

with open("./util/story_data.json") as json_file:
    story_data = json.load(json_file)

def reduce_dimansion(arr, tarage_dimansion=1):
    if len(arr) <= tarage_dimansion:
        return arr

    new_array = []
    for d in range(0, len(arr) - 1):
        new_array.append(arr[d + 1] - arr[d])

    return reduce_dimansion(new_array, tarage_dimansion)


def get_dots(d=2, story_id="1015"):
    dots = []
    for user_name, use_data in user_data.items():
        # use_data_vec = [[value_zone_change(unit) for unit in use_data[store_id]] if store_id in use_data else [-1] for store_id in store_list]
        if story_id not in use_data:
            continue
        else:
            # print(use_data)
            use_data_vec = use_data[story_id]

            # use_data_vec_one = combine_dimansion(use_data_vec)
            # use_data_vec_xy = reduce_dimansion(combine_dimansion(use_data_vec),d)
            use_data_vec_xy = reduce_dimansion(use_data_vec, d)
            dots.append((user_name, use_data_vec_xy))

    return dots

def get_templete_dots(d=2, story_id="1015"):
    dots = []
    if story_id in story_data:
        for content, vec in story_data[story_id].items():

            use_data_vec_xy = reduce_dimansion(vec, d)
            dots.append((content, use_data_vec_xy))

    return dots
# print(get_dots())
# print(get_templete_dots())