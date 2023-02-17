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
{'KEY_0': 'value-0', 'KEY_1': 'value-1'}

# write env
keepass_env.write_env(db_filename, entry_path, password=password, env={
    'MY_KEY_0': 'my-value-0',
    'MY_KEY_1': 'my-value-1',
})
```

## entry references
This tool supports entry references. For example some entry have following key-value attributes:

```
KEY_0 value-0
KEY_1 ref@group5/entry42:API_TOKEN
```

Value for `KEY_1` will be loaded from another entry with path `['group5', 'entry42']` and will be taken from its attribute `API_TOKEN`.

- Format of references is prefix `ref@`, path separator `/` attribute separator `:`.
- Multiple references are supported. (If referenced value is also reference and so on, it will be looked up recursively)
- You can also reference to title, username, password, url of an entry with using following format:
    - `ref@group5/entry42:__title__`
    - `ref@group5/entry42:__username__`
    - `ref@group5/entry42:__password__`
    - `ref@group5/entry42:__url__`
- username, password, url can also be a refernces. title can't be a reference

## print to stdout
This package comes with console script `keepass-env` (It will be accessible after pip installation).

```shell
keepass-env --db mydb.kdbx --password secure-af --entry-path group0/subgroup1/my_entry
KEY_0=value-0
KEY_1=value-1

# --export argument to print in shell format:
keepass-env --db mydb.kdbx --password secure-af --entry-path group0/subgroup1/my_entry --export
export KEY_0=value-0
export KEY_1=value-1

# configuration via env variables are also available:
KEEPASS_DB=mydb.kdbx KEEPASS_PASSWORD=secure-af KEEPASS_ENTRY_PATH=group0/subgroup1/my_entry KEEPASS_EXPORT=1
export KEY_0=value-0
export KEY_1=value-1
```

If you do not specify `--password` argument or `KEEPASS_PASSWORD` variable, you will be asked to enter a password in the command line.


Printing variables can be used to load them before running some command in the shell:

```shell
eval "$(keepass-env --db my.kdbx --password 1234 --entry-path main/project-x)" python main.py
```

Or you can put in Makefile like this:
```Makefile
.PHONY: run
run:
	eval "$$(keepass-env --db my.kdbx --password 1234 --entry-path main/project-x)" python main.py

# another example:

.PHONY: run_fastapi_app
run_fastapi_app:
	eval "$$(keepass-env --db my.kdbx --password 1234 --export --entry-path main/project-x)"; \
	uvicorn server:app
```
