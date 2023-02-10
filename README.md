<h1 align="center">arcadia</h1>

<div align="center">
	<img src="assets/arcadia.png" width="250" title="arcadia logo">
</div>

## About
`arcadia` is a command line and lib toolset for a data storage and organization framework with SQLite support.

## Install
This project is managed with [Python Poetry](https://github.com/python-poetry/poetry). With Poetry installed correctly, simply clone this project and install its dependencies:

- Clone repo
    ```
    git clone https://github.com/roboto84/arcadia.git
    ```
    ```
    cd arcadia
    ```
- Install dependencies
    ```
    poetry install
    ```
## Environmental Variables
- You must create a `.env` file with the following environmental variables set:
    - `SQL_LITE_DB`: Location of Arcadia SQLite DB.

- An explained `.env` file format is shown below:
    ```
    SQL_LITE_DB=<Arcadia DB Location>
    ```

- A typical `.env` file may look like this:
    ```
    SQL_LITE_DB=/home/data/arcadia.db
    ```

## Usage
- Add URL to `arcadia`
    ```
    poetry run python arcadia/main.py <url> <tags (comma separated, no spaces)>
    ```
- Search `arcadia` by tag:
    ```
    poetry run python arcadia/main.py <tag>
    ```

## Example
- Insert an article with the tags `security` & `tech`.
    ```
    poetry run python arcadia/main.py https://techcrunch.com/2023/01/10/interior-department-watchdog-passwords/ security,tech
    ```
- Insert an article with the tags `tech`, `js`, & `framework`
    ```
    poetry run python arcadia/main.py https://alpinejs.dev/ tech,js,framework
    ```
- Search by tag: `tech`
    ```
    poetry run python arcadia/main.py tech
    ```
- View `tech` search results
    ```
    🌿  Tech

    framework:
        ◦ 2023-01-13T22:08:52Z: https://alpinejs.dev/
    js:
        ◦ 2023-01-13T22:08:52Z: https://alpinejs.dev/
    security:
        ◦ 2023-01-13T22:01:12Z: https://techcrunch.com/2023/01/10/interior-department-watchdog-passwords/
    ```

## Commit Conventions
Git commits follow [Conventional Commits](https://www.conventionalcommits.org) message style as explained in detail on their website.

<br/>
<sup>
    <a href="https://www.flaticon.com/free-icons/leaf" title="leaf icons">
        arcadia icon created by Freepik - Flaticon
    </a>
</sup>
