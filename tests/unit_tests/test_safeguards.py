from stem_agent.nodes.execute import execute
from stem_agent.graph import _route_after_execute
from langgraph.graph import END

def test_execute_respects_max_iterations():
    # Arrange: Setup state with current_iters == max_iters
    state = {
        "messages": [],
        "strategy": {"max_iterations": 3},
        "iteration_count": 3,
        "circuit_breaker_tripped": False
    }
    
    # Act
    result = execute(state)
    
    # Assert
    assert "reached maximum iteration budget" in result["execution_result"]

def test_route_after_execute_respects_max_iterations():
    # Arrange: Setup state where limit is reached
    state = {
        "strategy": {"max_iterations": 3},
        "iteration_count": 3,
        "circuit_breaker_tripped": False
    }
    
    # Act
    next_node = _route_after_execute(state)
    
    # Assert
    assert next_node == END

def test_execute_increments_counter():
    # Arrange
    class MockMsg:
        tool_calls = []
        content = "hello"

    class MockLLM:
        def invoke(self, msgs):
            return MockMsg()

    from unittest.mock import patch
    with patch("stem_agent.nodes.execute.init_chat_model") as mock_init:
        mock_init.return_value = MockLLM()
        
        state = {
            "messages": [],
            "strategy": {"max_iterations": 5, "reasoning_method": "react"},
            "iteration_count": 2,
            "signal": {"domain": "General"},
            "plan": [],
            "tool_manifest": [],
            "circuit_breaker_tripped": False
        }
        
        # Act
        result = execute(state)
        
        # Assert
        assert result["iteration_count"] == 3
