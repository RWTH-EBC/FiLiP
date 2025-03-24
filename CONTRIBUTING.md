# Contribute as a user

The documentation, examples and tutorials should be understandable and the code bug-free.
As all users have different backgrounds, you may not understand everything or encounter bugs.
In that case, PLEASE raise an issue [here](https://github.com/RWTH-EBC/filip/issues/new).

Consider labeling the issue with an [appropriate label](https://github.com/RWTH-EBC/FiLiP/labels).

# Contribute as a developer

If you instead want to contribute new features or fix bugs yourself, we are more than happy.

Please [raise an issue](https://github.com/RWTH-EBC/filip/issues/new).
Issue branches are created automatically on issue assignments.

See [workflow definition](.github/workflows/issue-tracker.yml) and 
[configuration file](.github/issue-branch.yml) for customization.

Branch creation is skipped for issues with the label "question".

Once your feature is ready, create a pull request and check if the pipeline succeeds.
Assign a reviewer before merging. 
Once review is finished, you can merge.

**Before** implementing or modifying modules, classes or functions, please read the following page.

## Style guides

### Coding style guide

We use PEP8 as a coding style guide. Some IDEs (like PyCharm) automatically show you code that is not in PEP8. If you don't have such an IDE, please read [this page](https://pep8.org/) to get a better understanding of it.

### Committing style guide

For committing style guide please use Conventional Commits 1.0.0. For more details how to structure your commits please visit this [page](https://www.conventionalcommits.org/en/v1.0.0/).

### Pre-commit Hooks

In order to make the development easy and uniform, use of pre-commit is highly recommended. The pre-commit hooks run before every commit to ensure the code is compliant with the project style.

Check if pre-commit is installed:
```bash
pre-commit --version
```
Install pre-commit via pip if it's not already installed.
```bash
pip install pre-commit~=4.0.1
```
Install the git hook scripts:
```bash
pre-commit install
```
This will run pre-commit automatically on every git commit. Checkout [pre-commit-config.yaml](.pre-commit-config.yaml) file to find out which hooks are currently configured.

> **Note:** Currently we are using the pre-commit to perform black formatter. You can perform a formatting to all files by running the following command:
> ```bash
> pre-commit run black --all-files
> ```

## Documentation

All created or modified functions should be documented properly. 
Try to follow the structure already present. 
If possible, write a little doctest example into the docstring to make clear to the user what the desired output of your function is. 
All non-self-explanatory lines of code should include a comment. 
Although you will notice that not all docstring are already in this style, we use the google-style for docstrings, e.g.

```python

from typing import Union

def foo(dummy: str , dummy2: Union[str, int]):
    """
    Describe what the function does in here.
    The blank line below is necessary for the doc to render nicely.
    
    Args:
        dummy (str): Any parameter description
        dummy (str, int): A variable that may have two types.
    """
```

Furthermore, we use type annotations as this helps users to automatically 
identify wrong usage of functions. 
In a further step, type annotations may also help to accelerate your code. 
For more details please check the official [documentation on type hints](https://docs.python.org/3/library/typing.html).

## Unit-Tests
Especially when creating new functions or classes, you have to add a unit-test function.
Tests are located in the `\tests` directory. Every file that includes tests has a `test_` prefix. 
Open the appropriate module where you want to write a test and add an appropriate function.
When you are adding tests to an existing test file, it is also recommended that you study the other tests in that file; it will teach you which precautions you have to take to make your tests robust and portable.
If the corresponding module does not exist, then you should create a new module with `test_` prefix and appropriate name. 

If you are not familiar with unit-tests, here is a quick summary:
- Test as many things as possible. Even seemingly silly tests like correct input-format help prevent future problems for new users.
- Use the `self.assertSOMETHING` functions provided by `unittest`. This way a test failure is presented correctly. An error inside your test function will not be handled as a failure but as an error.
- If the success of your test depends on the used development environment, you can use decorators like `skip()`, `skipif(numpy.__version__<(1, 0), "not supported with your numpy version")`, etc. 
- `setUp()` and `tearDown()` are called before and after each test. Use these functions to define parameters used in every test, or to close applications like Dymola once a test is completed.
- See the [unittest-documentation](https://docs.python.org/3/library/unittest.html#organizing-tests) for further information.

You can check your work by running all tests before committing to git. 

## Pylint
With pylint we try to keep our code clean.  
[Here](https://pypi.org/project/pylint/) you can read more about Pylint and how to use it.
