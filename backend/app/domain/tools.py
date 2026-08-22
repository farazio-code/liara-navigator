from enum import StrEnum


class ResourceFamily(StrEnum):
    PAAS = "paas"
    DOMAIN = "domain"
    DNS = "dns"
    DATABASE = "database"


class ToolName(StrEnum):
    INSPECT_SUMMARY = "inspect_summary"
    INSPECT_RUNTIME = "inspect_runtime"
    INSPECT_METRICS = "inspect_metrics"
    INSPECT_DNS = "inspect_dns"
    INSPECT_SSL = "inspect_ssl"


class ToolDecisionCode(StrEnum):
    ALLOWED = "allowed"
    POLICY_DENIED = "policy_denied"
    RESOURCE_NOT_ALLOWED = "resource_not_allowed"
    RATE_LIMITED = "rate_limited"
