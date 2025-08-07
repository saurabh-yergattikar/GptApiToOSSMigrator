"""Tool registry for Harmony tools."""

from typing import Any, Dict, List, Optional

from ..core.models import Conversation


class ToolRegistry:
    """Registry for Harmony tools."""
    
    _tools: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, name: str, tool: Any) -> None:
        """Register a tool."""
        cls._tools[name] = tool
    
    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        """Get a tool by name."""
        return cls._tools.get(name)
    
    @classmethod
    def list(cls) -> List[str]:
        """List all registered tools."""
        return list(cls._tools.keys())
    
    @classmethod
    def execute(cls, name: str, conversation: Conversation, **kwargs) -> Dict[str, Any]:
        """Execute a tool."""
        tool = cls.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        if hasattr(tool, 'execute'):
            return tool.execute(conversation, **kwargs)
        else:
            raise ValueError(f"Tool '{name}' does not have an execute method")


class BaseTool:
    """Base class for Harmony tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, conversation: Conversation, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        raise NotImplementedError
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True


class WeatherTool(BaseTool):
    """Weather tool for Harmony."""
    
    def __init__(self):
        super().__init__(
            name="weather_tool",
            description="Get weather information for a location"
        )
    
    def execute(self, conversation: Conversation, **kwargs) -> Dict[str, Any]:
        """Execute weather tool."""
        location = kwargs.get('location', 'Unknown')
        
        # Simulate weather data
        return {
            "location": location,
            "temperature": "72°F",
            "condition": "Sunny",
            "humidity": "45%",
            "wind": "5 mph",
        }
    
    def validate_input(self, **kwargs) -> bool:
        """Validate weather tool input."""
        return 'location' in kwargs


class TimeTool(BaseTool):
    """Time tool for Harmony."""
    
    def __init__(self):
        super().__init__(
            name="time_tool",
            description="Get current time information"
        )
    
    def execute(self, conversation: Conversation, **kwargs) -> Dict[str, Any]:
        """Execute time tool."""
        import datetime
        
        now = datetime.datetime.now()
        return {
            "current_time": now.strftime("%H:%M:%S"),
            "current_date": now.strftime("%Y-%m-%d"),
            "timezone": "UTC",
            "timestamp": now.timestamp(),
        }


class CalculatorTool(BaseTool):
    """Calculator tool for Harmony."""
    
    def __init__(self):
        super().__init__(
            name="calculator_tool",
            description="Perform mathematical calculations"
        )
    
    def execute(self, conversation: Conversation, **kwargs) -> Dict[str, Any]:
        """Execute calculator tool."""
        expression = kwargs.get('expression', '')
        
        try:
            # Safe evaluation (in production, use a proper math parser)
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "expression": expression,
                "result": result,
                "success": True,
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False,
            }
    
    def validate_input(self, **kwargs) -> bool:
        """Validate calculator tool input."""
        return 'expression' in kwargs


# Register default tools
ToolRegistry.register("weather_tool", WeatherTool())
ToolRegistry.register("time_tool", TimeTool())
ToolRegistry.register("calculator_tool", CalculatorTool()) 