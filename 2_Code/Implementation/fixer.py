from bs4 import BeautifulSoup,Tag
import re
import os
from langdetect import detect
import numpy as np
import wcag_contrast_ratio as contrast
from matplotlib import colors
import os
import azure.ai.vision as sdk
from deep_translator import GoogleTranslator
import requests
import time

def run(file,url):

    ##############
    # Setup
    ##############

    ## Needs to be set up for every page
    
    ### FIX THIS
    url = url

    html_in = open(f"./{file}", "r", encoding="utf-8")
    html_out = open(f"./out/{file}", "w", encoding="utf-8")
    soup = BeautifulSoup(html_in, 'html.parser')


    ##############
    # Setup for Functions
    ##############
    service_options = sdk.VisionServiceOptions("https://ai-tagging-ma.cognitiveservices.azure.com/",os.environ["VISION_KEY"])

    analysis_options = sdk.ImageAnalysisOptions()

    analysis_options.features = (sdk.ImageAnalysisFeature.CAPTION)

    analysis_options.language = "en"

    ### Logging

    website_log = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,file]



    ##############
    # Functions
    ##############

    def has_style(tag):
        return tag.has_attr('style')


    def with_id(tag):
        return tag.has_attr('id') 


    def has_handler(tag):
        return (tag.has_attr('onmouseover') and not tag.has_attr('onfocus')) or tag.has_attr('ondblclk') or tag.has_attr('onclick')


    def has_title(tag):
        return tag.has_attr('title')


    def color_to_rgb(color):
        try:
            if(color.find("rgb") > -1):
                #Check division!
                color = color[color.find("rgb")+4:-1]
                color = tuple(map(int, color.split(', ')))
                color = tuple(ti/255 for ti in color)
            else:
                color = colors.to_rgb(color.strip())
        except:
            color = "Failed"
            website_log[23] = website_log[23] + 1

        return color


    def has_bg_color(tag):
        return tag.has_attr('style') and "background-color:" in tag["style"]

    def has_color(tag):
        return tag.has_attr('style') and "color:" in tag["style"]

    def get_text_color(tag):
        if tag.has_attr("style"):
            style = str(tag["style"]).replace("background-color:","")
            if "color" in style:
                loc_1 = style.find("color:") +6
                loc_2 = style.find(";",loc_1)
                if loc_2 == -1:
                    loc_2 = len(style)
                style = color_to_rgb( style[loc_1:loc_2])
            else:
                style = [0,0,0]
        else:
            style = [0,0,0]
        return style


    def get_alt_text(Link):
    # FIX THIS
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("Start : %m/%d/%Y, %H:%M:%S", named_tuple)
        if "http" not in Link:
            Link = url + "/" + Link
        print(f"ALT TEXT AT: {time_string} {Link}")
        try:
            vision_source = sdk.VisionSource(
            url=Link)
            image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)
        
            result = image_analyzer.analyze()
            if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:

                if result.caption is not None:
                    translated = GoogleTranslator(source='en', target='de').translate(text=result.caption.content)
                    return translated
                else:
                    website_log[26] = website_log[26] + 1
                    print(f"ALT Creation did not work {Link}")
                    return "ALT Creation did not work"
        except:
            website_log[26] = website_log[26] + 1
            print(f"ALT Creation did not work {Link}")
            return "ALT Creation did not work"





    def get_link_info(Link):
        ## FIX THIS
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("Start : %m/%d/%Y, %H:%M:%S", named_tuple)
        if "http" not in Link:
            Link = url + "/" + Link
        print(f"Link info AT: {time_string} {Link}")
        try:
            r = requests.get(Link, timeout = 5)
            soupy = BeautifulSoup(r.content, features="lxml")
   
            info = soupy.title.string

            meta = soupy.find_all('meta')

            for tag in meta:
                if(tag.get('name') == "description"):
                    if len(tag.get('content'))< 150:
                        info = tag.get('content')
        except:
            website_log[25] = website_log[25] + 1
            info = Link[Link.find("://")+3:Link.find("/")].replace(".","")


        return info


    #### Lists all Children

    def list_children(tag):
        list = [tag]
        contents = tag.contents
        for child in contents:     
            if isinstance(child,Tag):
                list.extend(list_children(child))
        return list


    #### Lists all Children that dont have their own background color
    #### All Children in this array have the bg_color of their parent


    def list_children_nobg(tag):
        list = [tag]
        contents = tag.contents
        for child in contents:     
            if isinstance(child,Tag):
                if child.has_attr("style"):
                    if "background-color" not in child["style"] :
                        list.extend(list_children(child))
                else:
                    list.extend(list_children(child))
        return list

    ##############
    # Website Fix
    ##############

    #### Fix missing ALT Tags

    images = soup.find_all('img')

    for image in images:
        if image.has_attr("src") and not image.has_attr("alt"):
            source = image["src"]
            if "http" not in source:
                source = url + source 
            image["alt"] = get_alt_text(source)
            website_log[0] = website_log[0]+1


    ### Link Empty
    ### Searches for Empty Link 

    links = soup.find_all("a")

    for link in links:
        if(link != None and link.string == None and link.has_attr("href")):
            try:
                link.string = get_link_info(link["href"])
                website_log[1] = website_log[1]+1
            except:
                website_log[1] = website_log[1]


    
    #### H1_missing

    h1= soup.find('h1')
    if h1 == None:
        #find first heading
        heading = soup.find_all(re.compile("^h[1-6]$"))
        if heading != []:
            heading = heading[0]
            previous_name = heading.name
            heading.name = "h1"
            if not heading.has_attr("class"):
                heading["class"] = previous_name
            website_log[2] = website_log[2]+1


    ### Heading Empty

    headings = soup.find_all(re.compile("^h[1-6]$"))
    for heading in headings:
        if heading.string == None:
            heading.extract()
            website_log[3] = website_log[3]+1



    ### Heading Skipped

    i = 6
    heading_prev = []
    while i > 0:
        heading = soup.find_all(f"h{i}")
        if(heading != []):
            heading_prev = heading
            while i > 1:
                i = i - 1
                heading = soup.find_all(f"h{i}")
                if(heading == []):
                    if heading_prev != []:
                        for move_heading in heading_prev:
                            move_heading.name = f"h{i}"
                            if not move_heading.has_attr("class"):
                                move_heading["class"] = f"h{i+1}"
                    website_log[4] = website_log[4]+1
        i = i-1


    ### Button Empty
    buttons = soup.find_all("button")
    for button in buttons:
        if button.string == None:
            button.string = "Button"
            website_log[5] = website_log[5]+1



    ### Language_missing

    html_tag = soup.find("html")
    if html_tag != None and not html_tag.has_attr("lang"):
        language = soup.find("p")
        if language != None:
            language = language.getText().strip()
            language = detect(language)
            html_tag["lang"] = language
            website_log[6] = website_log[6]+1
        
    # ### Region missing

    ### Regions can not be automatically defined in this thesis - mögliche ansätze angeben

    ### Table_layout
    tables = soup.find_all("table")

    for table in tables:
        header = table.find_all("th")
        if header == []:
            to_add = soup.new_tag("p")
            rows = table.find_all("tr")
            for row in rows:
                ## Add line Break
                cells = row.find_all("td")
                for cell in cells:
                    cell.name = "span"
                    if cell.has_attr("style"):
                        cell["style"] = cell["style"] + ";display:inline-block;"
                    else:
                        cell["style"] = ";display:inline-block;"
                    to_add.append(cell)
                to_add.append(soup.new_tag("br"))
            table.previous_sibling.insert_after(to_add)
            table.extract()
            website_log[8] = website_log[8]+1

    ### Noscript

    noscript = soup.find_all("noscript")
    if noscript != []:
        for element in noscript:
            element.extract()
        website_log[9] = website_log[9]+1

    ### ALT_suspicious

    images = soup.find_all('img')

    for image in images:
        try:
            alt_text = str(image["alt"])
            if len(alt_text) < 10:
                source = image["src"]
                if "http" not in source:
                    source = url + source 
                image["alt"] = get_alt_text(source)
                website_log[10] = website_log[10]+1
            elif any(re.findall(r'.jp|.JP|.pn|.PN|http', alt_text, re.IGNORECASE)):
                source = image["src"]
                if "http" not in source:
                    source = url + source 
                image["alt"] = get_alt_text(source)
                website_log[10] = website_log[10]+1
        except:
            website_log[10] = website_log[10]


    # ### Event_handler

    event_handler = soup.find_all(has_handler)

    for element in event_handler:
        if(element.has_attr('onmouseover')):
            element["onfocus"] = element['onmouseover']
            website_log[11] = website_log[11]+1
        if(element.has_attr('onmouseout')):
            element["onfocusout"] = element['onmouseout']
            website_log[11] = website_log[11]+1
        if(element.has_attr('onclick')):
            element["onfocus"] = element['onclick']
            website_log[11] = website_log[11]+1
        elif(element.has_attr('ondblclk')):
            element["onfocus"] = element['onclick']
            website_log[11] = website_log[11]+1    




    #### Text_justified

    with_style = soup.find_all(has_style)

    for element in with_style:
        if "text-align: justify" in element["style"] and len(element.string) > 500:
            element["style"] = element["style"].replace("text-align: justify","")
            website_log[12] = website_log[12]+1

    ### Text Small & heading_possible

    with_style = soup.find_all(has_style)

    ## Check heading level
    level = 6
    while soup.find_all(f"h{level}") == [] and level >0:
        level -= 1

    if level < 6:
        level +=1

    for element in with_style:
        if "font-size:" in element["style"]:
            size = str(element["style"])
            size = size[size.find("font-size:")+11:size.find("px;")]
            try:
                size = float(size)
            except:
                website_log[24] = website_log[24]+1
                size = 12
            if(size < 11):
                if size < 1:
                    element.extract()
                else:
                    element["style"] = element["style"] + ";font-size:12px"
                website_log[13] = website_log[13]+1
            elif(size > 19 and len(element) < 50):
                website_log[14] = website_log[14]+1
                element.name = f"h{level}"

            elif(size > 15 and ("<b>" in str(element) or "<it>" in str(element)) and len(element) < 50):
                website_log[14] = website_log[14]+1
                element.name = f"h{level}"




    ### Link_internal_broken

    links = soup.find_all("a")
    targets = soup.find_all(with_id)
    for link in links:
        if link.has_attr("href") and len(link["href"])>2 and link["href"][0] == "#":
            internal_link = link["href"]
            if f'"{internal_link[1:]}"' in str(targets):
                  # No console output
                website_log[15] = website_log[15]
            else:
                link.extract()
                website_log[15] = website_log[15]+1



    ### Link_redundant
    links = soup.find_all("a")
    i = 0
    while i < len(links)-1:
        if(links[i].has_attr("href") and links[i+1].has_attr("href") and links[i]["href"] == links[i+1]["href"]):
            if len(links[i].contents[0]) > len(links[i+1].contents[0]):
                links[i].extract()
            else:
                links[i+1].extract()
            website_log[16] = website_log[16]+1
        i +=1    

    ### alt_duplicate
    images = soup.find_all("img")
    i = 0
    while i < len(images)-1:
        if(images[i].has_attr("alt") and images[i+1].has_attr("alt") and images[i].has_attr("src") and images[i+1].has_attr("src")):
            if(images[i]["alt"] == images[i+1]["alt"]):
                if(images[i]["src"] != images[i+1]["src"]):
                    source = images[i]["src"]
                    if "http" not in source:
                        source = url + source 
                    images[i]["alt"] = get_alt_text(source)
                    website_log[17] = website_log[17]+1
        i +=1    


    ### Link_suspicious

    links = soup.find_all("a")

    for link in links:
        if any(re.findall(r'click|klicken|weiter lesen|lesen|mehr|details|www.|.com|.de|Link', link.text, re.IGNORECASE)) and link.has_attr("href"):
            link.string = get_link_info(link["href"])
            website_log[18] = website_log[18]+1

    ### Label missing

    ### This requires user input on input function

    forms = soup.find_all("form")
    input_name = 1
    for form in forms:
        inputs = form.find_all("input")
        labels = form.find_all("label")
        
        for input in inputs:
            if input.has_attr("type") and input["type"] not in ["image","submit","reset","button","hidden"]:
                if not input.has_attr("id"):
                    input["id"] = f"Input{input_name}"
                    label = soup.new_tag("label")
                    label["for"] = f"Input{input_name}"
                    label.string = "Input for: " + input["type"]
                    input.insert_before(label)
                    input_name = input_name + 1
                    website_log[19] = website_log[19]+1
                elif input["id"] not in str(labels):
                    label = soup.new_tag("label")
                    label["for"] = input["id"]
                    label.string = "Input for: " + input["type"]
                    input.insert_before(label)
                    website_log[19] = website_log[19]+1
                    

    ### Title Redundant


    titles = soup.find_all(has_title)
    if titles != []:
        for title in titles:
            if title != None and title.has_attr("alt") and title.has_attr("title") and title["title"] != None and title["alt"] != None:
                if title["title"] in title["alt"]:
                    del title["title"]
                    website_log[20] = website_log[20]+1
            elif  title != None and title["title"] in str(title.contents):
                del title["title"]
                website_log[20] = website_log[20]+1



    #### Alt Redundant

    images = soup.find_all("img")
    if images != [] and images != None:
        for image in images:
            if image.has_attr("alt") and image.has_attr("src"):
                try:
                    if(image["alt"] in str(image.previous_sibling) or image["alt"] in str(image.next_sibling)):
                        source = image["src"]
                        if "http" not in source:
                            source = url + source 
                        image["alt"] = get_alt_text(source)
                        website_log[21] = website_log[21]+1
                except:
                    website_log[21] = website_log[21]


    ### Contrast


    with_bg = soup.find_all(has_bg_color)
    if(with_bg == []):
        with_bg = list_children(soup)
        color_bg = [1,1,1]
        body = soup.find("body")
        if body.has_attr("style"):
            body["style"] = body["style"] + (";background-color:white;") 
        else:
            body["style"] = "background-color:white;"
        with_bg = soup.find_all(has_bg_color)
        ### No defined Background color -> White
        ### Define white background in Tag!


    for tag in with_bg:
        children = list_children_nobg(tag)
        if tag.has_attr("style") and "background-color:" in tag["style"]:
            style= tag["style"]
            loc_1 = style.find("background-color:") + 17
            loc_2 = style.find(";",loc_1)
            color_bg = str(style[loc_1:loc_2])
            color_bg = color_to_rgb(color_bg)
        for child in children:
            ### Children are also broken, if they have no separate Text Color
            color_text = get_text_color(child)
            try:
                text_contr = contrast.rgb(color_text,color_bg)
                if text_contr < 4.5:
                    contrast_white = contrast.rgb([1,1,1],color_bg)
                    contrast_black = contrast.rgb([0,0,0],color_bg)
                    if contrast_black > 4.5 and contrast_white < contrast_black:
                        child["style"] = child["style"] + "color: black"
                        website_log[22] = website_log[22]+1
                    elif contrast_white > 4.5 and contrast_white > contrast_black:
                        child["style"] = child["style"] + "color: white"
                        website_log[22] = website_log[22]+1
            except:
                website_log[23] = website_log[23]


    ##############
    # End
    ##############



    ### Save new HTML
    html_out.write(soup.prettify())


    ### Save Logging Data
    return str(website_log)[1:-1]
