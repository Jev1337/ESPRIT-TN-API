# ESPRIT-TN Python API

This is the Python API for the ESPRIT-TN website. It is used to interact with the ESPRIT-TN Website.

## Installation

~~To install the API, you can use pip~~

(Currently working on a PyPI package)

To install, you have to place the file `esprit_tn.py` inside of your project. Make sure to install the requirements inside requirements.txt!

## Usage

To use the API, you need to import the `esprit` class from the `esprit_tn` module:

```python
from esprit_tn import esprit
```

Then, you can create an instance of the `esprit` class:

```python
instance = esprit(username,password)
```

You can then use the instance to interact with the ESPRIT-TN website.

## Examples

Here is an example of how to use the API:

```python
from esprit_tn import esprit

instance = esprit("username","password")

# Get the page's HTML content
response = instance.getSess().get("https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx")

# Print the response
print(response.text)
```

There is an example also of getting the grades of the student in `marks_example.py` file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


