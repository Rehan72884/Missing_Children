# Missing Children Backend

A Flask REST API for missing-child reports, found-child reports, adoption and
foster requests, shelter information, police workflows, and notifications. It
uses SQLAlchemy with Microsoft SQL Server and stores uploaded image paths in the
database.

## Requirements

- Python 3.10 or later
- Microsoft SQL Server
- Microsoft ODBC Driver 17 for SQL Server
- Python dependencies from `requirements.txt`

Install the Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The `face_recognition` dependency also requires its native `dlib` dependency;
installation instructions may vary by operating system and Python version.

## Database configuration

Set these environment variables before starting the API:

| Variable | Description |
| --- | --- |
| `DB_SERVER` | SQL Server host (and instance, if applicable) |
| `DB_NAME` | Database name |
| `DB_USERNAME` | SQL Server login |
| `DB_PASSWORD` | SQL Server password |

The database schema is defined in the modules under `model/`. This repository
does not include database credentials, a database dump, or uploaded images.

## Run

From the project directory, with the environment variables configured:

```powershell
python app.py
```

The Flask routes are defined in `app.py`. Uploaded images are stored under
`uploads/`, which is intentionally excluded from Git.

## Image-based face matching

**Yes, image-based face recognition is present.** The app uses the
`face_recognition` Python package to locate faces, generate face encodings, and
compare them; it does not include a separate custom-trained model weights file.

- `controller/AdoptivePersonController.py` implements `match_person` and uses
  face distance to find matching child images. It is called by the
  `/getRelevantChild` image-upload route in `app.py`.
- `controller/Person_Controller.py` also implements `match_person` using face
  encodings and face comparison.

The package's pretrained face-recognition model is supplied by the installed
dependency; there is no model file stored in this repository.
