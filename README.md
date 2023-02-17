# keepass-env
Read key-value pairs from `.kdbx` file and set them as environment variables or return as dict. `.kdbx` entries can store key-value attributes. This tool takes a path to entry and loads it's attributes.

## install
```
pip install keepass-env
```

## usage
```py
import keepass_env

db_filename = 'my_database.kdbx'
password = 'secure-af'
entry_path = ['group0', 'subgroup1', 'my_entry']

# load to os.environ
keepass_env.load_env(db_filename, entry_path, password=password)

# return as dict
keepass_env.env_values(db_filename, entry_path, password=password)
{'key-0': 'value-0', 'key-1': 'value-1'}

# write env
keepass_env.write_env(db_filename, entry_path, password=password, env={
    'my-key-0': 'my-value-0',
    'my-key-1': 'my-value-1',
})
```

## entry references
This tool supports entry references. For example some entry have following key-value attributes:

```
key-0 value-0
key-1 ref@group5/entry42:API_TOKEN
```

Value for `key-1` will be loaded from another entry with path `['group5', 'entry42']` and will be taken from its attribute `API_TOKEN`.

- Format of references is prefix `ref@`, path separator `/` attribute separator `:`.
- Multiple references are supported. (If referenced value is also reference and so on, it will be looked up recursively)
- You can also reference to title, username, password, url of an entry with using following format:
    - `ref@group5/entry42:__title__`
    - `ref@group5/entry42:__username__`
    - `ref@group5/entry42:__password__`
    - `ref@group5/entry42:__url__`
- username, password, url can also be a refernces. title can't be a reference
