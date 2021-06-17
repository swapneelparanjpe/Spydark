from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CrawlDropdownSelect, SimilarityPlatformSelect, LinkSimilarityKeywordSelect, ContentSimilarityKeywordSelect, ContentSimilarityLinkSelect, ContentSimilarityCustomLink, FlagLinksToTrack, LinkActivityPeriod
from django.contrib.auth.decorators import login_required

from .utils import connect_mongodb, generate_wordcloud_dynamically, Dashboard
from crawler.darkweb_crawler import DarkWebCrawler
from filters.text_process import compare_page_content
from crawler.track_links import track_links_periodically, stop_tracking
from crawler.views import get_global_variables

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
def flag_links(request):   
    set_global_variables()     
    if database is None or collection is None:
        return render(request, 'crawler/404.html', {'title':"Dashboard"})
    if database != "dark-url-db" and database != "dark-key-db":
        return render(request, 'dashboard/flag_links.html', {'title':"Flag to Track", 'service_not_valid':True})

    dash = Dashboard()
    unflagged_link_choices, current_status = dash.get_unflagged_links(database, collection)

    if len(unflagged_link_choices)<=0:
        return render(request, 'dashboard/flag_links.html', {'title':"Flag to Track", 'no_links_found':True})

    if request.method =='POST':
        flag_links_form = FlagLinksToTrack(unflagged_link_choices, request.POST)
        if flag_links_form.is_valid():
            link_choices = flag_links_form.cleaned_data.get('links')
            coll = connect_mongodb("flagged-links", "darkweb-flagged")
            flagged_links = []
            for link_choice in link_choices:
                coll.insert_one({"Link":unflagged_link_choices[int(link_choice)][1], "Status":[current_status[int(link_choice)] == "Active"], "isTracked":False})
                flagged_links.append(unflagged_link_choices[int(link_choice)][1])
            if len(link_choices)>0:
                return render(request, 'dashboard/flag_links.html', {'title':"Flag to Track", 'flagged_links':flagged_links, 'no_links_found':False, 'is_flag_done':True})
    else:
        flag_links_form = FlagLinksToTrack(unflagged_link_choices)
    return render(request, 'dashboard/flag_links.html', {'title':"Flag to Track", 'flag_links_form':flag_links_form, 'is_flag_done':False, 'no_links_found':False})


@login_required
def word_cloud(request):
    set_global_variables()
    if database is None or collection is None:
        return render(request, 'crawler/404.html', {'title':"Wordcloud"})
    if len(iterativeCrawledKeywords)>0:
        if request.method =='POST':
            form = CrawlDropdownSelect(crawled_dropdown_choices, request.POST)
            if form.is_valid():
                crawled_choice = int(form.cleaned_data.get('crawled_choice'))
                generate_wordcloud_dynamically(database, iterativeCrawledKeywords, crawled_choice)
                return render(request, 'dashboard/wordclouddash.html', {'title':"Wordcloud", 'form':form})
        else: 
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            generate_wordcloud_dynamically(database, iterativeCrawledKeywords, 0)
        return render(request, 'dashboard/wordclouddash.html', {'title':"Wordcloud", 'form':form, 'wc': True})
    return render(request, 'dashboard/wordclouddash.html', {'title':"Wordcloud"})


