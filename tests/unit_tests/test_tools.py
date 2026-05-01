"""Unit tests for the agent tools."""

from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest

from stem_agent.tools import (
    calculator,
    file_reader,
    file_search,
    get_tools_by_names,
    tools_description,
    utc_now,
    web_search,
)


def test_utc_now() -> None:
    result = utc_now.invoke({})
    assert isinstance(result, str)
    assert "T" in result


def test_calculator_valid() -> None:
    assert calculator.invoke({"expression": "2 + 3 * 4"}) == "14"
    assert calculator.invoke({"expression": "(10 - 2) / 2"}) == "4.0"
    assert calculator.invoke({"expression": "2 ** 3"}) == "8"


def test_calculator_invalid() -> None:
    with pytest.raises(ValueError, match="Expression contains unsupported syntax"):
        calculator.invoke({"expression": "__import__('os').system('ls')"})


def test_file_reader_valid(tmp_path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")
    result = file_reader.invoke({"path": str(test_file)})
    assert result == "hello world"


def test_file_reader_missing() -> None:
    result = file_reader.invoke({"path": "non_existent_file.txt"})
    assert "Error" in result


@patch("stem_agent.configuration.CONFIG")
def test_web_search_no_api_key(mock_config) -> None:
    mock_config.tavily_api_key = None
    result = web_search.invoke({"query": "test"})
    assert "TAVILY_API_KEY is not configured" in result


@patch("stem_agent.configuration.CONFIG")
@patch("tavily.TavilyClient")
def test_web_search_success(mock_tavily_class, mock_config) -> None:
    mock_config.tavily_api_key = "fake_key"
    mock_client = MagicMock()
    mock_tavily_class.return_value = mock_client
    mock_client.search.return_value = {
        "results": [
            {"title": "Result 1", "content": "Content 1", "url": "http://1"},
        ]
    }

    result = web_search.invoke({"query": "python news"})
    assert "Result 1" in result
    assert "Content 1" in result


def test_get_tools_by_names() -> None:
    tools = get_tools_by_names(["calculator", "utc_now", "invalid_tool"])
    assert len(tools) == 2
    assert tools[0].name == "calculator"
    assert tools[1].name == "utc_now"


def test_file_search_valid(tmp_path) -> None:
    # Create nested structure
    subdir = tmp_path / "a" / "b"
    subdir.mkdir(parents=True)
    target = subdir / "find_me.py"
    target.write_text("print('found')")

    result = file_search.invoke({"filename": "find_me.py", "directory": str(tmp_path)})
    assert str(target) in result


def test_file_search_missing(tmp_path) -> None:
    result = file_search.invoke({"filename": "missing.txt", "directory": str(tmp_path)})
    assert "not found" in result


def test_file_search_invalid_dir() -> None:
    result = file_search.invoke({"filename": "test.txt", "directory": "/non/existent/path"})
    assert "Error" in result


def test_tools_description() -> None:
    desc = tools_description()
    assert "- **utc_now**" in desc
    assert "- **calculator**" in desc
    assert "- **file_reader**" in desc
    assert "- **file_search**" in desc
