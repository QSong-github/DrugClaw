"""
Configuration file for DrugClaw — Drug-Specialized Agentic RAG System
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """System configuration and constants"""

    def __init__(self, key_file: str | None = None):
        """Initialize configuration from JSON key file"""
        repo_root = Path(__file__).resolve().parent.parent
        default_key_file = (
            os.environ.get("DRUGCLAW_KEY_FILE")
            or str(repo_root / "navigator_api_keys.json")
        )
        key_path = Path(key_file or default_key_file).expanduser()

        if not key_path.is_absolute():
            key_path = (Path.cwd() / key_path).resolve()

        with open(key_path, 'r') as file:
            data = json.load(file)

        self.OPENAI_API_KEY = data.get('OPENAI_API_KEY')
        self.base_url = data.get('base_url')
        os.environ['TOOLKIT_API_KEY'] = self.OPENAI_API_KEY

        # Model settings
        self.MODEL_NAME = "gpt-oss-120b"
        self.TEMPERATURE = 0.7
        self.MAX_TOKENS = 2000

        # System parameters
        self.MAX_ITERATIONS = 0
        self.EVIDENCE_THRESHOLD_EPSILON = 0.1  # Minimum marginal information gain
        self.MIN_EVIDENCE_SCORE = 0.7  # Minimum evidence sufficiency score
        self.MAX_SUBGRAPH_SIZE = 100  # Maximum entities in evidence subgraph

        # Agent weights for re-ranking
        self.SEMANTIC_WEIGHT = 0.6
        self.STRUCTURAL_WEIGHT = 0.4


        # ------------------------------------------------------------------
        # Per-skill configurations — 68 LLM-friendly resources
        # Organized by subcategory (from 68DrugResources.xlsx).
        #
        # Each key is the skill's .name attribute.
        # Leave {} to use defaults. Set paths for LOCAL_FILE skills.
        # CLI skills (ChEMBL, ChEBI, KEGG Drug) auto-detect installed packages.
        # ------------------------------------------------------------------
        self.SKILL_CONFIGS: Dict[str, Any] = {

            # ── DTI (Drug-Target Interaction) ──────────────────────────
            # ChEMBL: CLI-first via chembl_webresource_client, REST fallback
            "ChEMBL": {"timeout": 20},
            # BindingDB: public REST API
            "BindingDB": {"timeout": 20},
            # DGIdb: public GraphQL
            "DGIdb": {"timeout": 20},
            # Open Targets: public GraphQL
            "Open Targets Platform": {"timeout": 25},
            # TTD: download flat files from ttd.idrblab.cn
            "TTD": {
                "drug_target_tsv": "",   # e.g. "/data/ttd/P1-01-TTD_target_download.txt"
            },
            # STITCH: public REST (STRING API)
            "STITCH": {"timeout": 20, "species": 9606},
            # TarKG: local TSV download from tarkg.ddtmlab.org
            "TarKG": {
                "tsv_path": "",          # e.g. "/data/tarkg/tarkg.tsv"
            },
            # PROMISCUOUS 2.0: no public API (registered but unavailable)
            "PROMISCUOUS 2.0": {},
            # GDKD: Synapse platform download
            "GDKD": {
                "csv_path": "",          # e.g. "/data/gdkd/gdkd.csv"
            },
            # DTC: download CSV from drugtargetcommons.fimm.fi
            "DTC": {
                "csv_path": "",          # e.g. "/data/dtc/DTC_data.csv"
            },

            # ── ADR (Adverse Drug Reaction) ────────────────────────────
            # FAERS: pre-process FDA quarterly files into CSV
            # Expected: drug_name, adverse_event (or pt), report_count (or reports)
            "FAERS": {
                "csv_path": "",          # e.g. "/data/faers/faers_processed.csv"
                "min_reports": 5,
            },
            # SIDER: download meddra_all_se.tsv from sideeffects.embl.de
            "SIDER": {
                "se_tsv": "",            # e.g. "/data/sider/meddra_all_se.tsv"
                "name_to_stitch": {},    # {drug_name_lower: stitch_id}
            },
            # nSIDES: public REST API
            "nSIDES": {"timeout": 20},
            # VigiAccess: no public API
            "VigiAccess": {},
            # ADReCS: REST API
            "ADReCS": {"timeout": 20},

            # ── Drug Knowledgebase ─────────────────────────────────────
            # UniD3: local GraphML files (paths from KG_ENDPOINTS['unid3'])
            "UniD3": {
                'UniD3_Level1_DDM': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L1T1.graphml'),
                'UniD3_Level1_DEA': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L1T2.graphml'),
                'UniD3_Level1_DTA': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L1T3.graphml'),
                'UniD3_Level2_DDM': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L2T1.graphml'),
                'UniD3_Level2_DEA': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L2T2.graphml'),
                'UniD3_Level2_DTA': str(repo_root / 'resources_metadata/drug_knowledgebase/UniD3/UniD3_L2T3.graphml'),
            },
            # DrugBank: register at go.drugbank.com for full API
            "DrugBank": {
                "api_key": "",           # optional — full access requires key
                "timeout": 20,
            },
            # IUPHAR: public REST API
            "IUPHAR/BPS Guide to Pharmacology": {"timeout": 20},
            # DrugCentral: public REST API
            "DrugCentral": {"timeout": 20},
            # Drugs.com: no public API
            "Drugs.com": {},
            # PharmKG: local TSV from github.com/MindRank-Biotech/PharmKG
            "PharmKG": {
                "train_tsv": "",         # e.g. "/data/pharmkg/train.tsv"
            },
            # WHO EML: local CSV from WHO download
            "WHO Essential Medicines List": {
                "csv_path": "",          # e.g. "/data/who_eml/eml.csv"
            },
            # FDA Orange Book: openFDA drugs@FDA API
            "FDA Orange Book": {
                "api_key": "",           # optional
                "timeout": 20,
            },
            # CPIC: public REST API
            "CPIC": {"timeout": 20},

            # ── Drug Mechanism ─────────────────────────────────────────
            # DRUGMECHDB: auto-downloads from GitHub if local_path missing
            "DRUGMECHDB": {
                "local_path": "",        # e.g. "/data/drugmechdb/indication_paths.json"
                "fetch_remote": True,
            },

            # ── Drug Labeling ──────────────────────────────────────────
            "openFDA Human Drug": {
                "api_key": "",           # optional — raises rate limit
                "timeout": 15,
            },
            "DailyMed": {"timeout": 20},
            "RxList Drug Descriptions": {},  # no public API
            "MedlinePlus Drug Info": {"timeout": 20},

            # ── Drug Ontology ──────────────────────────────────────────
            "RxNorm": {"timeout": 20},
            "ATC/DDD": {"timeout": 20},
            "NDF-RT": {"timeout": 20},
            # ChEBI: CLI-first via libchebipy, REST fallback
            "ChEBI": {"timeout": 20},

            # ── Drug Repurposing ───────────────────────────────────────
            "RepoDB": {
                "csv_path": str(repo_root / "resources_metadata/drug_repurposing/RepoDB/full.csv"),
                "include_failed": False,
            },
            "DRKG": {
                "drkg_tsv": "",          # e.g. "/data/drkg/drkg.tsv"
            },
            "OREGANO": {
                "data_path": "",         # e.g. "/data/oregano/"
            },
            "Drug Repurposing Hub": {
                "csv_path": "",          # e.g. "/data/repurposing_hub/repurposing_drugs.csv"
            },
            "DrugRepoBank": {},
            "RepurposeDrugs": {},
            "DrugRepurposing Online": {},
            "CancerDR": {},
            "EK-DRD": {},

            # ── Pharmacogenomics ───────────────────────────────────────
            "PharmGKB": {"timeout": 20},

            # ── DDI (Drug-Drug Interaction) ────────────────────────────
            # MecDDI: download from mecddi.idrblab.net
            "MecDDI": {
                "csv_path": "",          # e.g. "/data/mecddi/mecddi.csv"
            },
            # DDInter: public REST API
            "DDInter": {"timeout": 20},
            # KEGG Drug: CLI-first via bioservices, REST fallback
            "KEGG Drug": {"timeout": 20},

            # ── Drug Toxicity ──────────────────────────────────────────
            "UniTox": {
                "csv_path": "",          # e.g. "/data/unitox/unitox.csv"
            },
            "LiverTox": {"timeout": 20},
            "DILIrank": {
                "csv_path": "",          # e.g. "/data/dilirank/DILIrank.csv"
            },
            "DILI": {
                "csv_path": "",          # e.g. "/data/dili/dili.csv"
            },

            # ── Drug Combination ───────────────────────────────────────
            "DrugCombDB": {
                "csv_path": "",          # e.g. "/data/drugcombdb/drugcombdb.csv"
            },
            "CDCDB": {
                "csv_path": "",          # e.g. "/data/cdcdb/cdcdb.csv"
            },
            "DrugComb": {
                "csv_path": "",          # e.g. "/data/drugcomb/drugcomb.csv"
            },
            "DCDB": {
                "csv_path": "",          # e.g. "/data/dcdb/dcdb.csv"
            },

            # ── Drug Molecular Property ────────────────────────────────
            "GDSC": {
                "csv_path": "",          # e.g. "/data/gdsc/GDSC2_fitted_dose_response.csv"
            },

            # ── Drug Disease ───────────────────────────────────────────
            "SemaTyP": {
                "data_path": "",         # e.g. "/data/sematyp/"
            },

            # ── Drug Review (dataset, no API) ──────────────────────────
            "WebMD Drug Reviews": {},
            "askapatient": {},
            "Drug Reviews (Drugs.com)": {},

            # ── Drug NLP (dataset, local files) ───────────────────────
            "DrugEHRQA": {},
            "DDI Corpus 2013": {},
            "DrugProt": {},
            "ADE Corpus": {},
            "n2c2 2018 Track 2": {},
            "CADEC": {},
            "PsyTAR": {},
            "TAC 2017 ADR": {},
            "PHEE": {},
        }

        # ------------------------------------------------------------------
        # Default active skills — only implemented skills (25 with example.py + SKILL.md)
        # ------------------------------------------------------------------
        self.DEFAULT_ACTIVE_SKILLS = [
            # DTI (6 implemented)
            "ChEMBL",           # CLI-first (chembl_webresource_client)
            "BindingDB",        # REST API
            "DGIdb",            # REST API / GraphQL
            "Open Targets Platform",  # REST API / GraphQL
            "TTD",              # LOCAL_FILE
            "STITCH",           # REST API
            # ADR (2 implemented)
            "FAERS",            # DATASET
            "SIDER",            # LOCAL_FILE
            # Drug Knowledgebase (5 implemented)
            "UniD3",            # LOCAL_FILE (GraphML)
            "DrugBank",         # REST API (API key optional)
            "IUPHAR/BPS Guide to Pharmacology",  # REST API
            "DrugCentral",      # REST API
            "CPIC",             # REST API
            # Drug Mechanism (1 implemented)
            "DRUGMECHDB",       # REST API (auto-download)
            # Drug Labeling (3 implemented)
            "openFDA Human Drug",    # REST API
            "DailyMed",         # REST API
            "MedlinePlus Drug Info", # REST API
            # Drug Ontology (2 implemented)
            "RxNorm",           # REST API
            "ChEBI",            # CLI-first (libchebipy)
            # Drug Repurposing (1 implemented)
            "RepoDB",           # DATASET
            # Pharmacogenomics (1 implemented)
            "PharmGKB",         # REST API
            # DDI (3 implemented)
            "MecDDI",           # LOCAL_FILE
            "DDInter",          # REST API
            "KEGG Drug",        # CLI-first (bioservices)
            # Drug Review (1 implemented)
            "WebMD Drug Reviews",   # DATASET
        ]

    def get_llm_config(self) -> Dict[str, Any]:
        """Return LLM configuration dictionary"""
        return {
            'api_key': self.OPENAI_API_KEY,
            'base_url': self.base_url,
            'model': self.MODEL_NAME,
            'temperature': self.TEMPERATURE,
            'max_tokens': self.MAX_TOKENS
        }
