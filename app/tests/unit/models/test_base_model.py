from datetime import datetime
from pathlib import Path

from app.models.base import BaseModel


class ChildModel(BaseModel):
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


class ParentModel(BaseModel):
    def __init__(
        self,
        title: str,
        child: ChildModel,
        tags: list,
        metadata: dict,
        created_at: datetime,
        file_path: Path,
    ):
        self.title = title
        self.child = child
        self.tags = tags
        self.metadata = metadata
        self.created_at = created_at
        self.file_path = file_path
        self._private_field = "hidden_value"


def test_basemodel_serialization():
    now = datetime(2026, 7, 29, 12, 0, 0)
    path = Path("/home/majid/project")
    child = ChildModel(name="Ali", age=10)

    parent = ParentModel(
        title="Project Setup",
        child=child,
        tags=["python", "fastapi", child],
        metadata={"created_by": "Majid", "nested_path": path},
        created_at=now,
        file_path=path,
    )

    result = parent.to_dict()

    assert result["title"] == "Project Setup"
    assert "_private_field" not in result
    assert result["child"] == {"name": "Ali", "age": 10}
    assert result["tags"] == ["python", "fastapi", {"name": "Ali", "age": 10}]
    assert result["metadata"] == {
        "created_by": "Majid",
        "nested_path": "/home/majid/project",
    }
    assert result["created_at"] == "2026-07-29T12:00:00"
    assert result["file_path"] == "/home/majid/project"


def test_empty_model_serialization():

    class EmptyModel(BaseModel):
        pass

    empty = EmptyModel()
    assert empty.to_dict() == {}


def test_basemodel_serializes_tuple_as_list():
    class TupleModel(BaseModel):
        def __init__(self):
            self.values = ("python", "flask", 123)

    model = TupleModel()

    result = model.to_dict()

    assert result == {
        "values": ["python", "flask", 123],
    }


def test_basemodel_from_dict_creates_model_instance():
    class UserModel(BaseModel):
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    result = UserModel.from_dict(
        {
            "name": "Majid",
            "age": 25,
        }
    )

    assert isinstance(result, UserModel)
    assert result.name == "Majid"
    assert result.age == 25
    assert result.to_dict() == {
        "name": "Majid",
        "age": 25,
    }


def test_basemodel_nested_private_fields_are_not_serialized():
    class PrivateChild(BaseModel):
        def __init__(self):
            self.name = "child"
            self._hidden_field = "hidden"

    class Parent(BaseModel):
        def __init__(self):
            self.child = PrivateChild()

    parent = Parent()

    result = parent.to_dict()

    assert result == {
        "child": {
            "name": "child",
        }
    }
