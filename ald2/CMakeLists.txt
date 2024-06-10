cmake_minimum_required(VERSION 3.13)
project(hello C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)
file(MAKE_DIRECTORY tmp)

add_compile_options(-Wall -Wpedantic -g)

include_directories(src)
include_directories(include)

include(FetchContent)

FetchContent_Declare(
  yaml-cpp
  GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
  GIT_TAG master # Can be a tag (yaml-cpp-x.x.x), a commit hash, or a branch name (master)
)
FetchContent_GetProperties(yaml-cpp)

if (NOT yaml-cpp_POPULATED)
  message(STATUS "Fetching yaml-cpp...")
  FetchContent_Populate(yaml-cpp)
  add_subdirectory(${yaml-cpp_SOURCE_DIR} ${yaml-cpp_BINARY_DIR})
endif()

# ------ main-1 ---------------------------------------------------------------
#
add_executable(main-1
  src/main-1.cpp
  src/Components.cpp
)

target_link_libraries(main-1 PUBLIC yaml-cpp::yaml-cpp) 

