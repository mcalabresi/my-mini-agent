import inspect
import json
from dataclasses import dataclass, field
from types import NoneType
from typing import Annotated, Any, Callable, Final, Union, get_args, get_origin


@dataclass
class Tools:
    """ "This class manages tools for the agent
    One of its duties will be to extract the info of the functions
    we pass and create a schema that the LLM can use
    """

    # tool schema attribute,
    TOOL_SCHEMA_ATTR: Final[str] = "__tool_schema__"
    # here is a dict of functions (tools), this represents the group of tools that the agent is allowed to use
    tools: dict[str, Callable[..., Any]] = field(default_factory=dict)

    @staticmethod
    def _annotation_to_schema(annotation: Any) -> dict[str, Any]:
        """converts annotation to JSON schema fragment
         (by annotation in Python we mean the types involved with the function (arguments and return type))

        :param annotation: Any - the annotation (of the function tool) that we want to convert to schema
        :return: dic[str, Any] - the schema of the annotation
        """
        # Notice that the types we return in the schema look like TypeScript / JavaScript types
        # in fact come straight from the definition of a JSON schema

        # default schema
        schema: dict[str, Any] = {"type": "string"}
        # description of the tool function
        description: str | None = None

        # gets the origin of the provided annotation
        origin = get_origin(annotation)

        # print("origin")
        # print(origin)
        # print("annotation")
        # print(annotation)

        if origin is Annotated:
            # if the origin is Annotated get the base type and call again the method on the base type
            base_type, *meta = get_args(annotation)
            schema = Tools._annotation_to_schema(base_type)
            if meta:
                description = str(meta[0])
        elif annotation is int:
            schema = {"type": "integer"}
        elif annotation is float:
            schema = {"type": "number"}
        elif annotation is bool:
            schema = {"type": "boolean"}
        elif annotation is str:
            schema = {"type": "string"}
        elif annotation is dict:
            schema = {"type": "object"}
        elif annotation is list:
            schema = {"type": "array"}
        elif annotation is NoneType:
            schema = {"type": "null"}
        # from now on we check the origins
        elif origin is list:
            schema = {
                "type": "array",
                "items": Tools._annotation_to_schema(get_args(annotation)[0]),
            }
        elif origin is dict:
            schema = {"type": "object"}
        # if the origin is a Union get the first type
        elif origin is Union:
            any_of = [
                Tools._annotation_to_schema(arg)
                for arg in get_args(annotation)
                # if arg is not type(None)
            ]
            if any_of:
                schema = {"any_of": any_of}

        # if there is a description we will add it to the schema
        if description:
            schema["description"] = description

        return schema

    @classmethod
    def schema_for_callable(cls, func: Callable[..., Any]) -> dict[str, Any]:
        """Inspects a function and returns the schema in the format that LLM likes for a tool

        :param cls: - the class
        :param func: Callable[..., Any] - a function with an arbitrary number of parameters of any type
        :return: dict[str, Any] - the schema of the provided function tool
        """
        sig = inspect.signature(func)
        annotations = inspect.get_annotations(func)

        parameters: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
            "default": "",
            "additionalProperties": False,
        }
        # print("function name:" + func.__name__)
        for name, param in sig.parameters.items():
            annotation = annotations.get(name, inspect.Parameter.empty)
            # print("parameter name:" + name)
            # print(param)
            if annotation is inspect.Parameter.empty:
                # could be an error to be raised
                continue

            parameters["properties"][name] = cls._annotation_to_schema(annotation)

            # if there is no default value associated to this parameter it means that it is required
            if param.default is param.empty:
                parameters["required"].append(name)
            elif param.default is None:
                parameters["default"] = "null"
                parameters.pop("required")
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided",
                "parameters": parameters,
                "strict": True,
            },
        }

    def get_schemas(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for fn in self.tools.values():
            s = getattr(fn, self.TOOL_SCHEMA_ATTR, None)
            if s is not None:
                out.append(s)
        return out

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """decorator to register a tool

        :param func: Callable[..., Any] - the function we want to become a tool
        :return: the original function
        """
        if getattr(func, self.TOOL_SCHEMA_ATTR, None) is None:
            setattr(func, self.TOOL_SCHEMA_ATTR, self.schema_for_callable(func))
        self.tools[func.__name__] = func
        return func

    def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """function to run the tool the LLM chose

        :param tool_call: dict[str, Any] - the info about what tool we need to call and with which parameters
        :return: the result of the tool call in a format that LLM can use to give a response
        """
        fn_payload = tool_call.get("function") or {}
        fn_name = fn_payload.get("name")
        fn = self.tools.get(fn_name) if fn_name else None

        if not fn:
            return {"error": f"Tool '{fn_name}' not found"}

        try:
            args = json.loads(fn_payload.get("arguments") or "{}")
            # check if an argument has been called with 'None'
            for k, v in args.items():
                if v == "None":
                    args[k] = None
            print(f">> Invoking function {fn_name} with arguments {args} <<")
            result = fn(**args)
            return result if isinstance(result, dict) else {"result": result}
            # add a proper logger here
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"error": str(e)}
