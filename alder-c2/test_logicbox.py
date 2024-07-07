import logicbox

class Source:
    def __init__(self):
        self.values = {}
    
    def get(self, name):
        return self.values[name]
    
    def set(self, name, value):
        self.values[name] = value
    

source = Source()
lb = logicbox.LogicBox("../daves-1f/typewriter-mechanical.logic", source)    

# Initialize
for n in lb.get_input_names():
    source.set(n, False)

for t in range(0, 8):

    print(t, "-----------------------------")

    if t == 1:
        source.set("r30_pick_current", True)
        source.set("r10_pick_current", True)
    elif t == 2:
        source.set("r30_pick_current", False)
        source.set("r10_pick_current", False)
    elif t == 4:
        source.set("r10_trip_current", True)
    elif t == 5:
        source.set("r10_trip_current", False)

    lb.tick()

    print(lb.get("r30_1_no"), lb.get("r10_1_no"), lb.get("crcb_4_no"))



