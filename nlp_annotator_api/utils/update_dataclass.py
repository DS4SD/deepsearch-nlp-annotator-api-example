from dataclasses import Field, is_dataclass
from typing import Any, Mapping


def update_dataclass(self: Any, config: Any):
    if not is_dataclass(self):
        raise ValueError("Only dataclasses are supported.")

    for k, v in config.items():
        if k not in self.__dataclass_fields__:
            continue

        field_spec: Field = self.__dataclass_fields__[k]
        current_value = getattr(self, k)

        if issubclass(field_spec.type, Mapping):
            current_value.update(v)
        elif is_dataclass(field_spec.type):
            update_dataclass(current_value, v)
        else:
            current_value = v

        setattr(self, k, current_value)

    return self
