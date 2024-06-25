/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _LogicDiagram_h
#define _LogicDiagram_h

#include <string>
#include <vector>
#include <map>
#include <iostream>

#include "yaml-cpp/yaml.h"

namespace LogicDiagram {

    struct Card {
        std::string typ;
    };

    struct Block {
        std::string typ, gate, loc, coo;
        int cir;
        std::map<std::string, std::vector<std::string>> inp;
        std::map<std::string, std::vector<std::string>> out;
    };

    struct Alias {
        std::string name;
        std::vector<std::string> inp;
    };

    struct Page {
        std::string part;
        std::string title;
        std::string num;
        std::string pdf;
        std::vector<Block> blocks;
        std::vector<Alias> aliases;

        const Block& getBlockByCoordinate(const std::string& coo) const;
    };

    extern std::vector<std::string> PinNames;

    bool validPinName(const std::string& pinName);

    struct BlockCooPin {
        std::string coo;
        std::string pinId;
    };

    /**
     * Takes a string in format xxx.ab and returns a vector of block coordinated/pins
     * in this format:
     * 
     * { xxx.a, xxx.b }
     * 
     * Notice that a multi-character bin designation is treated like multiple pins.
    */
    std::vector<BlockCooPin> parsePinRefs(const std::string& ref);
}

// TODO: MOVE TO UTIL
static void removeTrailingCharacters(std::string &str, const char charToRemove) {
    str.erase (str.find_last_not_of(charToRemove) + 1, std::string::npos );
}

namespace YAML {

    template<>
    struct convert<LogicDiagram::Block> {
        static bool decode(const Node& node, LogicDiagram::Block& rhs) {
            if (!node.IsMap()) 
                return false;
            // The trailing hyphens are removed
            std::string typ = node["typ"].as<std::string>();
            removeTrailingCharacters(typ, '-');
            rhs.typ = typ;
            rhs.gate = node["gate"].as<std::string>();
            rhs.loc = node["loc"].as<std::string>();
            rhs.coo = node["coo"].as<std::string>();
            rhs.cir = node["cir"].as<int>();

            if (node["inp"]) {
                auto j = node["inp"];
                for (auto it1 = std::begin(j); it1 != std::end(j); it1++) {
                    // This should be an iterable list of node names
                    if (!it1->second.IsSequence())
                        return false;
                    std::string pinName = it1->first.as<std::string>();
                    if (!LogicDiagram::validPinName(pinName)) 
                        throw std::string("Invalid pin name on block " + rhs.loc + " : " + pinName);
                    // Create an empty vector that will receive the strings
                    rhs.inp[pinName] = std::vector<std::string>();
                    auto k = it1->second;
                    for (auto it2 = std::begin(k); it2 != std::end(k); it2++)
                        rhs.inp[pinName].push_back(it2->as<std::string>());
                }
            }

            if (node["out"]) {
                auto j = node["out"];
                for (auto it1 = std::begin(j); it1 != std::end(j); it1++) {
                    // This should be an iterable list of node names
                    if (!it1->second.IsSequence())
                        return false;
                    std::string pinName = it1->first.as<std::string>();
                    if (!LogicDiagram::validPinName(pinName)) 
                        throw std::string("Invalid pin name on block " + rhs.loc + " : " + pinName);
                    // Create an empty vector that will receive the strings
                    rhs.inp[pinName] = std::vector<std::string>();
                    auto k = it1->second;
                    for (auto it2 = std::begin(k); it2 != std::end(k); it2++)
                        rhs.out[it1->first.as<std::string>()].push_back(it2->as<std::string>());
                }
            }

            return true;
        }
    };

    template<>
    struct convert<LogicDiagram::Alias> {
        static bool decode(const Node& node, LogicDiagram::Alias& lhs) {
            if (!node.IsMap()) 
                return false;
            lhs.name = node["name"].as<std::string>();
            auto j = node["inp"];
            // This should be an iterable list of node names
            if (!j.IsSequence())
                return false;
            for (auto it2 = std::begin(j); it2 != std::end(j); it2++)
                lhs.inp.push_back(it2->as<std::string>());
            return true;
        }
    };

    template<>
    struct convert<LogicDiagram::Page> {
        static bool decode(const Node& node, LogicDiagram::Page& lhs) {
            if (!node.IsMap()) 
                return false;
            lhs.part = node["part"].as<std::string>();
            lhs.title = node["title"].as<std::string>();
            lhs.num = node["num"].as<std::string>();
            if (node["pdf"]) 
                lhs.pdf = node["pdf"].as<std::string>();
            if (node["blocks"]) {
                auto j = node["blocks"];
                // This should be an iterable list of blocks
                if (!j.IsSequence())
                    return false;
                for (auto it2 = std::begin(j); it2 != std::end(j); it2++)
                    lhs.blocks.push_back(it2->as<LogicDiagram::Block>());
            }
            if (node["aliases"]) {
                auto j = node["aliases"];
                // This should be an iterable list of aliases
                if (!j.IsSequence())
                    return false;
                for (auto it2 = std::begin(j); it2 != std::end(j); it2++)
                    lhs.aliases.push_back(it2->as<LogicDiagram::Alias>());
            }
            return true;
        }
    };
}

#endif
