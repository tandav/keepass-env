# keepass-env
Read key-value pairs from `.kdbx` file and set them as environment variables or return as dict. `.kdbx` entries can store key-value attributes. This tool takes a path to entry and loads it's attributes.

## install
```
pip install keepass-env
```

## usage
```py
import keepass_env

entry_path = ['group0', 'subgroup1', 'my_entry']

# load to os.environ
keepass_env.load_env('my_database.kdbx', entry_path)

# return as dict
keepass_env.env_values('my_database.kdbx', entry_path)
{'key-0': 'value-0', 'key-1': 'value-1'}
```

## entry references
This tool supports entry references. For example some entry have following key-value attributes:

```
key-0 value-0
key-1 ref@group5/entry42:API_TOKEN
```

Value for `key-1` will be loaded from another entry with path `['group5', 'entry42']` and will be taken from its attribute `API_TOKEN`.

- Multiple references are supported.
- Default format of references is prefix `ref@`, path separator `/` attribute separator `:`. This can be configured via arguments to `load_env` and `env_values`
