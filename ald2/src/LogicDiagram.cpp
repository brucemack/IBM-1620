#include "LogicDiagram.h"

using namespace std;

namespace LogicDiagram {

const Block& Page::getBlockByCoordinate(const string& coo) const {
    for (const LogicDiagram::Block& b : blocks) {
        if (b.coo == coo)
            return b;
    }
    throw string("Invalid block coordinate: " + coo);
}

}


