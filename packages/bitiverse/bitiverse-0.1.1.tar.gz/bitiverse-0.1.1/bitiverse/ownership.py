import csv
import pixelwriter as p
import reader as r

#initial conditions
root_output = {'output': '625af0a83d184f6c93df6201dc0b753b630191c24c29e1207e9ca6794606121e:0', 'value': 2030000}

grid_filename = 'grid.csv'
owners_filename = 'owners.txt'

def init_ownership():
    og = root_output['output']
    ownerlist = {}
    ownerlist[og] = p.universe_height*p.universe_width
    data = [[og for _ in range(0, p.universe_height)] for _ in range(0, p.universe_width)]
    save_ownership(data, ownerlist)
    return data, ownerlist

def load_ownership():
    with open(grid_filename, 'a+') as f:
        data = list(list(rec) for rec in csv.reader(f, delimiter=','))
    ownerlist = []
    with open(owners_filename, 'a+') as q:
        r = q.readlines()
        if len(r) == 0:
            r = [root_output['output']+"=0"]
    ownerlist = {}
    for x in r:
        outp = x.split('=')[0]
        v = int(x.split('=')[1])
        ownerlist[outp] = v
    if len(data) < p.universe_width:
        data, ownerlist = init_ownership()
    return data, ownerlist

def save_ownership(owners, ownerlist):
    with open(grid_filename, "wb+") as f:
        writer = csv.writer(f)
        writer.writerows(owners)
    r = open(owners_filename, "wb+")
    for x in ownerlist:
        r.write(str(x)+"="+str(ownerlist[x])+"\n")
    r.close()

def process_all():
    owners, ownerlist = load_ownership()
    cont = True
    while cont:
        owners, ownerlist, i = process(owners, ownerlist)
        if i == 0:
            cont = False
    save_ownership(owners, ownerlist)
    return owners, ownerlist

def process(owners, ownerlist):
    iterations = 0
    print "Searching through known owners."
    for x in ownerlist.keys():
        print "Investigating owner: %s." % x
        txhash = x.split(':')[0]
        output_n = int(x.split(':')[1])
        next_output = r.where_was_output_spent(txhash, output_n)
        if not next_output is None:
            iterations += 1
            print "Processing txhash: %s." % str(next_output)
            owners, ownerlist = read(next_output, owners, ownerlist)
    return owners, ownerlist, iterations

def read(txhash, owners, ownerlist):
    data, _, inputs_array = r.read_tx(txhash)
    if len(data) > 2 and not data[0] == "C":
        owners, ownerlist = read_transfer(txhash, data, inputs_array, owners, ownerlist)
    return owners, ownerlist

def adjust_ownership(owners, coords, new_owner, inputs_array, ownerlist, change_recipient):
    """
    first output is always new recipient of space in coords (inclusive).  Second output
    is always change receipt.  So ownership must also be adjusted to this new output.
    """
    unspents = [x[1] for x in inputs_array]
    print "Applying new ownership to %s." % new_owner
    if not new_owner in ownerlist.keys():
        ownerlist[new_owner] = 0
    if not change_recipient  in ownerlist.keys(): #this check is unnecessary
        ownerlist[change_recipient] = 0

    for x in range(coords[0][0], coords[1][0]+1): #this is also horrible
        for y in range(coords[0][1], coords[1][1]+1):  #inclusive always
            if owners[x][y] in unspents: #is authentically owned
                ownerlist[owners[x][y]] -= 1
                owners[x][y] = new_owner
                ownerlist[new_owner] += 1

    for x in range(0, p.universe_width):  #yes this is even more horrible I know
        for y in range(0, p.universe_height):
            if owners[x][y] in unspents: #is owned by inputs of tx
            #send them to change output
                ownerlist[owners[x][y]] -= 1
                owners[x][y] = change_recipient
                ownerlist[change_recipient] += 1

    for x in ownerlist.keys():
        if ownerlist[x] == 0:
            del ownerlist[x]

    return owners, ownerlist

def read_transfer(txhash, data, inputs_array, owners, ownerlist):
    """
    Parses a transfer transaction for meaning.  Changes ownership state
    if valid.
    Implicit Rules ====> First output is transferred, second is change (in pixelspace)
    """
    coords = p.decompress_coords(int(data))

    assert len(coords) == 2
    recipient = txhash + ":0"  #receiver should always be first output
    change_recipient = txhash + ":1" #second output should always receive change
    owners, ownerlist = adjust_ownership(owners, coords, recipient, inputs_array, ownerlist, change_recipient)
    return owners, ownerlist
