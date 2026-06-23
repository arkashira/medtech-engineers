import json
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Engineer:
    name: str
    portfolio: str
    experience: int
    skills: list

@dataclass
class VettingResult:
    engineer: Engineer
    portfolio_review: str
    technical_assessment: str
    result: bool

def review_portfolio(engineer: Engineer) -> str:
    if engineer.portfolio:
        return "Portfolio reviewed and approved"
    else:
        return "Portfolio not provided or not approved"

def technical_assessment(engineer: Engineer) -> str:
    if engineer.skills:
        return "Technical assessment passed"
    else:
        return "Technical assessment failed"

def vet_engineer(engineer: Engineer) -> VettingResult:
    portfolio_review = review_portfolio(engineer)
    technical_assessment_result = technical_assessment(engineer)
    result = portfolio_review == "Portfolio reviewed and approved" and technical_assessment_result == "Technical assessment passed"
    return VettingResult(engineer, portfolio_review, technical_assessment_result, result)

def onboard_engineer(engineer: Engineer, vetting_result: VettingResult) -> str:
    if vetting_result.result:
        return f"Engineer {engineer.name} onboarded successfully"
    else:
        return f"Engineer {engineer.name} not onboarded due to vetting failure"

def vetting_process(engineer: Engineer) -> str:
    vetting_result = vet_engineer(engineer)
    return onboard_engineer(engineer, vetting_result)
