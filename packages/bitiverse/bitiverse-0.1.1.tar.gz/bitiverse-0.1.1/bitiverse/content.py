import json

version = 0.1

def create_content_file(image_url, link_url, content_file_name):
    data = {}
    data['image_url'] = image_url
    data['link_url'] = link_url
    data['version'] = version
    with open(content_file_name, 'wb') as outfile:
        json.dump(data, outfile)