@login_required
def active_links(request):
    set_global_variables() 
    if database is None or collection is None:
        return render(request, 'crawler/404.html', {'title':"Active links"})
    if len(iterativeCrawledKeywords)>0:
        if request.method =='POST':
            form = CrawlDropdownSelect(crawled_dropdown_choices, request.POST)
            if form.is_valid():
                crawled_choice = int(form.cleaned_data.get('crawled_choice'))
                dash = Dashboard()
                if crawled_choice < len(iterativeCrawledKeywords):
                    a, ia = dash.active_inactive(database, iterativeCrawledKeywords[crawled_choice])
                else:
                    a, ia = 0, 0
                    for iterativeCrawledKeyword in iterativeCrawledKeywords:
                        a_this, ia_this = dash.active_inactive(database, iterativeCrawledKeyword)
                        a += a_this
                        ia += ia_this
                return render(request, 'dashboard/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links", 'form':form})
        else:
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            dash = Dashboard()
            a, ia = dash.active_inactive(database, collection)
            return render(request, 'dashboard/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links", 'form':form})
    dash = Dashboard()
    a, ia = dash.active_inactive(database, collection)
    return render(request, 'dashboard/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links"})


@login_required
def link_similarity(request):
    set_global_variables() 
    if len(iterativeCrawledKeywords)>0:
        dash = Dashboard()
        links, matrix, no_of_links, percentages, all_count = dash.display_link_similarity(database, iterativeCrawledKeywords)
        links_matrix = zip(links, matrix, percentages)
        total_links = len(links)
        keywords_nuumberOfLinks = zip(iterativeCrawledKeywords, no_of_links)
        return render(request, 'dashboard/link_similarity.html', {'title':"Link Similarity", 'collections':keywords_nuumberOfLinks, 'links_matrix':links_matrix, 'total_links':total_links, 'all_count':all_count})
    
    else:
        global platform_choice
        global selected_database
        global visited_keywords_choices
        platform_choices = [
                (0,"--Select option--"),
                (1,"Surface (URL)"),
                (2,"Google"),
                (3,"Instagram"),
                (4,"Twitter"),
                (5,"Dark web (URL)"),
                (6,"Dark web (Keyword)")
            ]
        if request.method =='POST':
            select_platform_dropdown = SimilarityPlatformSelect(platform_choices, request.POST)
            if select_platform_dropdown.is_valid():
                pltfrm_choice = select_platform_dropdown.cleaned_data.get('platform_choice')
                dash = Dashboard()
                sdb, vkc = dash.get_visited_keywords(pltfrm_choice, "link")

                if pltfrm_choice!="":
                    platform_choice = pltfrm_choice
                    selected_database = sdb
                    visited_keywords_choices = vkc
                
                select_keyword_dropdown = LinkSimilarityKeywordSelect(visited_keywords_choices, request.POST)
                if select_keyword_dropdown.is_valid():
                    keyword_choices = select_keyword_dropdown.cleaned_data.get('keyword_choice')
                    selected_collections = []
                    for keyword_choice in keyword_choices:
                        selected_collections.append(visited_keywords_choices[int(keyword_choice)][1])
                    dash_selected = Dashboard()
                    links, matrix, no_of_links, percentages, all_count = dash_selected.display_link_similarity(selected_database, selected_collections)
                    links_matrix = zip(links, matrix, percentages)
                    keywords_numberOfLinks = zip(selected_collections, no_of_links)
                    total_links = len(links)
                    if len(links)>0:
                        return render(request, 'dashboard/link_similarity.html', {'title':"Link Similarity", 'collections':keywords_numberOfLinks, 'links_matrix':links_matrix, 'total_links':total_links, 'all_count':all_count})
                return render(request, 'dashboard/link_similarity.html', {'title':"Link Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown})
        else: 
            select_platform_dropdown = SimilarityPlatformSelect(platform_choices)
        return render(request, 'dashboard/link_similarity.html', {'title':"Link Similarity", 'select_platform_dropdown':select_platform_dropdown})


@login_required
def link_tree(request):
    set_global_variables() 
    if database is None or collection is None:
        return render(request, 'crawler/404.html', {'title':"Link Tree"})
    if len(iterativeCrawledKeywords)>0:
        if request.method =='POST':
            form = CrawlDropdownSelect(crawled_dropdown_choices, request.POST)
            if form.is_valid():
                crawled_choice = int(form.cleaned_data.get('crawled_choice'))
                if crawled_choice < len(iterativeCrawledKeywords):
                    dash = Dashboard()
                    j = dash.create_tree(database, iterativeCrawledKeywords[crawled_choice])
                else:
                    j = None
                return render(request, 'dashboard/link_tree.html', {'json':j, 'title':"Link Tree", 'form':form})
        else:
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            dash = Dashboard()
            j = dash.create_tree(database, collection)
            return render(request, 'dashboard/link_tree.html', {'json':j, 'title':"Link Tree", 'form':form})
    dash = Dashboard()
    j = dash.create_tree(database, collection)
    return render(request, 'dashboard/link_tree.html', {'json':j, 'title':"Link Tree"})


@login_required
def content_similarity(request):
    set_global_variables() 

    global platform_choice
    global selected_database
    global collection_choice
    global selected_collection
    global visited_keywords_choices
    global visited_links_choices

    platform_choices = [
            (0,"--Select option--"),
            (1,"Surface (URL)"),
            (2,"Google"),
            (3,"Dark web (URL)"),
            (4,"Dark web (Keyword)")
        ]
    if request.method =='POST':

        # Custom link
        custom_link_form = ContentSimilarityCustomLink(request.POST)
        if custom_link_form.is_valid():
            custom_link = custom_link_form.cleaned_data.get('custom_link')
            if custom_link != "":
                custom_crawler = DarkWebCrawler()
                page_content = custom_crawler.get_page_content(custom_link)
                cs_matrix = compare_page_content(page_content)
                return render(request, 'dashboard/content_similarity.html', {'title':"Content Similarity", 'selected_link':custom_link, 'cs_matrix':cs_matrix})

        # Link from database
        select_platform_dropdown = SimilarityPlatformSelect(platform_choices, request.POST)
        if select_platform_dropdown.is_valid():
            pltfrm_choice = select_platform_dropdown.cleaned_data.get('platform_choice')
            dash = Dashboard()
            sdb, vkc = dash.get_visited_keywords(pltfrm_choice, "content")

            if pltfrm_choice!="":
                platform_choice = pltfrm_choice
                selected_database = sdb
                visited_keywords_choices = vkc

            select_keyword_dropdown = ContentSimilarityKeywordSelect(visited_keywords_choices, request.POST)

            if select_keyword_dropdown.is_valid():
                kw_choice = select_keyword_dropdown.cleaned_data.get('keyword_choice')
                if kw_choice != "":
                    collection_choice = kw_choice
                    selected_collection = visited_keywords_choices[int(kw_choice)][1]
                    dash = Dashboard()
                    visited_links_choices = dash.get_visited_links(selected_database, selected_collection)

                select_link_dropdown = ContentSimilarityLinkSelect(visited_links_choices, request.POST)

                if select_link_dropdown.is_valid():
                    link_choice = select_link_dropdown.cleaned_data.get('link_choice')
                    if link_choice != "":
                        selected_link = visited_links_choices[int(link_choice)][1]
                        dash = Dashboard()
                        page_content = dash.get_page_content(selected_link, selected_collection, selected_database)
                        cs_matrix = compare_page_content(page_content)
                        return render(request, 'dashboard/content_similarity.html', {'title':"Content Similarity", 'selected_link':selected_link, 'cs_matrix':cs_matrix})

                if len(visited_links_choices)>0:
                    return render(request, 'dashboard/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown, 'select_link_dropdown':select_link_dropdown})

            return render(request, 'dashboard/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown})
    else: 
        select_platform_dropdown = SimilarityPlatformSelect(platform_choices)
        custom_link_form = ContentSimilarityCustomLink()
    return render(request, 'dashboard/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'custom_link_form':custom_link_form})



@login_required
def activity_period(request):
    set_global_variables() 
    dash = Dashboard()
    flagged_link_choices = dash.get_visited_links("flagged-links", "darkweb-flagged")
    flagged_link_choices.append((len(flagged_link_choices), "All links"))

    if request.method =='POST':

        if 'track-now' in request.POST:
            msg = track_links_periodically(True)
            select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
            return render(request, 'dashboard/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'msg':msg})
        
        if 'stop-tracking' in request.POST:
            stop_tracking_link = request.POST['stop-tracking']
            msg = stop_tracking(stop_tracking_link)
            select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
            return render(request, 'dashboard/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'msg':msg})
        
        select_link_dropdown = LinkActivityPeriod(flagged_link_choices, request.POST)
        if select_link_dropdown.is_valid():
            link_choice = select_link_dropdown.cleaned_data.get('flagged_link_choices')
            selected_link = flagged_link_choices[int(link_choice)][1]
            if selected_link == "All links":
                active_links_period, inactive_links_period, percentage_activity, custom_activity_all_matrix = dash.get_all_activity_period()
                return render(request, 'dashboard/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'selected_link':selected_link, 'active_links_period':active_links_period, 'inactive_links_period':inactive_links_period, 'percentage_activity':percentage_activity, 'custom_activity_all_matrix':custom_activity_all_matrix})
            else:
                activity, percentage_activity, custom_activity_matrix = dash.get_activity_period(selected_link)
                return render(request, 'dashboard/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'selected_link':selected_link, 'activity':activity, 'percentage_activity':percentage_activity, 'custom_activity_matrix':custom_activity_matrix})
    else: 
        select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
    return render(request, 'dashboard/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown})

