import os
import image_writer as i
import ownership as o

skeleton1 = """
<html>
<head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
</head>

<body style="margin:0;padding:0">
    <a id="mg">
    <img src="bitiverse.jpg" style="width:100%;height:100%;" onmousemove="hoverClick(event)" onclick="showCoords(event)">
    </a>
</body>
</html>
<script>
function showCoords(event) {
    var x = event.clientX;
    var y = event.clientY;
    coords = moduleCoords(x, y)
    fetch(coords)
}
"""

skeleton2 = """
function get_url(coords) {
    var x = coords[0]
    var y = coords[1]
    var linkn = links[y*1920 + x]
    var url = keylist[linkn]
    console.log(linkn, url)
    return url
}
function fetch(coords) {
    var url = get_url(coords)
    window.location.href = url
}
function hoverClick(event) {
    var x = event.clientX;
    var y = event.clientY;
    coords = moduleCoords(x, y)
    document.getElementById("mg").href = get_url(coords)
}
function moduleCoords(x, y) {
    var coords = [-1, -1];
    coords[0] = Math.floor(x * 1920 / window.innerWidth);
    coords[1] = Math.floor(y * 1080 / window.innerHeight);
    return coords
}
</script>
"""
def get_links_array(owners, ownerlist):
    links, l = i.create_links_array(owners, ownerlist)
    links_array = "["
    for x in links:
        for y in x:
            links_array += str(y) + ","
    links_array = links_array[0:len(links_array) - 4] + "]"
    keylist = str([str(x[1]) for x in l.items()])
    return links_array, keylist

def write_html(owners, ownerlist):
    f = open('static/index.html', 'wb')
    html = skeleton1
    linksarray, keylist = get_links_array(owners, ownerlist)

    html += "var links = " + linksarray
    html += "\nvar keylist = " + keylist

    html += skeleton2
    f.write(html)
    f.close()

def make():
    os.system('rm -rf static')
    os.system('mkdir -p static')
    os.system('touch static/index.html')

    owners, ownerlist = o.process_all()
    print "creating image"
    i.create_and_save_image('static/bitiverse.jpg', owners, ownerlist)
    write_html(owners, ownerlist)

if __name__ == "__main__":
    make()
