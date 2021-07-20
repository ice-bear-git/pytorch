#!/usr/bin/env python3

from dataclasses import asdict, dataclass
from pathlib import Path

import jinja2
from typing_extensions import Literal

YamlShellBool = Literal["''", 1]

DOCKER_REGISTRY = "308535385114.dkr.ecr.us-east-1.amazonaws.com"
GITHUB_DIR = Path(__file__).resolve().parent.parent

WINDOWS_CPU_TEST_RUNNER = "windows.4xlarge"
WINDOWS_CUDA_TEST_RUNNER = "windows.8xlarge.nvidia.gpu"
WINDOWS_RUNNERS = [
    WINDOWS_CPU_TEST_RUNNER,
    WINDOWS_CUDA_TEST_RUNNER,
]

LINUX_CPU_TEST_RUNNER = "linux.2xlarge"
LINUX_CUDA_TEST_RUNNER = "linux.8xlarge.nvidia.gpu"
LINUX_RUNNERS = [
    LINUX_CPU_TEST_RUNNER,
    LINUX_CUDA_TEST_RUNNER,
]


@dataclass
class CIWorkflow:
    # Required fields
    arch: str
    build_environment: str
    test_runner_type: str

    # Optional fields
    cuda_version: str = ''
    docker_image_base: str = ''
    enable_doc_jobs: bool = False
    exclude_test: bool = False
    is_libtorch: bool = False
    is_scheduled: str = ''
    num_test_shards: int = 1
    on_pull_request: bool = False
    only_build_on_pull_request: bool = False

    # The following variables will be set as environment variables,
    # so it's easier for both shell and Python scripts to consume it if false is represented as the empty string.
    enable_jit_legacy_test: YamlShellBool = "''"
    enable_multigpu_test: YamlShellBool = "''"
    enable_nogpu_no_avx_test: YamlShellBool = "''"
    enable_nogpu_no_avx2_test: YamlShellBool = "''"
    enable_slow_test: YamlShellBool = "''"

    def __post_init__(self) -> None:
        if self.is_libtorch:
            self.exclude_test = True
        self.only_build_on_pull_request = self.only_build_on_pull_request and self.on_pull_request

    def assert_valid(self) -> None:
        assert self.arch in ['linux', 'windows'], f"invalid arch: {self.arch}, must be one of ['linux','windows']"

        err_message = f"invalid test_runner_type for {self.arch}: {self.test_runner_type}"
        if self.arch == 'linux':
            assert self.test_runner_type in LINUX_RUNNERS, err_message
        if self.arch == 'windows':
            assert self.test_runner_type in WINDOWS_RUNNERS, err_message

    def generate_workflow_file(self, workflow_template: jinja2.Template) -> None:
        output_file_path = GITHUB_DIR / f"workflows/{workflow.build_environment}.yml"
        with open(output_file_path, "w") as output_file:
            GENERATED = "generated"
            output_file.writelines([f"# @{GENERATED} DO NOT EDIT MANUALLY\n"])
            output_file.write(workflow_template.render(**asdict(workflow)))
            output_file.write("\n")
        print(output_file_path)


WINDOWS_WORKFLOWS = [
    CIWorkflow(
        arch="windows",
        build_environment="pytorch-win-vs2019-cpu-py3",
        cuda_version="cpu",
        test_runner_type=WINDOWS_CPU_TEST_RUNNER,
        on_pull_request=True,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="windows",
        build_environment="pytorch-win-vs2019-cuda10-cudnn7-py3",
        cuda_version="10.1",
        test_runner_type=WINDOWS_CUDA_TEST_RUNNER,
        on_pull_request=True,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="windows",
        build_environment="pytorch-win-vs2019-cuda11-cudnn8-py3",
        cuda_version="11.1",
        test_runner_type=WINDOWS_CUDA_TEST_RUNNER,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="windows",
        build_environment="periodic-pytorch-win-vs2019-cuda11-cudnn8-py3",
        cuda_version="11.3",
        test_runner_type=WINDOWS_CUDA_TEST_RUNNER,
        num_test_shards=2,
        is_scheduled="45 0,4,8,12,16,20 * * *",
    ),
]

