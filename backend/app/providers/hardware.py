from __future__ import annotations

import os
import platform
import shutil
import subprocess
import psutil
from pydantic import BaseModel, Field


class RecommendedModelSpec(BaseModel):
    model_tag: str
    display_name: str
    parameter_count: str
    download_size_gb: float
    estimated_vram_gb: float
    recommended_context: int
    suitability_tier: str  # optimal_installed | recommended_upgrade | high_capacity | heavy
    suitability_reason: str
    license_name: str
    license_notes: str
    pull_command: str
    is_currently_installed: bool = False


class HardwareReport(BaseModel):
    os_name: str
    os_release: str
    architecture: str
    cpu_name: str
    cpu_physical_cores: int
    cpu_logical_cores: int
    ram_total_gb: float
    ram_available_gb: float
    gpu_detected: bool
    gpu_name: str
    gpu_vram_total_gb: float
    gpu_vram_free_gb: float
    disk_free_gb: float
    ollama_binary_detected: bool
    ollama_version: str
    hardware_tier: str
    recommendations: list[RecommendedModelSpec] = Field(default_factory=list)


def _detect_gpu_via_nvidia_smi() -> tuple[bool, str, float, float]:
    """Query nvidia-smi for exact VRAM (avoids Windows WMI 4GB uint32 cap)."""
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return False, "Integrated / CPU Only", 0.0, 0.0
    try:
        proc = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=name,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            first_line = proc.stdout.strip().splitlines()[0]
            parts = [p.strip() for p in first_line.split(",")]
            if len(parts) >= 3:
                name = parts[0]
                total_mib = float(parts[1])
                free_mib = float(parts[2])
                return True, name, round(total_mib / 1024.0, 2), round(free_mib / 1024.0, 2)
    except Exception:
        pass
    return False, "Integrated / CPU Only", 0.0, 0.0


