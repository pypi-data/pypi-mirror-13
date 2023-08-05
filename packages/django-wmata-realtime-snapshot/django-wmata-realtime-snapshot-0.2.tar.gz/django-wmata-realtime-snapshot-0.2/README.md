# WMATA Realtime Snapshot

### Overview

Provide a point-in-time mirror of Washington DC Metro's realtime train schedule

### Installation

1. **Install the package**

    ```shell
    pip install django-wmata-realtime-snapshot
    ```

1. **Add the app to your django project's settings**

    ```python
    INSTALLED_APPS = (
        ...
        wmata_realtime_snapshot,
    )
    ```

1. **Get a WMATA API key**

    If you don't already have a WMATA API account, sign up here: https://developer.wmata.com/signup

    Alternatively, you may have success using the demo key provided here: https://developer.wmata.com/Products

    Once you have a key, (e.g. `1234IAMAKEY`), you can use it to download a dump of the realtime data.

1. **Download a JSON and/or XML dump from WMATA**

    These instructions are for a UNIX based system.

    JSON Dump:
    ```shell
    curl https://api.wmata.com/StationPrediction.svc/json/GetPrediction/All?api_key=1234IAMAKEY > realtime_dump.json
    ```

    XML Dump:
    ```shell
    curl https://api.wmata.com/StationPrediction.svc/GetPrediction/All?api_key=1234IAMAKEY > realtime_dump.xml
    ```

    To download both at the same time:

    ```shell
    curl https://api.wmata.com/StationPrediction.svc/json/GetPrediction/All?api_key=1234IAMAKEY > realtime_dump.json & curl https://api.wmata.com/StationPrediction.svc/GetPrediction/All?api_key=1234IAMAKEY > realtime_dump.xml
    ```

1. **Add your dumps to the Django settings file**

    In your Django settings, define the following variables for the dumps you want to serve.

    ```
    WMATA_JSON_DUMP='path/to/realtime_dump.json'
    WMATA_XML_DUMP='path/to/realtime_dump.xml'
    ```

    Any endpoint type (json or xml) that does not have a dump file to read will return a json/xml error message when querying the snapshot API:

    ```json
    {"Error": "No JSON resource has been defined. Please read the installation instructions."}
    ```

    ```xml
    <Error>No XML resource has been defined. Please read the installation instructions.</Error>
    ```

1. **Add a url endpoint**

    ```python
    url(r'^mirror/', include('wmata_realtime_snapshot.urls', namespace='wmata_realtime_snapshot')),
    ```

1. **Visit the API**

    The API path is the same as the real WMATA API for easy plug-n-play:

    ```
    http://localhost:8000/mirror/StationPrediction.svc/json/GetPrediction/All
    http://localhost:8000/mirror/StationPrediction.svc/GetPrediction/B01
    http://localhost:8000/mirror/StationPrediction.svc/json/GetPrediction/K08,D13,A05
    ```

