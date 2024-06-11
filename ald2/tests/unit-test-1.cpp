#include <iostream>
#include <map>
#include <string>
#include <span>
#include <vector>
#include <cassert>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"
#include "Components.h"

using namespace std;

int main(int, const char**) {

    {
        CardMeta cardMeta1;
        PlugLocation loc1("0000");
        Card card1(cardMeta1, loc1);
        Pin& pina = card1.getPin("A");
        Pin& pinb = card1.getPin("B");
        vector<reference_wrapper<Pin>> pins;
        pins.push_back(pina);

        for (auto c : pins) {
            c.get();
        }

        reference_wrapper<Pin> a1 = pina;
        reference_wrapper<Pin> a2 = pina;
        // See that the underlying objects are equal
        assert(std::addressof(a1.get()) == std::addressof(a2.get()));
        // BE CAREFUL! The wrappers are not equal
        assert(std::addressof(a1) != std::addressof(a2));

        // Search semantics - found
        {
            auto it = std::find_if(pins.begin(), pins.end(), 
                [&pina](const std::reference_wrapper<Pin>& x) { 
                    return std::addressof(pina) == std::addressof(x.get()); 
                });
            assert(it != pins.end());
        }
        {
            auto it = std::find_if(pins.begin(), pins.end(), 
                [&pinb](const std::reference_wrapper<Pin>& x) { 
                    return std::addressof(pinb) == std::addressof(x.get()); 
                });
            assert(it == pins.end());
        }

    }
}
