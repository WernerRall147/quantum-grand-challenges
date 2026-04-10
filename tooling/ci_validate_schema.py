"""Validate JSON result schema in CI."""
import json
import jsonschema

with open("tooling/schema/result.json") as f:
    schema = json.load(f)

jsonschema.Draft7Validator.check_schema(schema)
print("Result schema is valid")

sample_result = {
    "problem_id": "01_test",
    "algorithm": "QAE",
    "instance": {"description": "Test instance", "parameters": {}},
    "estimator_target": "surface_code_generic_v1",
    "metrics": {"logical_qubits": 10},
    "build": {
        "commit": "0123456789abcdef0123456789abcdef01234567",
        "date_utc": "2025-01-01T00:00:00Z",
    },
}

jsonschema.validate(sample_result, schema)
print("Sample result validates against schema")
