"""resource_monitor.py - リソース監視"""
import psutil
from loguru import logger

try:
    import pytorch_lightning as pl
except ImportError:
    import lightning.pytorch as pl


class ResourceMonitor(pl.Callback):
    """Resource monitoring callback"""
ECHO is on.
    def __init__(self):
        super().__init__()
        self.cpu_peak = 0.0
        self.ram_peak = 0.0
        self.gpu_peak = 0.0
        self.vram_peak = 0.0
ECHO is on.
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        """Monitor resources after each batch"""
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_peak = max(self.cpu_peak, cpu_percent)
ECHO is on.
        # RAM
        ram = psutil.virtual_memory()
        ram_gb = ram.used / 1024**3
        self.ram_peak = max(self.ram_peak, ram_gb)
ECHO is on.
        # GPU (if available)
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            vram_gb = info.used / 1024**3
            self.vram_peak = max(self.vram_peak, vram_gb)
ECHO is on.
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            self.gpu_peak = max(self.gpu_peak, util.gpu)
        except:
            pass
ECHO is on.
    def on_train_end(self, trainer, pl_module):
        """Log peak resources"""
        logger.info(f"Resource peaks: CPU={self.cpu_peak:.1f}%%, RAM={self.ram_peak:.1f}GB")
        if self.gpu_peak > 0:
            logger.info(f"GPU={self.gpu_peak:.1f}%%, VRAM={self.vram_peak:.1f}GB")
