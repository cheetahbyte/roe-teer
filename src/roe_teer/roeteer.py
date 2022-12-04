from .n import Node, Param, Result
from typing import TypeVar, List, Tuple

T = TypeVar('T')

class Roeteer:
    def __init__(self) -> None:
        self._radix: Dict[str, Node[T]] = {}

    def _get_radix(self, method: str) -> Node[T]:
        if method not in self._radix:
            self._radix[method] = Node[T]()
        return self._radix[method]


    def use(self, path: str, handler: T) -> None:
        if '*' in path:
            raise Exception("Catch all wildcard not allowed in middleware")
        self._get_radix("middleware").insert(path, handler)

    def get(self, path: str, *arg: List[T]) -> None:
        self._get_radix("get").insert(path, *arg)

    def post(self, path: str, *arg: List[T]) -> None:
        self._get_radix("post").insert(path, *arg)

    def head(self, path: str, *arg: List[T]) -> None:
        self._get_radix("head").insert(path, *arg)

    def put(self, path: str, *arg: List[T]) -> None:
        self._get_radix("put").insert(path, *arg)

    def delete(self, path: str, *arg: List[T]) -> None:
        self._get_radix("delete").insert(path, *arg)

    def connect(self, path: str, *arg: List[T]) -> None:
        self._get_radix("connect").insert(path, *arg)

    def options(self, path: str, *arg: List[T]) -> None:
        self._get_radix("options").insert(path, *arg)

    def trace(self, path: str, *arg: List[T]) -> None:
        self._get_radix("trace").insert(path, *arg)

    def patch(self, path: str, *arg: List[T]) -> None:
        self._get_radix("patch").insert(path, *arg)

    def resolve(self, method: str, path: str) -> List[Tuple[T, Param]]:
        handlers = []
        results = self._get_radix("middleware").lookup(path, stacked=True)
        if results:
            for result in results:
                for handler in result.handler:
                    handlers.append((handler, result.params))
        result = self._get_radix(method).lookup(path)
        if result:
            for handler in result.handler:
                handlers.append((handler, result.params))
        return handlers
