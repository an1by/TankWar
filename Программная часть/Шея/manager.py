import tcpip

last_obstacles = []

def update_field(new_obstacles):
    global last_obstacles
    new_last_obstacles = []
    arr = []
    for lobs in last_obstacles:
        found = False
        for nobs in new_obstacles:
            if lobs["positions"] == nobs["positions"]:
                found = True
                if lobs["state"] != nobs["state"]:
                    arr.append(nobs)
                    new_last_obstacles.append(nobs)
                break
        if not found:
            lobs.state = "empty"
            arr.append(lobs)
    last_obstacles = new_last_obstacles
    tcpip.send_data({"command": "edit", "what": "obstacles", "list": arr})