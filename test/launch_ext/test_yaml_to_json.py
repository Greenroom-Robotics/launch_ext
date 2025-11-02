from launch import LaunchContext
from launch.substitutions import TextSubstitution
from launch_ext.substitutions import YamlToJson


def test_yaml_to_json_quoted():
    lc = LaunchContext()

    # Create a TextSubstitution that contains YAML content
    yaml_content = """
name: test
values:
  - item1
  - item2
config:
  enabled: true
  count: 42
"""

    yaml_substitution = TextSubstitution(text=yaml_content)
    yaml_to_json_sub = YamlToJson(yaml_substitution, quote_output=True)

    result = yaml_to_json_sub.perform(lc)

    # The result should be a JSON string wrapped in quotes
    assert result.startswith("'")
    assert result.endswith("'")

    # Remove the wrapping quotes and parse as JSON to verify structure
    import json
    json_content = json.loads(result[1:-1])  # Remove quotes

    assert json_content['name'] == 'test'
    assert json_content['values'] == ['item1', 'item2']
    assert json_content['config']['enabled'] is True
    assert json_content['config']['count'] == 42


def test_yaml_to_json_unquoted():
    lc = LaunchContext()

    # Create a TextSubstitution that contains YAML content
    yaml_content = """
name: test
values:
  - item1
  - item2
config:
  enabled: true
  count: 42
"""

    yaml_substitution = TextSubstitution(text=yaml_content)
    yaml_to_json_sub = YamlToJson(yaml_substitution, quote_output=False)

    result = yaml_to_json_sub.perform(lc)

    # The result should be raw JSON without quotes
    assert not result.startswith("'")
    assert not result.endswith("'")

    # Parse as JSON to verify structure
    import json
    json_content = json.loads(result)

    assert json_content['name'] == 'test'
    assert json_content['values'] == ['item1', 'item2']
    assert json_content['config']['enabled'] is True
    assert json_content['config']['count'] == 42


def test_yaml_to_json_default_quoted():
    """Test that the default behavior is to quote the output."""
    lc = LaunchContext()
    yaml_content = "name: test"
    yaml_substitution = TextSubstitution(text=yaml_content)
    yaml_to_json_sub = YamlToJson(yaml_substitution)  # No quote_output specified

    result = yaml_to_json_sub.perform(lc)
    assert result.startswith("'")
    assert result.endswith("'")


def test_yaml_to_json_describe():
    yaml_substitution = TextSubstitution(text="test: value")
    yaml_to_json_sub = YamlToJson(yaml_substitution)

    description = yaml_to_json_sub.describe()
    assert "YamlToJson" in description
    assert "TextSubstitution" in description
    assert "quote_output=True" in description


def test_yaml_to_json_invalid_yaml():
    lc = LaunchContext()

    # Create a substitution with invalid YAML
    invalid_yaml = "invalid: yaml: content: :"
    yaml_substitution = TextSubstitution(text=invalid_yaml)
    yaml_to_json_sub = YamlToJson(yaml_substitution)

    try:
        yaml_to_json_sub.perform(lc)
        assert False, "Expected ValueError for invalid YAML"
    except ValueError as e:
        assert "Failed to parse YAML content" in str(e)