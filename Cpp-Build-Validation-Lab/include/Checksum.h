#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

namespace validation
{
    std::uint32_t ComputeChecksum(
        std::span<const std::byte> bytes);
}