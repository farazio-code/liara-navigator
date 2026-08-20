from enum import StrEnum


class Mode(StrEnum):
    AUTO = "auto"
    ASK = "ask"
    GUIDE = "guide"
    DIAGNOSE = "diagnose"


class TaskFamily(StrEnum):
    DEPLOYMENT = "deployment"
    DOMAIN_DNS_SSL = "domain_dns_ssl"
    DATABASE = "database"
    GENERAL_DOCS = "general_docs"
    BILLING = "billing"
    OTHER = "other"


class ScopeCoverage(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    ASK_ONLY = "ask_only"
