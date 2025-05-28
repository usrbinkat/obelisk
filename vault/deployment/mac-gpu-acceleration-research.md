# Mac GPU Acceleration Research for Containerized Ollama

## Overview

This document captures the research findings and design decisions from investigating GPU acceleration options for containerized Ollama deployments on Apple Silicon Macs. This research was conducted to evaluate the viability of achieving Metal GPU acceleration within containers for the Obelisk RAG system.

## Research Summary

### Key Findings

1. **Docker Limitation**: Docker Desktop on macOS fundamentally cannot provide GPU passthrough due to Apple's Hypervisor.framework limitations
2. **Vulkan-to-Metal Translation**: Podman with libkrun enables partial GPU acceleration through Vulkan virtualization, achieving 60-80% of native Metal performance
3. **Engineering Complexity**: Custom Ollama builds with Vulkan support require significant patches and maintenance overhead
4. **Production Recommendation**: Native Ollama with containerized services remains the optimal approach

### Technical Constraints

#### Ollama GPU Detection Mechanism

Ollama detects Metal GPUs through:
```go
// gpu_darwin.go
func metalSupported() bool {
    return ns.ProcessInfo.processorType == "ARM" && 
           mtl.CopyAllDevices().Count > 0
}
```

This detection fails in containers, causing fallback to CPU mode.

#### Critical Environment Variables

| Variable | Purpose | Impact |
|----------|---------|---------|
| `OLLAMA_DEBUG=1` | GPU detection logging | Essential for debugging |
| `OLLAMA_GPU_LAYERS` | Force layer offloading | Can override detection |
| `OLLAMA_METAL_DEBUG=1` | Metal shader logs | Shows API calls |

## Vulkan-to-Metal Architecture

### libkrun/Podman Approach

The most promising approach uses:
1. Podman as container runtime
2. libkrun as Virtual Machine Monitor (VMM)
3. Vulkan-to-Metal translation via MoltenVK
4. Venus protocol for GPU virtualization

### Setup Process

```bash
# Enable libkrun provider
export CONTAINERS_MACHINE_PROVIDER="libkrun"
podman machine init --cpus 8 --memory 32768
podman machine start

# Verify GPU device
podman machine ssh
ls /dev/dri  # Should show renderD128
```

### Performance Characteristics

- **Translation Overhead**: 15-20% from Vulkan-to-Metal
- **Memory Overhead**: 13.7% additional VRAM usage
- **Achievable Performance**: 60-80% of native Metal

## Implementation Requirements

### Building Vulkan-Enabled Ollama

Required patches to Ollama source:

1. **CMakeLists.txt modifications**:
```cmake
option(LLAMA_VULKAN "Enable Vulkan support" ON)
find_package(Vulkan REQUIRED)
target_link_libraries(llama Vulkan::Vulkan)
```

2. **GPU detection override**:
```go
// Add Vulkan detection for containers
if _, err := os.Stat("/dev/dri/renderD128"); err == nil {
    return GpuInfo{
        Library: "vulkan",
        Variant: "v1",
    }
}
```

3. **Mesa driver requirements**:
```dockerfile
RUN dnf -y copr enable slp/mesa-krunkit && \
    dnf -y install mesa-vulkan-drivers && \
    dnf -y downgrade mesa-vulkan-drivers \
    --repo copr:copr.fedorainfracloud.org:slp:mesa-krunkit
```

## Production Viability Assessment

### Risk Matrix

| Approach | Performance | Stability | Maintenance | Viability |
|----------|-------------|-----------|-------------|-----------|
| Native Ollama | 100% | High | Low | ✅ Recommended |
| Podman+Vulkan | 60-80% | Medium | High | ⚠️ Experimental |
| Custom Patches | Variable | Low | Very High | ❌ Not Recommended |

### Engineering Effort

- Research & Prototype: 2 weeks
- Custom Build Development: 4 weeks  
- Testing & Optimization: 3 weeks
- Total: ~9 weeks with 1-2 engineers

## Design Decision

**Recommendation**: Use native Ollama with containerized Obelisk services

**Rationale**:
- Maintains 100% GPU performance
- Reduces operational complexity
- Avoids maintaining custom patches
- Aligns with current Docker limitations

**Future Tracking**:
- Monitor Apple Virtualization.framework GPU support
- Track containerd-shim-metal development
- Evaluate MLX framework as alternative

## References

- GitHub Issue: [#43 - GPU-Accelerated Containerized Ollama](https://github.com/usrbinkat/obelisk/issues/43)
- Ollama GPU Detection: [ollama/ollama#3849](https://github.com/ollama/ollama/issues/3849)
- libkrun Documentation: [containers/krunkit](https://github.com/containers/krunkit)
- Podman GPU Research: [sinrega.org blog](https://sinrega.org/2024-03-06-enabling-containers-gpu-macos/)

## Excluded Approaches

### QEMU with virtio-gpu

**Decision**: Excluded from consideration

**Rationale**:
- Performance: Only ~45% of native Metal
- Complexity: Manual QEMU configuration required
- Stability: Experimental with frequent crashes
- Characterized as backwards-looking hack

## Conclusion

While technically feasible, the engineering complexity of containerized GPU acceleration for Ollama on macOS outweighs the benefits. The hybrid approach (native Ollama + containerized services) provides optimal performance with manageable complexity until Apple enables native GPU virtualization support.