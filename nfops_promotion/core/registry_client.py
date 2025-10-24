"""registry_client.py - Registry クライアント"""
import json
from pathlib import Path
from loguru import logger
from datetime import datetime
from nfops_promotion.models import ModelVersion, Stage


class RegistryClient:
    """Simple registry client (file-based for demo)"""
    
    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models_file = self.registry_path / "models.json"
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from file"""
        if self.models_file.exists():
            with open(self.models_file, encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
    
    def _save_registry(self):
        """Save registry to file"""
        with open(self.models_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)
    
    def create_model_version(
        self,
        model_name: str,
        run_id: str,
        stage: str = "Staging"
    ) -> ModelVersion:
        """Create new model version"""
        logger.info(f"Creating model version: {model_name}")
        
        if model_name not in self.registry:
            self.registry[model_name] = {
                "versions": [],
                "latest_version": 0
            }
        
        # Increment version
        version = self.registry[model_name]["latest_version"] + 1
        self.registry[model_name]["latest_version"] = version
        
        # Create version entry
        version_entry = {
            "version": version,
            "run_id": run_id,
            "stage": stage,
            "created_at": datetime.now().isoformat(),
            "tags": {}
        }
        
        self.registry[model_name]["versions"].append(version_entry)
        self._save_registry()
        
        logger.success(f"Created version {version} for {model_name}")
        
        return ModelVersion(
            name=model_name,
            version=version,
            stage=stage,
            run_id=run_id
        )
    
    def transition_stage(
        self,
        model_name: str,
        version: int,
        stage: str
    ):
        """Transition model version to new stage"""
        logger.info(f"Transitioning {model_name} v{version} to {stage}")
        
        if model_name not in self.registry:
            raise ValueError(f"Model {model_name} not found")
        
        # Find version
        for v in self.registry[model_name]["versions"]:
            if v["version"] == version:
                v["stage"] = stage
                v["stage_updated_at"] = datetime.now().isoformat()
                break
        
        self._save_registry()
        logger.success(f"Transitioned to {stage}")
    
    def get_model_version(
        self,
        model_name: str,
        version: int = None,
        stage: str = None
    ) -> ModelVersion:
        """Get model version by version number or stage"""
        if model_name not in self.registry:
            raise ValueError(f"Model {model_name} not found")
        
        versions = self.registry[model_name]["versions"]
        
        if version is not None:
            for v in versions:
                if v["version"] == version:
                    return ModelVersion(
                        name=model_name,
                        version=v["version"],
                        stage=v["stage"],
                        run_id=v["run_id"]
                    )
        elif stage is not None:
            for v in reversed(versions):
                if v["stage"] == stage:
                    return ModelVersion(
                        name=model_name,
                        version=v["version"],
                        stage=v["stage"],
                        run_id=v["run_id"]
                    )
        
        raise ValueError(f"Version not found for {model_name}")
