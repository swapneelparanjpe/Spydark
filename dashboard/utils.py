import json
from anytree import Node
from anytree.search import find_by_attr
from anytree.exporter import JsonExporter
from crawler.utils import connect_mongodb, display_wordcloud

def generate_wordcloud_dynamically(database, collections, crawled_choice):
    if database is None or collections is None:
        return False

    wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

    if crawled_choice < len(collections):

        coll = connect_mongodb(database, collections[crawled_choice])

        if database == "instagramdb" or database == "twitterdb":
            for x in coll.find():
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")

        elif database == "dark-key-db":
            for x in coll.find():
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass

    else: 

        for collection in collections:

            coll = connect_mongodb(database, collection)

            if database == "instagramdb" or database == "twitterdb":
                for x in coll.find():
                    for hashtag in x["Hashtags"]:
                        wc_words.write(hashtag + "\n")

            elif database == "dark-key-db":
                for x in coll.find():
                    try:
                        wc_words.write(x["Page content"] + "\n\n")
                    except Exception:
                        pass

    _ = display_wordcloud(wc_words)


class Dashboard:
    def read_db(self, database, collection):
        if database is None or collection is None:
            return False
        links = []
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            links.append(x["Link"])
        return links

    def active_inactive(self, database, collection):
        if database is None or collection is None:
            return False
        coll = connect_mongodb(database, collection)
        active_links = coll.find({"Link status":"Active"}).count()        
        inactive_links = coll.find({"Link status":"Inactive"}).count()  
        return active_links, inactive_links

    def create_tree(self, database, collection):
        if database is None or collection is None:
            return False
        if database == "instagramdb" or database == "twitterdb":
            return False
        root = None
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            link = x["Link"]
            parent = x["Parent link"]
            if parent:
                p = find_by_attr(root, parent)
                Node(link, parent = p)
            else:
                root = Node(link)
                
        exporter = JsonExporter(indent=2)
        j = exporter.export(root)
        return j
    
    def display_link_similarity(self, database, collections):
        if database is None or collections is None:
            return False
        
        links_all_dictionary = {}
        links_all = []
        no_of_links = []
        for collection in collections:
            links = []
            coll = connect_mongodb(database, collection)
            for x in coll.find():
                links.append(x["Link"])
                links_all.append(x["Link"])
            links_all_dictionary[collection] = links
            no_of_links.append(len(links))

        links_all = list(set(links_all))

        result_matrix = [[0 for _ in range(len(collections)+1)] for _ in range(len(links_all))]

        percentages = []

        all_count = 0
        for link, idx_link in zip(links_all, range(len(links_all))):
            for collection, idx_col in zip(collections, range(len(collections))):
                if link in links_all_dictionary[collection]:
                    result_matrix[idx_link][idx_col] = 1
            percentages.append(format(sum(100*result_matrix[idx_link])/len(collections), "0.2f") + "%")
            if sum(result_matrix[idx_link]) == len(collections):
                result_matrix[idx_link][-1] = 1
                all_count += 1
        
        return links_all, result_matrix, no_of_links, percentages, all_count

    def get_visited_keywords(self, platform_choice, link_or_content):
        database = None
        collection = None
        field = None
        if platform_choice == "1":
            database = "surfacedb"
            collection = "seed-urls-visited"
            field = "seed-url"
        elif platform_choice == "2":
            database = "googledb"
            collection = "keywords-visited"
            field = "keyword"
        elif platform_choice == "3":
            database = "instagramdb"
            collection = "keywords-visited"
            field = "keyword"
        elif platform_choice == "4":
            database = "twitterdb"
            collection = "keywords-visited"
            field = "keyword"
        elif platform_choice == "5":
            database = "dark-url-db"
            collection = "seed-urls-visited"
            field = "seed-url"
        else:
            database = "dark-key-db"
            collection = "keywords-visited"
            field = "Keyword"

        if link_or_content == "content":
            visited_keywords_choices = [(0,"--Select option--")]
            count = 1
        else:
            visited_keywords_choices = []
            count = 0

        coll = connect_mongodb(database, collection)
        for x in coll.find():
            visited_keywords_choices.append((count, x[field]))
            count += 1
        return database, visited_keywords_choices

    def get_visited_links(self, database, collection):
        if database is None or collection is None:
            return False
        visited_links_choices = [(0,"--Select option--")]
        count = 1
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            visited_links_choices.append((count, x["Link"]))
            count += 1
        return visited_links_choices

    
    def get_page_content(self, link, collection, database):
        coll = connect_mongodb(database, collection)
        page_content = coll.find_one({"Link":link})["Page content"]
        return page_content

    def get_link_data(self, link, collection, database):
        coll = connect_mongodb(database, collection)
        document = coll.find_one({"Link":link})
        try:
            wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')
            wc_words.write(document["Page content"])
            _ = display_wordcloud(wc_words)
            image_urls = coll.find_one({"Link":link})["Images"]
        except Exception:
            print("Page was not found")
            return list(document.items())[1:], []
        return list(document.items())[1:], image_urls

    def get_activity_period(self, link):
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        activity = coll.find_one({"Link":link})["Status"]
        percentage_activity = format(100*sum(activity)/len(activity), "0.2f")
        activity = json.dumps(activity)

        custom_activity = coll.find_one({"Link":link})["Custom"][0]
        custom_activity_matrix = []
        for key, value in custom_activity.items():
            custom_activity_matrix.append([key.split()[0], key.split()[1], "Active" if value else "Inactive"])

        return activity, percentage_activity, custom_activity_matrix

    def get_all_activity_period(self):
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        all_status = []
        max_length = -1
        custom_activity_all_matrix = []
        for x in coll.find():
            all_status.append(x["Status"][::-1])
            custom_activity_status = x["Custom"][0]
            custom_link_status_matrix = []
            for key, value in custom_activity_status.items():
                custom_link_status_matrix.append([key.split()[0], key.split()[1], "Active" if value else "Inactive"])
            custom_activity_all_matrix.append([x["Link"], len(custom_link_status_matrix)+1, custom_link_status_matrix])
            if len(x["Status"]) > max_length:
                max_length = len(x["Status"])

        active_links_period = []
        inactive_links_period = []
        for day in range(max_length):
            no_of_links = 0
            no_of_active_links = 0
            for status_idx in range(len(all_status)):
                try:
                    status = all_status[status_idx][day]
                    no_of_links += 1
                    no_of_active_links += status
                except Exception:
                    pass
            no_of_inactive_links = no_of_links - no_of_active_links
            active_links_period.append(no_of_active_links)
            inactive_links_period.append(no_of_inactive_links)

        percentage_activity = format(100*sum(active_links_period)/(sum(active_links_period) + sum(inactive_links_period)), "0.2f")
        active_links_period = json.dumps(active_links_period[::-1])
        inactive_links_period = json.dumps(inactive_links_period[::-1])
        return active_links_period, inactive_links_period, percentage_activity, custom_activity_all_matrix
        

    def get_unflagged_links(self, database, collection):
        if database is None or collection is None:
            return False

        flagged_links = []
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        for x in coll.find():
            flagged_links.append(x["Link"])

        unflagged_link_choices = []
        current_status = []
        count = 0
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            if x["Link"] not in flagged_links:
                unflagged_link_choices.append((count, x["Link"]))
                current_status.append(x["Link status"])
                count += 1

        return unflagged_link_choices, current_status
