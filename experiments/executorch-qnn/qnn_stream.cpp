#include <executorch/extension/module/module.h>
#include <executorch/extension/tensor/tensor.h>
#include <executorch/runtime/platform/runtime.h>
#include <executorch/runtime/backend/interface.h>
#include <executorch/backends/qualcomm/runtime/QnnExecuTorch.h>
#include <chrono>
#include <cstdio>
#include <cstdint>
#include <fcntl.h>
#include <io.h>
#include <vector>

using executorch::extension::Module;
using executorch::extension::TensorPtr;
using executorch::extension::make_tensor_ptr;
using executorch::runtime::Error;
using executorch::runtime::EValue;

int main(int argc, char** argv) {
  if (argc != 2) {
    std::fprintf(stderr, "Usage: secondhands_qnn_stream model.pte\n");
    return 2;
  }
  // Reserve the original stdout pipe for the binary protocol; route library logs to stderr.
  FILE* output = _fdopen(_dup(_fileno(stdout)), "wb");
  if (!output || _dup2(_fileno(stderr), _fileno(stdout)) != 0) return 3;
  _setmode(_fileno(stdin), _O_BINARY);
  _setmode(_fileno(output), _O_BINARY);
  executorch::runtime::runtime_init();
  QnnExecuTorchBackendRegister(
      reinterpret_cast<void*>(executorch::runtime::register_backend));
  Module module(argv[1]);
  auto status = module.load_forward();
  if (status != Error::Ok) {
    std::fprintf(stderr, "Model load failed: %u\n", static_cast<unsigned>(status));
    return 4;
  }
  auto meta = module.method_meta("forward");
  if (!meta.ok()) return 5;
  std::vector<TensorPtr> tensors;
  std::vector<EValue> values;
  uint32_t total_elements = 0;
  for (size_t i = 0; i < meta->num_inputs(); ++i) {
    auto info = meta->input_tensor_meta(i);
    if (!info.ok() || info->scalar_type() != executorch::aten::ScalarType::Float) return 6;
    auto sizes = info->sizes();
    std::vector<executorch::aten::SizesType> shape(sizes.begin(), sizes.end());
    size_t count = info->nbytes() / sizeof(float);
    if (count > 16000000 || total_elements + count > 16000000) return 7;
    total_elements += static_cast<uint32_t>(count);
    tensors.push_back(make_tensor_ptr(shape, std::vector<float>(count)));
    values.emplace_back(*tensors.back());
  }
  const uint32_t ready[] = {0x5348514e, total_elements};
  if (std::fwrite(ready, sizeof(uint32_t), 2, output) != 2 || std::fflush(output)) return 8;
  uint32_t supplied;
  while (std::fread(&supplied, sizeof(supplied), 1, stdin) == 1) {
    if (supplied != total_elements) return 9;
    for (auto& tensor : tensors) {
      size_t count = tensor->numel();
      if (std::fread(tensor->mutable_data_ptr<float>(), sizeof(float), count, stdin) != count) return 10;
    }
    auto start = std::chrono::steady_clock::now();
    auto result = module.forward(values);
    double milliseconds = std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now() - start).count();
    if (!result.ok()) {
      std::fprintf(stderr, "Inference failed: %u\n", static_cast<unsigned>(result.error()));
      return 11;
    }
    uint32_t outputs = static_cast<uint32_t>(result->size());
    std::fwrite(&outputs, sizeof(outputs), 1, output);
    for (auto& value : *result) {
      if (!value.isTensor()) return 12;
      auto tensor = value.toTensor();
      if (tensor.scalar_type() != executorch::aten::ScalarType::Float) return 13;
      uint32_t count = static_cast<uint32_t>(tensor.numel());
      std::fwrite(&count, sizeof(count), 1, output);
      std::fwrite(tensor.const_data_ptr<float>(), sizeof(float), count, output);
    }
    std::fwrite(&milliseconds, sizeof(milliseconds), 1, output);
    if (std::fflush(output)) return 14;
  }
  std::fclose(output);
  return std::feof(stdin) ? 0 : 15;
}