def _detect_ollama_cli() -> tuple[bool, str]:
    ollama_bin = shutil.which("ollama")
    if not ollama_bin:
        return False, "Not found in PATH"
    try:
        proc = subprocess.run(
            [ollama_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        out = (proc.stdout or proc.stderr or "").strip()
        return True, out or "Installed"
    except Exception:
        return True, "Installed"


def inspect_host_hardware(installed_model_names: list[str] | None = None) -> HardwareReport:
    installed_set = {m.lower() for m in (installed_model_names or [])}
    vm = psutil.virtual_memory()
    ram_total_gb = round(vm.total / (1024**3), 2)
    ram_avail_gb = round(vm.available / (1024**3), 2)

    disk_usage = psutil.disk_usage(os.getcwd())
    disk_free_gb = round(disk_usage.free / (1024**3), 2)

    gpu_detected, gpu_name, vram_total_gb, vram_free_gb = _detect_gpu_via_nvidia_smi()
    ollama_detected, ollama_version = _detect_ollama_cli()

    cpu_name = platform.processor() or "x86_64 Multi-Core Processor"
    if platform.system() == "Windows":
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                cpu_name = proc.stdout.strip().splitlines()[0].strip()
        except Exception:
            pass

    if vram_total_gb >= 12.0 or ram_total_gb >= 28.0:
        hardware_tier = "Workstation High-VRAM (Supports 4B to 14B Local Models in GPU VRAM)"
    elif vram_total_gb >= 6.0 or ram_total_gb >= 16.0:
        hardware_tier = "Mid-Range GPU (Supports 4B to 8B Local Models)"
    else:
        hardware_tier = "Entry Local Tier (Recommended 1.5B to 4B Quantized Models)"

    candidates = [
        RecommendedModelSpec(
            model_tag="qwen3.5:9b",
            display_name="Qwen 3.5 (9B) — Primary Flagship",
            parameter_count="9B",
            download_size_gb=6.6,
            estimated_vram_gb=7.2,
            recommended_context=32768 if vram_total_gb >= 12 else 16384,
            suitability_tier="optimal_installed" if "qwen3.5:9b" in installed_set else "recommended_upgrade",
            suitability_reason=(
                f"Active primary model. Uses ~7.2 GB of your {vram_total_gb} GB VRAM for real-time curriculum synthesis, "
                "deep Socratic tutoring, and CodeChef-style builder labs."
            ),
            license_name="Apache License 2.0",
            license_notes="Permissive open-source license by Alibaba Cloud Qwen team.",
            pull_command="ollama pull qwen3.5:9b",
            is_currently_installed="qwen3.5:9b" in installed_set,
        ),
        RecommendedModelSpec(
            model_tag="qwen3.5:4b",
            display_name="Qwen 3.5 (4B)",
            parameter_count="4B",
            download_size_gb=3.4,
            estimated_vram_gb=3.8,
            recommended_context=32768 if vram_total_gb >= 12 else 16384,
            suitability_tier="optimal_installed" if "qwen3.5:4b" in installed_set else "recommended_upgrade",
            suitability_reason=(
                f"Installed locally. Uses ~3.8 GB of your {vram_total_gb} GB VRAM, allowing ultra-fast "
                "token generation and large 16k-32k context windows."
            ),
            license_name="Apache License 2.0",
            license_notes="Permissive open-source license by Alibaba Cloud Qwen team.",
            pull_command="ollama pull qwen3.5:4b",
            is_currently_installed="qwen3.5:4b" in installed_set,
        ),
        RecommendedModelSpec(
            model_tag="gemma3:4b",
            display_name="Google Gemma 3 (4B)",
            parameter_count="4B",
            download_size_gb=3.3,
            estimated_vram_gb=3.6,
            recommended_context=32768 if vram_total_gb >= 12 else 16384,
            suitability_tier="optimal_installed" if "gemma3:4b" in installed_set else "recommended_upgrade",
            suitability_reason=(
                f"Installed locally. Lightweight 3.3 GB footprint fits effortlessly in your {vram_total_gb} GB VRAM "
                "for responsive Feynman feedback and recall question generation."
            ),
            license_name="Gemma Terms of Use",
            license_notes="Open-weight model subject to Google's Gemma Terms of Use and Prohibited Use Policy (not OSI open-source).",
            pull_command="ollama pull gemma3:4b",
            is_currently_installed="gemma3:4b" in installed_set,
        ),
        RecommendedModelSpec(
            model_tag="qwen3:8b",
            display_name="Qwen 3 (8B)",
            parameter_count="8B",
            download_size_gb=5.2,
            estimated_vram_gb=6.4,
            recommended_context=16384,
            suitability_tier="recommended_upgrade",
            suitability_reason=(
                f"Sweet-spot 8B model for your {gpu_name} ({vram_total_gb} GB VRAM). Runs 100% in GPU memory "
                "with strong mathematical derivation and code synthesis capabilities."
            ),
            license_name="Apache License 2.0",
            license_notes="Permissive Apache 2.0 license.",
            pull_command="ollama pull qwen3:8b",
            is_currently_installed="qwen3:8b" in installed_set,
        ),
        RecommendedModelSpec(
            model_tag="gemma3:12b",
            display_name="Google Gemma 3 (12B)",
            parameter_count="12B",
            download_size_gb=8.1,
            estimated_vram_gb=10.2,
            recommended_context=16384,
            suitability_tier="high_capacity" if vram_total_gb >= 12 else "heavy",
            suitability_reason=(
                f"High-depth 12B model requiring ~10.2 GB VRAM. Fits comfortably inside your {vram_total_gb} GB RTX A4500 VRAM."
                if vram_total_gb >= 12
                else "Requires ~10.2 GB VRAM; may partially offload to system RAM on smaller GPUs."
            ),
            license_name="Gemma Terms of Use",
            license_notes="Open-weight model subject to Google's Gemma Terms of Use (custom usage restrictions apply).",
            pull_command="ollama pull gemma3:12b",
            is_currently_installed="gemma3:12b" in installed_set,
        ),
        RecommendedModelSpec(
            model_tag="qwen3:14b",
            display_name="Qwen 3 (14B)",
            parameter_count="14B",
            download_size_gb=9.3,
            estimated_vram_gb=11.8,
            recommended_context=16384 if vram_total_gb >= 15 else 8192,
            suitability_tier="high_capacity" if vram_total_gb >= 14 else "heavy",
            suitability_reason=(
                f"Maximum local reasoning model for 16 GB VRAM workstations (~11.8 GB VRAM). Ideal for Research-Depth derivations."
            ),
            license_name="Apache License 2.0",
            license_notes="Permissive Apache 2.0 license.",
            pull_command="ollama pull qwen3:14b",
            is_currently_installed="qwen3:14b" in installed_set,
        ),
    ]

    return HardwareReport(
        os_name=platform.system(),
        os_release=platform.release(),
        architecture=platform.machine(),
        cpu_name=cpu_name,
        cpu_physical_cores=psutil.cpu_count(logical=False) or 1,
        cpu_logical_cores=psutil.cpu_count(logical=True) or 1,
        ram_total_gb=ram_total_gb,
        ram_available_gb=ram_avail_gb,
        gpu_detected=gpu_detected,
        gpu_name=gpu_name,
        gpu_vram_total_gb=vram_total_gb,
        gpu_vram_free_gb=vram_free_gb,
        disk_free_gb=disk_free_gb,
        ollama_binary_detected=ollama_detected,
        ollama_version=ollama_version,
        hardware_tier=hardware_tier,
        recommendations=candidates,
    )
