import json
import jsonschema
from jsonschema import validate
import csv

# Схема для студентів
student_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "department_id"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "department_id": {"type": "integer"}
        },
        "additionalProperties": True
    }
}

# Схема для кафедр
department_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "additionalProperties": True
    }
}


# Власні винятки
class InvalidInstanceError(Exception):
    pass


class DepartmentName(Exception):
    pass


# Валідація JSON згідно з переданою схемою
def validate_json(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError:
        return False


# Основна функція для об'єднання користувачів з кафедрами і запису в CSV
def user_with_department(output_csv_path, users_json_path, departments_json_path):
    with open(users_json_path, 'r') as user_file:
        users = json.load(user_file)

    with open(departments_json_path, 'r') as dept_file:
        departments = json.load(dept_file)

    if not validate_json(users, student_schema):
        raise InvalidInstanceError("Invalid user JSON schema")

    if not validate_json(departments, department_schema):
        raise InvalidInstanceError("Invalid department JSON schema")

    # Побудова словника з кафедр
    dept_dict = {d["id"]: d["name"] for d in departments}

    output_rows = []
    for user in users:
        dep_id = user["department_id"]
        if dep_id not in dept_dict:
            raise DepartmentName(f"Department ID {dep_id} not found")

        output_rows.append({
            "name": user["name"],
            "department": dept_dict[dep_id]
        })

    # Запис у CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ["name", "department"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)
