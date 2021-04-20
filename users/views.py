from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SearchURL, SearchKeyword, SearchKeywordPlt, CrawlDropdownSelect, SimilarityPlatformSelect, LinkSimilarityKeywordSelect, ContentSimilarityKeywordSelect, ContentSimilarityLinkSelect, ContentSimilarityCustomLink, FlagLinksToTrack, LinkActivityPeriod
from django.contrib.auth.decorators import login_required

from .utils import connect_mongodb, get_link_data, addhistory, get_images, get_text, generate_wordcloud_dynamically, Dashboard, SurfaceURL, Google, Instagram, Twitter
from .minicrawlbot import MiniCrawlbot
from .img_detect import detect_object
from .text_process import detect_text, compare_page_content
from .track_links import track_links_periodically, stop_tracking

# for passing arguments in redirect
from django.urls import reverse
from urllib.parse import urlencode
from datetime import datetime
import time

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

def register(request):
    if request.method =='POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.info(request, f'Account created for {username}! Log In now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form, 'title':"Register Now"})    

@login_required
def welcome(request):
    msg = track_links_periodically(False)
    if msg != None:
        messages.info(request, f'{msg}')
    return render(request, 'users/welcome.html', {'title':"Home", 'msg':msg})

@login_required
def dashboard(request):
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

    if request.method == "POST":
        if "show_link_data" in request.POST:
            link = request.POST["show_link_data"]
            document = get_link_data(database, collection, link)
            return render(request, 'users/dashboard.html', {'title':"Dashboard", "document":document})

        else:
            database = None
            collection = None
            iterativeCrawledKeywords = []
            crawled_dropdown_choices = []

            platform_choice = None
            selected_database = None
            visited_keywords_choices = []

            collection_choice = None
            selected_collection = None
            visited_links_choices = []
        
    if database is None or collection is None:
        return render(request, 'users/404.html', {'title':"Dashboard"})
    dash = Dashboard()
    links = dash.read_db(database, collection)
    return render(request, 'users/dashboard.html', {'links':links, 'title':"Dashboard"})


@login_required
def flag_links(request):        
    if database is None or collection is None:
        return render(request, 'users/404.html', {'title':"Dashboard"})
    if database != "dark-url-db" and database != "dark-key-db":
        return render(request, 'users/flag_links.html', {'title':"Flag to Track", 'service_not_valid':True})

    dash = Dashboard()
    unflagged_link_choices, current_status = dash.get_unflagged_links(database, collection)

    if len(unflagged_link_choices)<=0:
        return render(request, 'users/flag_links.html', {'title':"Flag to Track", 'no_links_found':True})

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
                return render(request, 'users/flag_links.html', {'title':"Flag to Track", 'flagged_links':flagged_links, 'no_links_found':False, 'is_flag_done':True})
    else:
        flag_links_form = FlagLinksToTrack(unflagged_link_choices)
    return render(request, 'users/flag_links.html', {'title':"Flag to Track", 'flag_links_form':flag_links_form, 'is_flag_done':False, 'no_links_found':False})


@login_required
def word_cloud(request):
    if database is None or collection is None:
        return render(request, 'users/404.html', {'title':"Wordcloud"})
    if len(iterativeCrawledKeywords)>0:
        if request.method =='POST':
            form = CrawlDropdownSelect(crawled_dropdown_choices, request.POST)
            if form.is_valid():
                crawled_choice = int(form.cleaned_data.get('crawled_choice'))
                generate_wordcloud_dynamically(database, iterativeCrawledKeywords, crawled_choice)
                return render(request, 'users/wordclouddash.html', {'title':"Wordcloud", 'form':form})
        else: 
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            generate_wordcloud_dynamically(database, iterativeCrawledKeywords, 0)
        return render(request, 'users/wordclouddash.html', {'title':"Wordcloud", 'form':form, 'wc': True})
    return render(request, 'users/wordclouddash.html', {'title':"Wordcloud"})


