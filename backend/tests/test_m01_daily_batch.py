"""
Test suite for M01 Daily Batch Job

Tests the command-line entry point for the M01 daily batch workflow.
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401 guardrails

import sys
import pytest
from unittest.mock import patch, MagicMock
from app.jobs import m01_daily_batch


def test_parse_args_success():
    """Test that parse_args correctly parses valid arguments."""
    test_args = [
        "m01_daily_batch.py",
        "--base-url", "https://api.example.com",
        "--sources", "newsapi,mock",
        "--limit-per-source", "20",
        "--min-score", "0.6"
    ]
    
    with patch.object(sys, 'argv', test_args):
        args = m01_daily_batch.parse_args()
        
    assert args.base_url == "https://api.example.com"
    assert args.sources == "newsapi,mock"
    assert args.limit_per_source == 20
    assert args.min_score == 0.6


def test_parse_args_missing_required():
    """Test that parse_args fails when required arguments are missing."""
    test_args = ["m01_daily_batch.py"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            m01_daily_batch.parse_args()


def test_main_validates_empty_base_url():
    """Test that main() validates empty base-url."""
    test_args = [
        "m01_daily_batch.py",
        "--base-url", "",
        "--sources", "mock",
        "--limit-per-source", "5",
        "--min-score", "0.5"
    ]
    
    with patch.object(sys, 'argv', test_args):
        exit_code = m01_daily_batch.main()
        
    assert exit_code == 1


def test_main_validates_no_sources():
    """Test that main() validates when no valid sources are provided."""
    test_args = [
        "m01_daily_batch.py",
        "--base-url", "https://api.example.com",
        "--sources", "",
        "--limit-per-source", "5",
        "--min-score", "0.5"
    ]
    
    with patch.object(sys, 'argv', test_args):
        exit_code = m01_daily_batch.main()
        
    assert exit_code == 1


@patch('app.jobs.m01_daily_batch.requests.post')
def test_run_ingestion_success(mock_post):
    """Test that run_ingestion makes correct API call."""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "articles_fetched": 10,
        "article_ids": [1, 2, 3, 4, 5]
    }
    mock_post.return_value = mock_response
    
    result = m01_daily_batch.run_ingestion(
        base_url="https://api.example.com",
        sources=["mock"],
        limit_per_source=5
    )
    
    assert result["articles_fetched"] == 10
    assert len(result["article_ids"]) == 5
    
    # Verify API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.example.com/api/news/ingest"
    assert call_args[1]["json"]["sources"] == ["mock"]
    assert call_args[1]["json"]["limit_per_source"] == 5


@patch('app.jobs.m01_daily_batch.requests.post')
def test_run_ranking_success(mock_post):
    """Test that run_ranking makes correct API call."""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ranked_articles": [
            {"id": 1, "score": 0.8},
            {"id": 2, "score": 0.7}
        ]
    }
    mock_post.return_value = mock_response
    
    result = m01_daily_batch.run_ranking(
        base_url="https://api.example.com",
        article_ids=[1, 2, 3],
        min_score=0.6
    )
    
    assert len(result["ranked_articles"]) == 2
    
    # Verify API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.example.com/api/news/rank"
    assert call_args[1]["json"]["article_ids"] == [1, 2, 3]
    assert call_args[1]["json"]["min_score"] == 0.6


def test_agents_module_import():
    """Test that the agents module can be imported (path fix works)."""
    # This test verifies that the sys.path fix in the module works correctly
    import agents.checks.router
    assert hasattr(agents.checks.router, 'should_offload')
    assert hasattr(agents.checks.router, 'offload_to_gemini')
