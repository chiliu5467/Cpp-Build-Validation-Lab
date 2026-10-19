#include "Checksum.h"

namespace validation
{
    std::uint32_t ComputeChecksum(
        std::span<const std::byte> bytes)
    {
        std::uint32_t sum = 0;

        for (std::byte value : bytes)
        {
            sum += std::to_integer<std::uint8_t>(value);
        }

        return sum;
    }
}