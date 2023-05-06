import sys
sys.path.insert(1, '../Libraries')

from tcpip import connection

last_obstacles = []

def update_field(new_obstacles):
    global last_obstacles
    arr = []

    for lobs in last_obstacles:
        found = False
        for nobs in new_obstacles:
            if nobs["position"] == lobs["position"]:
                found = True
                if lobs["type"] != nobs["type"]:
                    arr.append(nobs)
                break
        if not found:
            lobs["type"] = "empty"
            arr.append(lobs)

    for nobs in new_obstacles: # на совпадение
        found = False
        for aobs in arr:
            if aobs["position"] == nobs["position"]:
                found = True
                break
        if not found:
            arr.append(nobs)
        
    last_obstacles = new_obstacles
    if arr != []:
        connection.send({"command": "edit", "what": "obstacles", "list": arr})