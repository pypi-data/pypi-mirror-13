from PIL import Image
import pixelwriter as p
import reader as r

def init_image(output_filename):
    image = Image("RGB", (p.universe_width, p.universe_height), "white")
    image.save(output_filename)

def load_image(filename):
    image = Image.load(filename)
    return image

def resize_image(image, new_resolution):
    return image.resize(new_resolution, Image.ANTIALIAS)

def create_link_map(output_filename, linkarray):
    image = Image.new("RGB", (p.universe_width, p.universe_height), "white")
    for n, x in enumerate(linkarray):
        for m, y in enumerate(x):
            y = int(y)
            c = (y * 50 % 255, y * 30 % 255, y * 130 % 255)
            image.putpixel((n, m), c)
        print n
    image.save(output_filename)

def apply_image_on_image(pimage, image, coords, owners, applier_output):
    pix = pimage.load()
    xmax = image.size[0] - 1
    ymax = image.size[1] - 1
    for i in range(coords[0][0], min(coords[1][0] + 1, xmax)):
        for j in range(coords[0][1], min(coords[1][1] + 1, ymax)):
            if owners[i][j] == applier_output:
                try:
                    pc = pix[i, j]
                except:
                    print i
                    print j
                image.putpixel((i, j), pc)
    return image

def apply_owner_content(owner_content, image, owners, applier_output):
    for x in owner_content:
        pimage = x['image']
        coords = x['coords']
        print "COORDS "+str(coords)
        image = apply_image_on_image(pimage, image, coords, owners, applier_output)
    return image

def create_image(owners, ownerlist):
    image = Image.new("RGB", (p.universe_width, p.universe_height), "white")

    owners_contents = r.owners_contents(ownerlist)
    for owner in owners_contents:
        owner_content = owners_contents[owner]
        image = apply_owner_content(owner_content, image, owners, owner)
    return image

def apply_owner_links(owner_content, links, owners, owner, l):
    for x in owner_content:
        link = x['link']
        n = len(l.keys())
        l[n] = link
        coords = x['coords']
        for x in range(coords[0][0], coords[1][0]+1):
            for y in range(coords[0][1], coords[1][1]+1):
                try:
                    if owners[x][y] == owner:
                        links[x][y] = n
                except:
                    print 'out of bounds coords in link assignment'
    return links, l

def create_links_array(owners, ownerlist):
    contents = r.owners_contents(ownerlist)
    links = []
    l = {}
    for _ in range(p.universe_width):
        z = []
        for _ in range(p.universe_height):
            z.append('-1')
        links.append(z)

    for owner in contents:
        owner_content = contents[owner]
        links, l = apply_owner_links(owner_content, links, owners, owner, l)
    return links, l

def create_and_save_links_array(owners, ownerlist, filename, keylist_filename):
    links, l = create_links_array(owners, ownerlist)
    f = open(filename, 'wb+')
    for x in links:
        s = ''
        for m in x:
            s += str(m) + ','
        s += "\n"
        f.write(s)
    f.close()
    f2 = open(keylist_filename, 'wb+')
    for i in range(0, len(l)):
        f2.write(str(i)+"#"+str(l[i]))
        f2.write('\n')
    f2.close()

def load_links_array(filename, keylist_filename):
    f = open(filename)
    q = f.readlines()
    a = []
    keys = {}
    for x in q:
        m = x.replace('\n', '')
        a.append(m.split(','))
    ff = open(keylist_filename)
    r = ff.readlines()
    for y in r:
        h = y.split("#")
        keys[int(h[0])] = h[1]

    return a, keys

def create_and_save_image(filename, owners, ownerlist):
    image = create_image(owners, ownerlist)
    image.save(filename)

def image_to_grid(image_obj):
    data = list(image_obj.getdata())
    s = image_obj.size
    xrange = s[0]
    yrange = s[1]
    d = []
    for i in range(xrange):
        q = []
        for j in range(yrange):
            n = i * yrange + j
            q.append(data[n])
        d.append(q)
    return d
