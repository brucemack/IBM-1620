/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include <algorithm>
#include <unordered_set>
#include <queue>

#include "Pin.h"
#include "Components.h"
#include "PlugLocation.h"

using namespace std;

Pin::Pin(Card& card, const string& id) 
:   _card(card),
    _id(id) {        
}

string Pin::getDesc() const {
    return _card.getLocation().toString() + "/" + _id;
}

string Pin::getConnectionsDesc() const {
    string res;
    bool first = true;
    for (auto conn : _connections) {
        if (!first)
            res = res + ", ";
        res = res + conn.get().getDesc();
        first = false;
    }
    return res;
}

void Pin::connect(Pin& pin) { 
    // Check to see if the connection is redundant
    if (std::find_if(_connections.begin(), _connections.end(), 
        [&pin](const std::reference_wrapper<Pin>& x) { 
            return std::addressof(pin) == std::addressof(x.get()); 
        }
    ) != _connections.end()) {
        throw string("Redundant pin connection: " + pin.getDesc());
    }
    _connections.push_back(std::reference_wrapper<Pin>(pin));
}

bool Pin::operator== (const Pin& other) const { 
    return this == std::addressof(other); 
}

size_t Pin::hash() const {
    return std::hash<std::string>{}(_id) + std::hash<PlugLocation>{}(_card.getLocation());
}

void Pin::visitImmediateConnections(const std::function<void (const Pin&)> &f) const {
    for (auto conn : _connections) 
        f(conn.get());
}

void Pin::visitAllConnections(const std::function<void (const Pin&)> &f) const {
    // If there are no connections then leave immediately
    if (_connections.empty())
        return;
    // In order to avoid duplicate visitation we keep a set of pins that have
    // already been processed.
    unordered_set<string> alreadyVisited;
    // A queue of pins that are waiting to be processed.
    queue<const Pin*> pendingVisitation;
    // Start the ball rolling by queuing the starting point
    pendingVisitation.push(this);
    // Keep working the queue until we are done
    while (!pendingVisitation.empty()) {
        const Pin* work = pendingVisitation.front();
        pendingVisitation.pop();
        if (alreadyVisited.find(work->getDesc()) == alreadyVisited.end()) {
            // Fire the caller's function
            f(*work);
            // Look at everything that is connected to this pin
            work->visitImmediateConnections([&pendingVisitation](const Pin& p) {
                    pendingVisitation.push(&p);
                }
            );
            // Record this visitation to avoid duplicates
            alreadyVisited.insert(work->getDesc());
        }
    }
}
