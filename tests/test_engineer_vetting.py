from engineer_vetting import Engineer, VettingResult, vet_engineer, onboard_engineer, vetting_process
import pytest

@pytest.fixture
def engineer():
    return Engineer("John Doe", "https://example.com/portfolio", 5, ["Python", "Java"])

def test_review_portfolio(engineer):
    assert vet_engineer(engineer).portfolio_review == "Portfolio reviewed and approved"

def test_review_portfolio_no_portfolio():
    engineer_no_portfolio = Engineer("John Doe", "", 5, ["Python", "Java"])
    assert vet_engineer(engineer_no_portfolio).portfolio_review == "Portfolio not provided or not approved"

def test_technical_assessment(engineer):
    assert vet_engineer(engineer).technical_assessment == "Technical assessment passed"

def test_technical_assessment_no_skills():
    engineer_no_skills = Engineer("John Doe", "https://example.com/portfolio", 5, [])
    assert vet_engineer(engineer_no_skills).technical_assessment == "Technical assessment failed"

def test_vet_engineer(engineer):
    vetting_result = vet_engineer(engineer)
    assert vetting_result.result

def test_vet_engineer_no_portfolio(engineer):
    engineer_no_portfolio = Engineer("John Doe", "", 5, ["Python", "Java"])
    vetting_result = vet_engineer(engineer_no_portfolio)
    assert not vetting_result.result

def test_onboard_engineer(engineer):
    vetting_result = vet_engineer(engineer)
    assert onboard_engineer(engineer, vetting_result) == f"Engineer {engineer.name} onboarded successfully"

def test_onboard_engineer_no_portfolio(engineer):
    engineer_no_portfolio = Engineer("John Doe", "", 5, ["Python", "Java"])
    vetting_result = vet_engineer(engineer_no_portfolio)
    assert onboard_engineer(engineer_no_portfolio, vetting_result) == f"Engineer {engineer_no_portfolio.name} not onboarded due to vetting failure"

def test_vetting_process(engineer):
    assert vetting_process(engineer) == f"Engineer {engineer.name} onboarded successfully"
