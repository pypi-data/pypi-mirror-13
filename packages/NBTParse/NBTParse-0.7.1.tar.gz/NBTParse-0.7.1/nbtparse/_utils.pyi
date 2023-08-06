import typing as ty


def Sentinel(module_name: str, object_name: str, docstring: str) -> object:
    ...


exports = ...  # type: ty.MutableMapping[str, ty.Dict[str, object]]
