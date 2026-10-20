cmake_minimum_required(VERSION 3.20)

project(CppBuildValidationLab LANGUAGES CXX)

add_library(checksum STATIC
    Cpp-Build-Validation-Lab/src/Checksum.cpp
)

target_include_directories(checksum
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/Cpp-Build-Validation-Lab/include
)

target_compile_features(checksum
    PUBLIC cxx_std_20
)

add_executable(checksum_tests
    Cpp-Build-Validation-Lab/tests/test_checksum.cpp
)

target_link_libraries(checksum_tests
    PRIVATE checksum
)

enable_testing()

add_test(
    NAME checksum_tests
    COMMAND checksum_tests
)