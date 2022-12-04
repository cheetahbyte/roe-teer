from __future__ import annotations
import re
from copy import deepcopy
from typing import Generic, TypeVar, List, Dict, Tuple, Callable

def longest_common_prefix(a: str, b: str) -> int:
    i = 0
    l = min(len(a), len(b))
    while i < l and a[i] == b[i]:
        i += 1
    return i
    
T = TypeVar('T')

class Param:
    def __init__(self, value: str, type: str | None) -> None:
        self.value: str = value
        self.type: str | None = type
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Param):
            return False
        return self.value == other.value and self.type == other.type

class Result(Generic[T]):
    def __init__(self) -> None:
        self.handler: List[T] = []
        self.params: Dict[str, Param] = {}

class Node(Generic[T]):
    def __init__(self, path: str = None, handler: List[T] = None, children: Dict[str, "Node"] = None) -> None:
        self.path: str = path if path is not None else ""
        self.children: Dict[str, "Node"] = children if children is not None else {}
        self.handler: List[T] = handler if handler is not None else []
        self.paramName: str | None = None
        self.type: str | None = None
        self.regex: re.Pattern | None = None

    def lookup(self, p: str, stacked: bool = False) -> Result[T] | List[Result[T]] | None:
        stack: List[Tuple["Node"[T], bool, str, Result[T], bool]] = [(self, False, p, Result[T](), False)]

        i = 0
        while i >= 0:
            node, checked, path, result, walkedBy = stack[i]
            restPath: str = ""
            
            if checked:
                i -= 1
                continue
            else:
                stack[i] = (node, True, path, result, walkedBy)
            
            if len(node.path) > 0 and node.path[0] == "*":
                if node.paramName is None:
                    raise Exception(f"Catch all wildcard has no name in '{node.path}'")
                result.params[node.paramName] = Param(path, node.type)
                restPath = ""

                if stacked:
                    stack[i] = (node, True, path, result, True)
            elif len(node.path) > 0 and node.path[0] == ":":
                index = -1
                if node.regex is not None:
                    match = node.regex.match(path)
                    if match is None:
                        i -= 1
                        continue
                    index = match.end()
                else:
                    try:
                        index = path.index("/")
                    except:
                        index = len(path)
                restPath = path[index:]
                if node.paramName is None:
                    raise Exception(f"Catch all wildcard has no name in '{node.path}'")

                result.params[node.paramName] = Param(path[:index], node.type)

                if stacked:
                    stack[i] = (node, True, path, result, True)
            else:
                lcp = longest_common_prefix(node.path, path)
                if lcp != len(node.path):
                    i -= 1
                    continue
                else:
                    restPath = path[lcp:]

                if stacked:
                    stack[i] = (node, True, path, result, True)
            
            if restPath == "":
                if not stacked:
                    result.handler = node.handler
                    return result
                else:
                    stack = list(filter(lambda tuple: tuple[4], stack))
                    results: List[Result[T]] = []
                    for item in stack:
                        node, checked, path, result, walkedBy = item
                        if len(node.handler) <= 0:
                            continue
                        result.handler = node.handler
                        results.append(result)
                    return results
            
            if "*" in node.children:
                i += 1
                stack.insert(i, (node.children["*"], False, restPath, deepcopy(result), False))
            if ":" in node.children:
                i += 1
                stack.insert(i, (node.children[":"], False, restPath, deepcopy(result), False))
            if restPath[0] in node.children:
                i += 1
                stack.insert(i, (node.children[restPath[0]], False, restPath, deepcopy(result), False))

        if stacked:
            stack = list(filter(lambda tuple: tuple[4], stack))
            results: List[Result[T]] = []
            for item in stack:
                node, checked, path, result, walkedBy = item
                if len(node.handler) <= 0:
                    continue
                result.handler = node.handler
                results.append(result)
            return results
        return None

    def insert(self, path: str, *arg: List[T]) -> "Node":
        start = end = 0
        while end < len(path):
            if path[end] in [':', "*"]:
                self = self.merge(path[start:end])
                wildcard = path[end]
                start = end

                # Catch-all wildcard
                if wildcard == "*":
                    end = len(path)
                    p = path[start:end]
                    result = re.match(r"^\*(?P<paramName>[a-z0-9._-]*)(\|(?P<type>[a-zA-Z_]*))?$", p, flags=re.IGNORECASE)
                    if result is None:
                        raise Exception(f"Malformatted catch all wildcard '{p}': required format: *catch-all|type where catch-all name can only contain a-z, A-Z, 0-9, ., _, -")

                    if wildcard in self.children:
                        raise Exception(f"Cannot add '{p}': another catch all wildcard '{self.children[wildcard].path}' already exists")

                    child = Node(p, [], {})
                    child.paramName = result.group("paramName")
                    child.type = result.group("type")
                    self.children[wildcard] = child
                    self = child
                    start = end
                    break
                
                if wildcard == ":":
                    result = re.search(r"^(:(?P<paramName>[a-zA-Z0-9._-]+)(\((?P<regex>.*?)\))?(\|(?P<type>[a-zA-Z_]*))?)", path[start:], flags=re.IGNORECASE)
                    if result is None:
                        # Should never get thrown...
                        raise Exception(f"Malformatted parameter wildcard in '{path}': required format: :parameter-name(optional regex)|optional type/optional additional path where parameter name can container A-Z, a-z, 0-9, ., _, - and type can container A-Z, a-z, 0-9")

                    end += result.end()
                    p = path[start:end]

                    child = self.children[wildcard] if wildcard in self.children else None
                    if child is not None:
                        if child.path != p:
                            raise Exception(f"Parameter name '{p}' in '{path}' should be equal to previous provided name '{child.path}'")
                    else:
                        child = Node(p, [], {})
                        child.paramName = result.group("paramName")
                        child.type = result.group("type")
                        child.regex = re.compile(result.group("regex")) if result.group("regex") is not None else None
                        self.children[wildcard] = child
                    self = child
            else:
                end += 1
    
        if start < len(path):
            self = self.merge(path[start:])

        if len(arg) > 0:
            for handler in arg:
                if handler not in self.handler:
                    self.handler.append(handler)
            
        return self
    
    def merge(self, path: str) -> "Node":
        lcp = longest_common_prefix(path, self.path)
        
        if lcp == 0 and len(self.children) == 0:
            self.path = path
            return self
        
        if lcp < len(self.path):
            child = Node(self.path[lcp:], self.handler, self.children)
            self.path = path[:lcp]
            self.children = { child.path[0]: child }
            self.handler = []
        
        if lcp < len(path):
            if path[lcp] in self.children:
                self = self.children[path[lcp]].insert(path[lcp:])
            else:
                child = Node(path[lcp:], [], {})
                self.children[path[lcp]] = child
                self = child
        
        return self
