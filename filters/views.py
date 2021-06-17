from django.shortcuts import render
from django.contrib import messages
from .img_detect import detect_object
from .text_process import detect_text
from .utils import get_images, get_text, delete_gridfs_image
from crawler.views import get_global_variables
from django.contrib.auth.decorators import login_required
from crawler.utils import connect_gridfs


database = None
collection = None
iterativeCrawledKeywords = []
crawled_dropdown_choices = []

platform_choice = None
selected_database = None
collection_choice = None
selected_collection = None
visited_keywords_choices = []
visited_links_choices = [] 

def set_global_variables():
    global database
    global collection
    global iterativeCrawledKeywords
    global crawled_dropdown_choices
    global platform_choice
    global selected_database
    global collection_choice
    global selected_collection
    global visited_keywords_choices
    global visited_links_choices

    database, collection, iterativeCrawledKeywords, crawled_dropdown_choices, platform_choice, selected_database, collection_choice, selected_collection, visited_keywords_choices, visited_links_choices = get_global_variables()


@login_required
def img_processing(request):
    set_global_variables()
    coll, links_images, coll_fs_files = get_images(database, collection)
    fs = connect_gridfs(database)
    related_links = []
    for link_image in links_images:
        is_link_relevant = False
        link, images = link_image
        print("Processing: ", link)
        for idx in range(len(images)):
            if detect_object(fs, images[idx][0]):
                images[idx][1] = True
                is_link_relevant = True
            else:
                delete_gridfs_image(coll_fs_files, fs, images[idx][0])
        if is_link_relevant:
            related_links.append(link)
            coll.update_one({"Link":link}, {"$set":{"Images":images}})
        # TODO: Uncomment below else block
        # else:
        #     coll.delete_one({"Link":link})
        
    messages.info(request, f'These are your results after image processing...')
    return render(request, 'filters/img_process.html', {'related_links':related_links, 'no_of_links':len(related_links), 'title':"Image Processing"})

@login_required
def text_processing(request):
    set_global_variables()
    coll, links_texts = get_text(database, collection)
    related_links = []
    for link_text in links_texts:
        link, text = link_text
        if detect_text(text):
            related_links.append(link)
        # TODO: Uncomment below else block
        # else:
            # coll.delete_one({"Link":link})

    messages.info(request, f'These are your results after text processing...')
    return render(request, 'filters/text_process.html', {'related_links':related_links, 'no_of_links':len(related_links), 'title':"Text Processing"})
