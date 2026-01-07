#! /bin/bash

# This script tests the creation, activation, and deactivation of 4 different 
# types of kernels to verify that the kernel management scripts are working correctly.
# It should be run from within a JupyterLab terminal session.

set -e

# --- Shell and Environment Initialization ---
# Default to 'mamba' if CONDA_VER is not set.
export CONDA_VER=${CONDA_VER:-mamba}
# Initialize conda/mamba shell functions for this script's execution context.
eval $(${CONDA_VER} shell hook --shell bash)

# --- Setup ---
echo "========================================================================"
echo "Starting Kernel Verification Test (using ${CONDA_VER})"
echo "========================================================================"

# Get the directory where the kernel tools are located
KERNEL_TOOLS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Define a custom location for environments and ensure it exists
CUSTOM_ENVROOT="${HOME}/custom_envs"
mkdir -p "${CUSTOM_ENVROOT}"

# Store the original state to verify deactivation later
ORIGINAL_PYTHON_PATH=$(which python)
ORIGINAL_CONDA_PREFIX="${CONDA_PREFIX:-}"
ORIGINAL_VIRTUAL_ENV="${VIRTUAL_ENV:-}"

echo "Initial \`which python\` is: ${ORIGINAL_PYTHON_PATH}"
echo "Initial CONDA_PREFIX is: ${ORIGINAL_CONDA_PREFIX}"
echo "Initial VIRTUAL_ENV is: ${ORIGINAL_VIRTUAL_ENV}"
# ENVROOT is now defined in kernel-utils, sourced by each script.
echo "Custom ENVROOT:  ${CUSTOM_ENVROOT}"

# Helper function for activation verification
verify_activation() {
    local env_type=$1
    local env_name=$2
    local expected_path_part=$3
    local success=true

    echo "--> Verifying activation of '${env_name}'..."

    local active_env_path=""
    if [[ "${env_type}" == "conda" ]]; then
        active_env_path="${CONDA_PREFIX}"
    elif [[ "${env_type}" == "venv" ]]; then
        active_env_path="${VIRTUAL_ENV}"
    fi

    if [[ -z "${active_env_path}" ]]; then
        echo "ERROR: Activation variable (CONDA_PREFIX/VIRTUAL_ENV) is not set."
        success=false
    elif [[ "${active_env_path}" != *"${expected_path_part}"* ]]; then
        echo "ERROR: Activation path is incorrect."
        echo "  Expected to contain: ${expected_path_part}"
        echo "  Actual path: ${active_env_path}"
        success=false
    else
        echo "OK: Activation path is correct."
    fi

    local current_python_path=$(which python)
    if [[ "${current_python_path}" != "${active_env_path}/bin/python" ]]; then
        echo "ERROR: \`which python\` points to the wrong executable."
        echo "  Expected: ${active_env_path}/bin/python"
        echo "  Actual:   ${current_python_path}"
        success=false
    else
        echo "OK: \`which python\` is correct."
    fi

    if [[ "${success}" == "false" ]]; then
        echo "VERIFICATION FAILED for ${env_name}"
        exit 1
    fi
    echo "SUCCESS: Activation for '${env_name}' verified."
}

# Helper function for deactivation verification
verify_deactivation() {
    local env_name=$1
    echo "--> Verifying deactivation of '${env_name}'..."
    
    local current_conda_prefix="${CONDA_PREFIX:-}"
    if [[ "${current_conda_prefix}" != "${ORIGINAL_CONDA_PREFIX}" ]]; then
        echo "ERROR: CONDA_PREFIX did not revert to its original value."
        echo "  Expected: '${ORIGINAL_CONDA_PREFIX}'"
        echo "  Actual:   '${current_conda_prefix}'"
        exit 1
    fi

    local current_virtual_env="${VIRTUAL_ENV:-}"
    if [[ "${current_virtual_env}" != "${ORIGINAL_VIRTUAL_ENV}" ]]; then
        echo "ERROR: VIRTUAL_ENV did not revert to its original value."
        echo "  Expected: '${ORIGINAL_VIRTUAL_ENV}'"
        echo "  Actual:   '${current_virtual_env}'"
        exit 1
    fi
    
    local current_python_path=$(which python)
    if [[ "${current_python_path}" != "${ORIGINAL_PYTHON_PATH}" ]]; then
        echo "ERROR: \`which python\` did not revert to original path."
        echo "  Expected: ${ORIGINAL_PYTHON_PATH}"
        echo "  Actual:   ${current_python_path}"
        exit 1
    fi

    echo "SUCCESS: Deactivation for '${env_name}' verified."
}

# --- Test 1: Conda kernel in default ENVROOT ---
echo
echo "=== Test 1: Conda + Default ENVROOT ==="
"${KERNEL_TOOLS}/kernel-create" "conda-default"
source "${KERNEL_TOOLS}/kernel-activate" "conda-default"
verify_activation "conda" "conda-default" "${HOME}/envs/conda/conda-default"
source "${KERNEL_TOOLS}/kernel-deactivate" "conda-default"
verify_deactivation "conda-default"

# --- Test 2: Conda kernel in custom ENVROOT ---
echo
echo "=== Test 2: Conda + Custom ENVROOT ==="
"${KERNEL_TOOLS}/kernel-create" "conda-custom" "3.11" "Conda Custom" "${CUSTOM_ENVROOT}"
source "${KERNEL_TOOLS}/kernel-activate" "conda-custom" "${CUSTOM_ENVROOT}"
verify_activation "conda" "conda-custom" "${CUSTOM_ENVROOT}/conda/conda-custom"
source "${KERNEL_TOOLS}/kernel-deactivate" "conda-custom"
verify_deactivation "conda-custom"

# --- Test 3: Virtualenv kernel in default ENVROOT ---
echo
echo "=== Test 3: Venv + Default ENVROOT ==="
"${KERNEL_TOOLS}/kernel-create-venv" "venv-default"
source "${KERNEL_TOOLS}/kernel-activate" "venv-default"
verify_activation "venv" "venv-default" "${HOME}/envs/venv/venv-default"
source "${KERNEL_TOOLS}/kernel-deactivate" "venv-default"
verify_deactivation "venv-default"

# --- Test 4: Virtualenv kernel in custom ENVROOT ---
echo
echo "=== Test 4: Venv + Custom ENVROOT ==="
"${KERNEL_TOOLS}/kernel-create-venv" "venv-custom" "Venv Custom" "${CUSTOM_ENVROOT}"
source "${KERNEL_TOOLS}/kernel-activate" "venv-custom" "${CUSTOM_ENVROOT}"
verify_activation "venv" "venv-custom" "${CUSTOM_ENVROOT}/venv/venv-custom"
source "${KERNEL_TOOLS}/kernel-deactivate" "venv-custom"
verify_deactivation "venv-custom"


# --- Final Verification ---
echo
echo "========================================================================"
echo "Final Verification: Listing all created kernels..."
echo "========================================================================"
"${KERNEL_TOOLS}/kernel-list"

echo
echo "========================================================================"
echo "Test Complete!"
echo "All activation and deactivation tests passed."
echo "The following kernels remain available for manual inspection:"
echo "  - conda-default"
echo "  - Conda Custom"
echo "  - venv-default"
echo "  - Venv Custom"
echo "========================================================================"