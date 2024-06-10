#ifndef _LogicDiagram_h
#define _LogicDiagram_h

#include <string>
#include <vector>
#include <map>

#include "yaml-cpp/yaml.h"

namespace LogicDiagram {

    struct Block {
        std::string typ, loc, coo;
        int cir;
        std::map<std::string, std::vector<std::string>> inp;
    };

    struct Page {
        std::string part;
        std::string title;
        std::string num;
        std::string pdf;
        std::vector<Block> blocks;
    };
}

namespace YAML {

    template<>
    struct convert<LogicDiagram::Block> {
        static bool decode(const Node& node, LogicDiagram::Block& rhs) {
            if (!node.IsMap()) 
                return false;
            rhs.typ = node["typ"].as<std::string>();
            rhs.loc = node["loc"].as<std::string>();
            rhs.coo = node["coo"].as<std::string>();
            rhs.cir = node["cir"].as<int>();
            auto j = node["inp"];
            for (auto it1 = std::begin(j); it1 != std::end(j); it1++) {
                // This should be an iterable list of node names
                if (!it1->second.IsSequence())
                    return false;
                // Create an empty vector that will receive the strings
                rhs.inp[it1->first.as<std::string>()] = std::vector<std::string>();
                auto k = it1->second;
                for (auto it2 = std::begin(k); it2 != std::end(k); it2++)
                    rhs.inp[it1->first.as<std::string>()].push_back(it2->as<std::string>());
            }
            return true;
        }
    };

    template<>
    struct convert<LogicDiagram::Page> {
        static bool decode(const Node& node, LogicDiagram::Page& rhs) {
            if (!node.IsMap()) 
                return false;
            rhs.part = node["part"].as<std::string>();
            rhs.title = node["title"].as<std::string>();
            rhs.num = node["num"].as<std::string>();
            if (node["pdf"]) 
                rhs.pdf = node["pdf"].as<std::string>();
            auto j = node["blocks"];
            // This should be an iterable list of blocks
            if (!j.IsSequence())
                return false;
            for (auto it2 = std::begin(j); it2 != std::end(j); it2++)
                rhs.blocks.push_back(it2->as<LogicDiagram::Block>());
            return true;
        }
    };
}

#endif
