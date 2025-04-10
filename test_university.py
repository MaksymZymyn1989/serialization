import unittest
import json
import os
import csv
from tempfile import NamedTemporaryFile

from university import (
    validate_json,
    student_schema,
    department_schema,
    user_with_department,
    InvalidInstanceError,
    DepartmentName
)

class TestValidateJson(unittest.TestCase):
    def test_valid_student_schema(self):
        valid_data = [
            {"id": 1, "name": "John Doe", "department_id": 101},
            {"name": "Jane Smith", "department_id": 102}
        ]
        self.assertTrue(validate_json(valid_data, student_schema))

    def test_invalid_student_schema(self):
        without_dep_id = [
            {"id": 1, "name": "John Doe"}
        ]
        self.assertFalse(validate_json(without_dep_id, student_schema))

        # Wrong type for 'department_id'
        wrong_type_dep_id = [
            {"id": 1, "name": "John Doe", "department_id": "101"}
        ]
        self.assertFalse(validate_json(wrong_type_dep_id, student_schema))

    def test_valid_department_schema(self):
        valid_data = [
            {"id": 101, "name": "Computer Science"},
            {"id": 102, "name": "Mathematics"}
        ]
        self.assertTrue(validate_json(valid_data, department_schema))

    def test_invalid_department_schema(self):
        without_id = [
            {"name": "Computer Science"}
        ]
        self.assertFalse(validate_json(without_id, department_schema))

        wrong_type_id= [
            {"id": "101", "name": "Computer Science"}
        ]
        self.assertFalse(validate_json(wrong_type_id, department_schema))


class TestUserWithDepartment(unittest.TestCase):
    def setUp(self):
        self.valid_users = [
            {"id": 1, "name": "John Doe", "department_id": 101},
            {"id": 2, "name": "Jane Smith", "department_id": 102}
        ]

        self.valid_departments = [
            {"id": 101, "name": "Computer Science"},
            {"id": 102, "name": "Mathematics"}
        ]

        self.expected_output = [
            {"name": "John Doe", "department": "Computer Science"},
            {"name": "Jane Smith", "department": "Mathematics"}
        ]

    def create_temp_file(self, content):
        temp_file = NamedTemporaryFile(delete=False, mode='w')
        temp_file.write(json.dumps(content))
        temp_file.close()
        return temp_file.name

    def test_successful_execution(self):
        user_file = self.create_temp_file(self.valid_users)
        dept_file = self.create_temp_file(self.valid_departments)

        output_file = "test_output.csv"

        try:
            user_with_department(output_file, user_file, dept_file)

            with open(output_file, 'r') as f:
                reader = csv.DictReader(f)
                result = list(reader)

                self.assertEqual(len(result), len(self.expected_output))
                for i, row in enumerate(result):
                    self.assertEqual(row["name"], self.expected_output[i]["name"])
                    self.assertEqual(row["department"], self.expected_output[i]["department"])
        finally:
            os.unlink(user_file)
            os.unlink(dept_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_invalid_user_schema(self):
        without_name = [{"id": 1, "department_id": 101}]  
        user_file = self.create_temp_file(without_name)
        dept_file = self.create_temp_file(self.valid_departments)

        try:
            with self.assertRaises(InvalidInstanceError):
                user_with_department("output.csv", user_file, dept_file)
        finally:
            os.unlink(user_file)
            os.unlink(dept_file)

    def test_invalid_department_schema(self):
        without_id = [{"name": "Computer Science"}] 
        user_file = self.create_temp_file(self.valid_users)
        dept_file = self.create_temp_file(without_id)

        try:
            with self.assertRaises(InvalidInstanceError):
                user_with_department("output.csv", user_file, dept_file)
        finally:
            os.unlink(user_file)
            os.unlink(dept_file)

    def test_missing_department_id(self):
        nonexistent_dep_id = [
            {"id": 1, "name": "John Doe", "department_id": 999}  
        ]

        user_file = self.create_temp_file(nonexistent_dep_id)
        dept_file = self.create_temp_file(self.valid_departments)

        try:
            with self.assertRaises(DepartmentName):
                user_with_department("output.csv", user_file, dept_file)
        finally:
            os.unlink(user_file)
            os.unlink(dept_file)

    def test_empty_user_list(self):
        user_file = self.create_temp_file([])
        dept_file = self.create_temp_file(self.valid_departments)
        output_file = "test_empty.csv"

        try:
            user_with_department(output_file, user_file, dept_file)

            with open(output_file, 'r') as f:
                content = f.read().strip()
                self.assertEqual(content, "name,department")
        finally:
            os.unlink(user_file)
            os.unlink(dept_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            user_with_department("output.csv", "non_existent_user.json", "non_existent_dept.json")


if __name__ == '__main__':
    unittest.main()