@login_required
def active_links(request):
    if database is None or collection is None:
        return render(request, 'users/404.html', {'title':"Active links"})
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
                return render(request, 'users/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links", 'form':form})
        else:
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            dash = Dashboard()
            a, ia = dash.active_inactive(database, collection)
            return render(request, 'users/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links", 'form':form})
    dash = Dashboard()
    a, ia = dash.active_inactive(database, collection)
    return render(request, 'users/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links"})


@login_required
def link_similarity(request):
    if len(iterativeCrawledKeywords)>0:
        dash = Dashboard()
        links, matrix, no_of_links, percentages, all_count = dash.display_link_similarity(database, iterativeCrawledKeywords)
        links_matrix = zip(links, matrix, percentages)
        total_links = len(links)
        keywords_nuumberOfLinks = zip(iterativeCrawledKeywords, no_of_links)
        return render(request, 'users/link_similarity.html', {'title':"Link Similarity", 'collections':keywords_nuumberOfLinks, 'links_matrix':links_matrix, 'total_links':total_links, 'all_count':all_count})
    
    else:
        global platform_choice
        global selected_database
        global visited_keywords_choices
        platform_choices = [
                (0,"--Select option--"),
                (1,"Surface (URL)"),
                (2,"Instagram"),
                (3,"Twitter"),
                (4,"Dark web (URL)"),
                (5,"Dark web (Keyword)")
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
                        return render(request, 'users/link_similarity.html', {'title':"Link Similarity", 'collections':keywords_numberOfLinks, 'links_matrix':links_matrix, 'total_links':total_links, 'all_count':all_count})
                return render(request, 'users/link_similarity.html', {'title':"Link Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown})
        else: 
            select_platform_dropdown = SimilarityPlatformSelect(platform_choices)
        return render(request, 'users/link_similarity.html', {'title':"Link Similarity", 'select_platform_dropdown':select_platform_dropdown})


@login_required
def link_tree(request):
    if database is None or collection is None:
        return render(request, 'users/404.html', {'title':"Link Tree"})
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
                return render(request, 'users/link_tree.html', {'json':j, 'title':"Link Tree", 'form':form})
        else:
            form = CrawlDropdownSelect(crawled_dropdown_choices)
            dash = Dashboard()
            j = dash.create_tree(database, collection)
            return render(request, 'users/link_tree.html', {'json':j, 'title':"Link Tree", 'form':form})
    dash = Dashboard()
    j = dash.create_tree(database, collection)
    return render(request, 'users/link_tree.html', {'json':j, 'title':"Link Tree"})


@login_required
def content_similarity(request):

    global platform_choice
    global selected_database
    global collection_choice
    global selected_collection
    global visited_keywords_choices
    global visited_links_choices

    platform_choices = [
            (0,"--Select option--"),
            (1,"Surface (URL)"),
            (4,"Dark web (URL)"),
            (5,"Dark web (Keyword)")
        ]
    if request.method =='POST':

        # Custom link
        custom_link_form = ContentSimilarityCustomLink(request.POST)
        if custom_link_form.is_valid():
            custom_link = custom_link_form.cleaned_data.get('custom_link')
            if custom_link != "":
                custom_crawler = MiniCrawlbot()
                page_content = custom_crawler.get_page_content(custom_link)
                cs_matrix = compare_page_content(page_content)
                return render(request, 'users/content_similarity.html', {'title':"Content Similarity", 'selected_link':custom_link, 'cs_matrix':cs_matrix})

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
                        return render(request, 'users/content_similarity.html', {'title':"Content Similarity", 'selected_link':selected_link, 'cs_matrix':cs_matrix})

                if len(visited_links_choices)>0:
                    return render(request, 'users/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown, 'select_link_dropdown':select_link_dropdown})

            return render(request, 'users/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'select_keyword_dropdown':select_keyword_dropdown})
    else: 
        select_platform_dropdown = SimilarityPlatformSelect(platform_choices)
        custom_link_form = ContentSimilarityCustomLink()
    return render(request, 'users/content_similarity.html', {'title':"Content Similarity", 'select_platform_dropdown':select_platform_dropdown, 'custom_link_form':custom_link_form})



@login_required
def activity_period(request):
    dash = Dashboard()
    flagged_link_choices = dash.get_visited_links("flagged-links", "darkweb-flagged")
    flagged_link_choices.append((len(flagged_link_choices), "All links"))

    if request.method =='POST':

        if 'track-now' in request.POST:
            msg = track_links_periodically(True)
            select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
            return render(request, 'users/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'msg':msg})
        
        if 'stop-tracking' in request.POST:
            stop_tracking_link = request.POST['stop-tracking']
            msg = stop_tracking(stop_tracking_link)
            select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
            return render(request, 'users/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'msg':msg})
        
        select_link_dropdown = LinkActivityPeriod(flagged_link_choices, request.POST)
        if select_link_dropdown.is_valid():
            link_choice = select_link_dropdown.cleaned_data.get('flagged_link_choices')
            selected_link = flagged_link_choices[int(link_choice)][1]
            if selected_link == "All links":
                active_links_period, inactive_links_period, percentage_activity, custom_activity_all_matrix = dash.get_all_activity_period()
                return render(request, 'users/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'selected_link':selected_link, 'active_links_period':active_links_period, 'inactive_links_period':inactive_links_period, 'percentage_activity':percentage_activity, 'custom_activity_all_matrix':custom_activity_all_matrix})
            else:
                activity, percentage_activity, custom_activity_matrix = dash.get_activity_period(selected_link)
                return render(request, 'users/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown, 'selected_link':selected_link, 'activity':activity, 'percentage_activity':percentage_activity, 'custom_activity_matrix':custom_activity_matrix})
    else: 
        select_link_dropdown = LinkActivityPeriod(flagged_link_choices)
    return render(request, 'users/activity_period.html', {'title':"Activity Period", 'select_link_dropdown':select_link_dropdown})




@login_required
def surface(request):
    global iterativeCrawledKeywords
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            iterativeCrawledKeywords = []
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3

            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            code = "surface_url"
            query_string =  urlencode({'url': url, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeywordPlt(request.POST)
        if form2.is_valid():
            iterativeCrawledKeywords = []
            keyword = form2.cleaned_data.get('keyword')
            platform = form2.cleaned_data.get('platform')
            pages = form2.cleaned_data.get('depth_key')
            isIterative = form2.cleaned_data.get('isIterative')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "surface_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'platform':platform, 'depth':depth,'isIterative':isIterative, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

    else:
        form2 = SearchKeywordPlt()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/surface.html', {'form1':form1, 'form2':form2, 'title':"Surface web Crawl"})
 
     
@login_required
def dark(request):
    global iterativeCrawledKeywords
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            iterativeCrawledKeywords = []
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3
            code = "dark_url"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'url': url, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            iterativeCrawledKeywords = []
            keyword = form2.cleaned_data.get('keyword')
            pages = form2.cleaned_data.get('depth_key')
            isIterative = form2.cleaned_data.get('isIterative')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "dark_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'depth':depth, 'isIterative':isIterative, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form2 = SearchKeyword()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/dark.html', {'form1':form1, 'form2':form2, 'title':"Dark web Crawl"})

# Crawling thorugh URLs    
@login_required
def crawled(request):
    start_time = datetime.now()
    code = request.GET.get('code')
    isIterative = request.GET.get('isIterative') == "True"

    global database
    global collection 
    global iterativeCrawledKeywords
    global crawled_dropdown_choices

    if code == 'surface_url':
        url = request.GET.get('url')
        depth = int(request.GET.get('depth'))
        crawler = SurfaceURL(url, depth)
        links, topFiveWords = crawler.surfacecrawl()
        database = "surfacedb"
        collection = url
        data = {"Platform": "Surface URL", "Seed URL": url, "Depth":depth}

    if code == 'surface_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        platform = int(request.GET.get('platform'))
        collection = keyword

        if isIterative:
            iterativeCrawledKeywords.append(keyword)
        else: 
            iterativeCrawledKeywords = []

        if platform == 1:
            ggl = Google(keyword, depth)
            links, topFiveWords = ggl.googlecrawl()
            database = "googledb"
            data = {"Platform": "Google", "Keyword": keyword, "Depth":depth}

        if platform == 2:
            ig = Instagram(keyword, depth)
            links, topFiveWords = ig.instacrawl()
            database = "instagramdb"
            data = {"Platform": "Instagram", "Keyword": keyword, "Depth":depth}
            
        if platform == 3:
            tweet = Twitter(keyword, depth)
            links, topFiveWords = tweet.twittercrawl()
            database = "twitterdb"
            data = {"Platform": "Twitter", "Keyword": keyword, "Depth":depth}

    if code == 'dark_url':
        url = request.GET.get('url')
        depth = int(request.GET.get('depth'))
        minicrawl = MiniCrawlbot()
        links, topFiveWords = minicrawl.tor_crawler(url, depth, False)
        database = "dark-url-db"
        collection = url
        data = {"Platform": "Dark Web URL", "Seed URL": url, "Depth":depth}

    if code == 'dark_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        minicrawl = MiniCrawlbot()
        links, topFiveWords = minicrawl.tor_crawler(keyword, depth, True)
        database = "dark-key-db"
        collection = keyword
        data = {"Platform": "Dark Web Keyword", "Keyword": keyword, "Depth":depth}
        if isIterative:
            iterativeCrawledKeywords.append(keyword)
        else: 
            iterativeCrawledKeywords = []
        
    addhistory(request.user.username, data)

    end_time = datetime.now()
    diff = end_time - start_time
    time_elapsed = str(diff)[2:11]

    # Get next iteration
    full_path = request.get_full_path()
    urlSub1 = full_path.split("=", 1)[0] + "="
    urlSub2 = "&" + full_path.split("&", 1)[1]

    wordUrls = []
    for word in topFiveWords:
        wordUrls.append(word.replace(" ", "+"))

    topWords = zip(topFiveWords, wordUrls)

    if len(iterativeCrawledKeywords) == 5:
        isIterative = False
    
    if len(iterativeCrawledKeywords)>0:
        crawled_dropdown_choices = []
        count = 0
        for iterativeCrawledKeyword in iterativeCrawledKeywords:
            crawled_dropdown_choices.append((count, iterativeCrawledKeyword))
            count += 1
        crawled_dropdown_choices.append((count, "All words together"))


    return render(request, 'users/crawled.html', {'links':links, 'time_elapsed':time_elapsed, 'isIterative':isIterative, 'topWords':topWords, 'urlSub1':urlSub1, 'urlSub2':urlSub2, 'title':"Crawling reults"})
    

@login_required
def img_processing(request):
    links_images = get_images(database, collection)
    related_links = []
    for link_image in links_images:
        detected = False
        link, img_link = link_image
        print("Processing: ", link)
        if isinstance(img_link, str):
            detected = detect_object(img_link)
        elif isinstance(img_link, list):
            for img in img_link:
                detected = detect_object(img)
                if detected:
                    break
        if detected:
            related_links.append(link)

    return render(request, 'users/img_process.html', {'related_links':related_links, 'title':"Image Processing"})

@login_required
def text_processing(request):
    links_texts = get_text(database, collection)
    related_links = []
    for link_text in links_texts:
        detected = False
        link, text = link_text
        detected = detect_text(text)
        if detected:
            related_links.append(link)

    return render(request, 'users/text_process.html', {'related_links':related_links, 'title':"Text Processing"})