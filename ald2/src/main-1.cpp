#include <iostream>
#include "yaml-cpp/yaml.h"
#include "LogicDiagram.h"

using namespace std;


/*
int main(int, const char**) {
    cout << "Hello World" << endl;

    YAML::Node c = YAML::LoadFile("../tests/main-1.yaml");
    cout << c["part"].as<string>() << endl;

    // Demonstrate iteration
    for (auto it = begin(c["blocks"]); it != end(c["blocks"]); it++) {
        cout << (*it)["loc"] << endl;  
        // Iterate on members of object
        auto j = (*it)["inp"];
        for (auto it2 = begin(j); it2 != end(j); it2++) {
            cout << it2->first << endl;
            cout << it2->second << endl;
        }

    }

    for (auto it = begin(c["outputs"]); it != end(c["outputs"]); it++) {
        cout << *it << endl;        
    }
}
*/

int main(int, const char**) {

    YAML::Node c = YAML::LoadFile("../tests/main-1.yaml");
    LogicDiagram::Page page = c.as<LogicDiagram::Page>();
    cout << page.part << endl;
    cout << page.blocks.size() << endl;
}
