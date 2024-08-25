## Additional Technical Description

### 1. GUI Functionality

The graphical user interface (GUI) for the podcast pipeline is implemented using the `tkinter` library and includes the following components:
- **Main GUI**: Found in `podcasts_GUI.py`, it provides a user-friendly interface to control the different stages of the pipeline.
  - **Tabs for Actions, Queries, and Cleaning Scripts**: The interface allows users to select specific actions, perform queries on the metadata, and run cleaning scripts.
  - **Query Integration**: Queries like finding a podcast title (`query_find_title.py`) or identifying potentially ceased podcasts (`query_possibly_ceased.py`) can be triggered directly from the GUI. The results are displayed within the GUI, making it easy for users to interact with the database.
  - **Cleaning Options**: The GUI provides a straightforward method to execute cleaning scripts, ensuring that the dataset and files are maintained properly.

### 2. Query Modules

Several query scripts are part of the pipeline, allowing specific searches and actions:
- **`query_find_title.py`**: Searches for podcast titles within the database.
- **`query_possibly_ceased.py`**: Identifies podcasts that may have stopped publishing episodes.
- **`query_delete_episode_by_id.py`**: Deletes episodes from the database by their unique ID.
- **`query_read_db_to_csv.py`**: Exports the database records to a CSV format for external analysis or archiving purposes.

These queries interact with the database handler, providing flexibility for cataloguers and system administrators to manage the podcast collection effectively.

### 3. Cleaning Scripts

- **`podcasts_cleaning_scripts.py`**: This script handles the cleaning of podcast data, files, and metadata. It removes outdated or incomplete records from the database and filesystem. The cleaning functions are automated but can be triggered from the GUI, allowing users to ensure that no unnecessary files or data are stored.

Cleaning workflow:
![draft](documents/podcasts_cleaning_scheme.jpg)
![final](documents/podcasts_cleaning.jpg)