LINUX_WORKFLOWS = [
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-xenial-py3.6-gcc5.4",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc5.4",
        test_runner_type=LINUX_CPU_TEST_RUNNER,
        on_pull_request=True,
        enable_doc_jobs=True,
        num_test_shards=2,
    ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-paralleltbb-linux-xenial-py3.6-gcc5.4",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc5.4",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-parallelnative-linux-xenial-py3.6-gcc5.4",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc5.4",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-pure_torch-linux-xenial-py3.6-gcc5.4",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc5.4",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-gcc7",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc7",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-asan",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-asan",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang7-onnx",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang7-onnx",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-bionic-cuda10.2-cudnn7-py3.9-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-cuda10.2-cudnn7-py3.9-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-xenial-cuda10.2-cudnn7-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda10.2-cudnn7-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        enable_jit_legacy_test=1,
        enable_multigpu_test=1,
        enable_nogpu_no_avx_test=1,
        enable_nogpu_no_avx2_test=1,
        enable_slow_test=1,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-libtorch-linux-xenial-cuda10.2-cudnn7-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda10.2-cudnn7-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        is_libtorch=True,
    ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-xenial-cuda11.1-cudnn8-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda11.1-cudnn8-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        num_test_shards=2,
    ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-libtorch-linux-xenial-cuda11.1-cudnn8-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda11.1-cudnn8-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        is_libtorch=True,
    ),
    CIWorkflow(
        arch="linux",
        build_environment="periodic-pytorch-linux-xenial-cuda11.3-cudnn8-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda11.3-cudnn8-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        num_test_shards=2,
        is_scheduled="45 0,4,8,12,16,20 * * *",
    ),
    CIWorkflow(
        arch="linux",
        build_environment="periodic-pytorch-libtorch-linux-xenial-cuda11.3-cudnn8-py3.6-gcc7",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-cuda11.3-cudnn8-py3-gcc7",
        test_runner_type=LINUX_CUDA_TEST_RUNNER,
        is_libtorch=True,
        is_scheduled="45 0,4,8,12,16,20 * * *",
    ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-bionic-py3.6-clang9-noarch",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-py3.6-clang9",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-xla-linux-bionic-py3.6-clang9",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-py3.6-clang9",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-vulkan-linux-bionic-py3.6-clang9",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-py3.6-clang9",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-bionic-py3.8-gcc9-coverage",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-py3.8-gcc9",
        test_runner_type=LINUX_CPU_TEST_RUNNER,
        on_pull_request=True,
        num_test_shards=2,
    ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-bionic-rocm3.9-py3.6",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-bionic-rocm3.9-py3.6",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-android-ndk-r19c-x86_32",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-android-ndk-r19c-x86_64",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-android-ndk-r19c-arm-v7a",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-android-ndk-r19c-arm-v8a",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-mobile",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-asan",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-mobile-custom-dynamic",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-mobile-custom-static",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
    # CIWorkflow(
    #     arch="linux",
    #     build_environment="pytorch-linux-xenial-py3.6-clang5-mobile-code-analysis",
    #     docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3-clang5-android-ndk-r19c",
    #     test_runner_type=LINUX_CPU_TEST_RUNNER,
    # ),
]


BAZEL_WORKFLOWS = [
    CIWorkflow(
        arch="linux",
        build_environment="pytorch-linux-xenial-py3.6-gcc7-bazel-test",
        docker_image_base=f"{DOCKER_REGISTRY}/pytorch/pytorch-linux-xenial-py3.6-gcc7",
        test_runner_type=LINUX_CPU_TEST_RUNNER,
    ),
]

if __name__ == "__main__":
    jinja_env = jinja2.Environment(
        variable_start_string="!{{",
        loader=jinja2.FileSystemLoader(str(GITHUB_DIR.joinpath("templates"))),
    )
    template_and_workflows = [
        (jinja_env.get_template("linux_ci_workflow.yml.j2"), LINUX_WORKFLOWS),
        (jinja_env.get_template("windows_ci_workflow.yml.j2"), WINDOWS_WORKFLOWS),
        (jinja_env.get_template("bazel_ci_workflow.yml.j2"), BAZEL_WORKFLOWS),
    ]
    for template, workflows in template_and_workflows:
        for workflow in workflows:
            workflow.assert_valid()
            workflow.generate_workflow_file(workflow_template=template)
