from bs4 import BeautifulSoup,Tag
import re
import os
from langdetect import detect
import numpy as np
import wcag_contrast_ratio as contrast
from matplotlib import colors


def run(file):
    ##############
    # Setup
    ##############
    print(file)
    html_in = open(f"./{file}", "r", encoding="utf-8")
    soup = BeautifulSoup(html_in, 'html.parser')


    ### Logging

    website_log = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,file]



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
                style = color_to_rgb( style[loc_1:loc_2].strip())
            else:
                style = [0,0,0]
        else:
            style = [0,0,0]
        return style


    ##############
    # Website Check
    ##############

    #### Checks for alt_missing 

    images = soup.find_all('img')

    for image in images:
        if not image.has_attr("alt"):
            website_log[0] = website_log[0]+1


    ### Link Empty
    ### Searches for Empty Link 

    links = soup.find_all("a")

    for link in links:
        if(link.string == None):
            website_log[1] = website_log[1]+1



    #### H1_missing

    h1= soup.find('h1')
    if h1 == None:
        website_log[2] = website_log[2]+1


    ### Heading Empty

    headings = soup.find_all(re.compile("^h[1-6]$"))
    for heading in headings:
        if heading.string == None:
            website_log[3] = website_log[3]+1

    ### Heading Skipped

    i = 6
    while i > 0:
        heading = soup.find_all(f"h{i}")
        if(heading != []):
            while i > 1:
                i = i - 1
                heading = soup.find_all(f"h{i}")
                if(heading == []):
                    website_log[4] = website_log[4]+1
        i = i-1



    ### Button Empty
    buttons = soup.find_all("button")
    for button in buttons:
        if button.string == None:
            website_log[5] = website_log[5]+1


    ### Language_missing

    html_tag = soup.find("html")
    if html_tag != None and not html_tag.has_attr("lang"):
        website_log[6] = website_log[6]+1


    ### Region missing

    regions = [soup.find("header"),soup.find("nav"),soup. find("main"),soup.find("footer")]

    for region in regions:
        if(region == None):
            website_log[7] = website_log[7]+1


    ### Table_layout
    tables = soup.find_all("table")

    for table in tables:
        header = table.find_all("th")
        if header == []:
            website_log[8] = website_log[8]+1


    ### Noscript

    noscript = soup.find_all("noscript")
    if noscript != []:
        website_log[9] = website_log[9]+1

    ### ALT_suspicious

    images = soup.find_all('img')

    for image in images:
        if image.has_attr("alt"):
            alt_text = str(image["alt"])
            if len(alt_text) < 10:
                website_log[10] = website_log[10]+1
            elif any(re.findall(r'.jp|.JP|.pn|.PN|http', alt_text, re.IGNORECASE)):
                website_log[10] = website_log[10]+1



    ### Event_handler

    event_handler = soup.find_all(has_handler)
    website_log[11] = len(event_handler)



    #### Text_justified

    with_style = soup.find_all(has_style)

    for element in with_style:
        if "text-align: justify" in element["style"] and len(element.string) > 500:
            website_log[12] = website_log[12]+1

    ### Text Small & heading_possible

    with_style = soup.find_all(has_style)

    for element in with_style:
        if "font-size:" in element["style"]:
            size = str(element["style"])
            size_start = size.find("font-size:")
            size = size[size_start+11:size.find("p",size_start)]
            try:
                size = float(size)
            except:
                website_log[24] = website_log[24]+1
                size = 12
            if(size < 11):
                website_log[13] = website_log[13]+1
            elif(size > 19 and len(element) < 50):
                website_log[14] = website_log[14]+1

            elif(size > 15 and ("<b>" in str(element) or "<it>" in str(element)) and len(element) < 50):
                website_log[14] = website_log[14]+1


    ### Link_internal_broken

    links = soup.find_all("a")
    targets = soup.find_all(with_id)
    for link in links:
        if link.has_attr("href") and len(link["href"])>2 and (link["href"])[0] == "#":
            internal_link = link["href"]
            if f'"{internal_link[1:]}"' not in str(targets):
                website_log[15] = website_log[15]+1
                


    ### Link_redundant
    links = soup.find_all("a")
    i = 0
    while i < len(links)-1:
        if(links[i].has_attr("href") and links[i+1].has_attr("href") and links[i]["href"] == links[i+1]["href"]):
            website_log[16] = website_log[16]+1
        i +=1    

    ### alt_duplicate
    images = soup.find_all("img")
    i = 0
    while i < len(images)-1:
        if(images[i].has_attr("alt") and images[i+1].has_attr("alt")):
            if(images[i]["alt"] == images[i+1]["alt"]):
                website_log[17] = website_log[17]+1
        i +=1    

    ### Link_suspicious

    links = soup.find_all("a")

    for link in links:
        if any(re.findall(r'click|klicken|weiter lesen|lesen|details|www.|.com|.de|Link', link.text, re.IGNORECASE)):
            website_log[18] = website_log[18]+1
    
    ### Label missing

    forms = soup.find_all("form")

    for form in forms:
        form = str(form)
        labels = len(re.findall(r'<label>', form, re.IGNORECASE))
        inputs = len(re.findall(r'<input',form, re.IGNORECASE))
        no_label = len(re.findall(r'"image"|"submit"|"reset"|"button"|"hidden"',form, re.IGNORECASE))
        label_ratio = inputs - labels - no_label
        if  label_ratio > 0:
            website_log[19] = website_log[19]+label_ratio


    ### Title Redundant


    titles = soup.find_all(has_title)
    for title in titles:
        if title.has_attr("alt"):
            if title["title"] in title["alt"]:
                website_log[20] = website_log[20]+1
        elif  title["title"] in str(title.contents):
            website_log[20] = website_log[20]+1



    #### Alt Redundant

    images = soup.find_all("img")

    for image in images:
        if image.has_attr("alt"):
            if(image["alt"] in str(image.previous_sibling) or image["alt"] in str(image.next_sibling)):
                website_log[21] = website_log[21]+1

    ### Contrast



    #### Lists all Children
    ### Not needed here

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


    with_bg = soup.find_all(has_bg_color)
    if(with_bg == []):
        with_bg = list_children(soup)
        color_bg = [1,1,1]
        body = soup.find("body")
        if body != None and body.has_attr("style"):
            body["style"] = body["style"] + (";background-color:white;") 
        elif body != None:
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
                    website_log[22] = website_log[22]+1
            except:
                website_log[23] = website_log[23]




    ##############
    # End
    ##############





    ### Save Logging Data
    return str(website_log)[1:-1]
