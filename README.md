
# Python FastAPI App to store user settings

A simple application to read, write and delete user settings via an API

## Getting Started

To run the app in a virtual environment, create a new venv:
1. From the root project directory, run `python -m venv ./.venv`
1. Run `source .venv/bin/activate` (bash/zsh) See [venv docs](https://docs.python.org/3/library/venv.html) for other environments
1. Run `pip install -r ./requirements.txt`
1. Run `uvicorn main:app` to start app (use `--reload` flag for dev)

## API Documentation

When the app is running, generated docs are available:
http://localhost:8000/docs

## Tech stack

- Built and tested on *nix environments
- Python 3.11.5 with venv
- FastAPI framework, utilizing async functions with uvicorn server

## Configuration

- In `./storage/base_storage.py`, the `FILE_STORAGE_SETTINGS_DIR` constant can be updated to store user settings in any chosen directory. Note that Python must have write access to the directory, or a PermissionError will be raised.

## Additions and Notes

- Limiting request size. For a hardened production deployment I would almost always use an nginx or Apache web server with a reverse proxy in front of the Python ASGI server (uvicorn in this case). For nginx, I would set `client_max_body_size` which would be the most efficient method of stopping oversized requests. I do not have experience with FastAPI, but short of manually streaming a request and checking the content size ([suggested per this comment](https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025)), it does not appear it supports limiting request size. If a request is too large (not sure what the internal limits are), on testing FastAPI does return a 422 Unprocessable Entity. Otherwise the application is configured with Pydantic validation so it will never attempt to store inputs larger than 100 characters and has a max username size as well (all configurable via constants). So worst case scenario in the current implementation is a malicious payload could theoretically crash the server which would wipe out all stored user settings.
- Skipped the use of Pydantic models because the only input is a single string, so directly validating the body length on the PUT endpoint.
- In-memory caching layer to reduce disk reads (naive implementation)
- BaseStorage abstract class for storage. Can be subclassed with any storage implementation. Defaults to the FileStorage class.
- For storing multiple user settings in the future, applications would have multiple options:
  1. Store a JSON string or any hashed string
  1. Create a new user key for each specific setting, ie `'{user_id}_key_name'`
  This implementation assures compatibility with any key/value store where the key and value must be strings, creating solid backward and forward compatability. It also allows multiple applications to use the service, but the applications would be responsible for namespacing keys. Of course these assumptions could always be revisited, but this is where I would start.

## Future Features
- Move `FILE_STORAGE_SETTINGS_DIR` from a constant to an environment variable
- Possibly a persistent data layer or filesystem backups. If the underlying server or VM goes down, the data is gone. I would likely choose redis
- Authentication, or ensuring app is only accessible to folks on the intranet
- Formalize and validate implementations of the BaseStorage abstract class
- Tests!
- Clean up generated API docs to ensure they're completely accurate and include examples

## Original Problem Statement

### Overview
    We currently have a client-side web application that stores user settings in the browser localStorage. The system team is implementing a policy that will wipe all browser cache (images, CSS, cookies, site data, etc.) every time the browser is closed to overcome some other organizational issues.
 
    The user setting amounts to a single value associated with their user ID.
 
    We need a way to store the users' setting value outside of the browser. We want to prototype a solution using Python and FastAPI, and simple files to store the data.
    User settings will be stored in a directory called user-settings. The location of the directory should be configurable either by a configuration file in the web application or by an easily accessible constant.
 
    The files should be simply named with the user ID. For example, if the user ID is bob123 then it will be stored in /opt/user-settings/bob123, assuming that we configured the user-settings folder to be on the /opt partition.
 
    The files only contain a single unicode text up to 100 characters in length.
 
    The data is not sensitive so no user access security is required. Even if Alice were to make the request "GET /bob123" and see Bob's stored setting of "abc1234" it has no negative implications. However, our cybersecurity team does run internal penetration tests and the application may get requests with large amounts of garbage data in an attempt to find vulnerabilities, so please include basic request validation to avoid issues that might arise if a vulnerability test makes a PUT request with a 1GB payload.
 
    Please email web application prototype Git repository archive when finished.
 
### Endpoints
    GET request comes in to endpoint /<userid>
    The application looks for a file named <userid> in the user-settings folder.
    If it finds a user's setting file it returns the value in the file found.
 
    PUT request comes in to endpoint /<userid>
    With the body containing the new value.
    The application simply creates (overwriting existing if needed) the user-settings/<userid> file and writes the value to it.
    DELETE request comes in to endpoint /<userid>
    The application simply deletes the user-settings/<userid> file if one exists.
    This likely isn't needed, but in case we need to add a "reset" option to erase the user's value.
 
### Future Considerations
    We might want to store additional settings later, or spin up multiple instances for redundancy and load-balancing, so try to keep the read/write/delete flexible but for now we would just need a way to store a single value per user.