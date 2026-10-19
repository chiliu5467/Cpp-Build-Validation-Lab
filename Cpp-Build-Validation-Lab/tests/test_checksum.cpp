#include "Checksum.h"

#include <vector>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <string>

int TestChecksum()
{
    int failed = 0;

    auto runTest = [&failed](
        const std::string& name,
        const std::vector<std::byte>& data,
        std::uint32_t expected)
        {
            std::uint32_t actual =
                validation::ComputeChecksum(data);

            if (actual == expected)
            {
                std::cout << "[PASS] " << name << '\n';
            }
            else
            {
                std::cerr << "[FAIL] " << name
                    << " --- expected: " << expected
                    << " / actual: " << actual
                    << '\n';

                ++failed;
            }
        };

    runTest("Empty Input", {}, 0);
    runTest("Single Byte", { std::byte{0x01} }, 1);
    runTest("Multiple Bytes",
        { std::byte{0x01}, std::byte{0x02}, std::byte{0x03} }, 6);
    runTest("Maximum Byte", { std::byte{0xFF} }, 255);
    runTest("Mixed Bytes",
        { std::byte{0xFF}, std::byte{0x01} }, 256);

    return failed;
}

int main()
{
    return TestChecksum() == 0 ? 0 : 1;
}