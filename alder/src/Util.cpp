
#include <algorithm>
#include "Util.h"

using namespace std;

string toLower(const string& r) {
    string data = r;
    std::transform(data.begin(), data.end(), data.begin(),
        [](char c){ return std::tolower(c); });
    return data;
}

