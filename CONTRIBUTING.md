## Contributing In General

To contribute code or documentation, please submit a [pull request](https://github.com/IBM/ei-geospatial-qgis-plugin/pulls).


### Setting up your development environment

To obtain all required Python modules, simply run:
```Bash
pip install -r requirements.txt
pip install -r requirements-development.txt
```
from the base of this repo.


### Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/IBM/ei-geospatial-qgis-plugin/issues) before sending a pull request so the feature can be discussed.


### Fixing bugs

If you would like to fix a bug, please [raise an issue](https://github.com/IBM/ei-geospatial-qgis-plugin/issues)before sending a pull request so it can be tracked.


### Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code review to indicate acceptance. A change requires LGTMs from one of the maintainers of each component affected.

For a list of the maintainers, see the [MAINTAINERS.md](MAINTAINERS.md) page.


## Legal

Each source file must include a license header for the [GPL-2.0-or-later](https://spdx.org/licenses/GPL-2.0-or-later.html)
Software License. Using the SPDX format is the simplest approach.
e.g.

```Python
# Copyright <years> <holder> All Rights Reserved.
#
# SPDX-License-Identifier: GPL-2.0-or-later
```

We have tried to make it as easy as possible to make contributions. This applies to how we handle the legal aspects of contribution. We use the same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://github.com/hyperledger/fabric/blob/master/docs/source/DCO1.1.txt) - that the Linux® Kernel [community](https://elinux.org/Developer_Certificate_Of_Origin) uses to manage code contributions.

We simply assert that when submitting a patch for review, the developer must include a sign-off statement in the commit message.

Here is an example Signed-off-by line, which indicates that the submitter accepts
the DCO linked above:
```
Signed-off-by: Your Name <your@mail.org>
```

You can include this automatically when you commit a change to your local git repository using the following command:
```Bash
git commit -s
```
Alternatively/in addition you can have a template for your commit text in a file like `git-commit-template` with the DCO above. Then run `git config commit.template git-commit-template` to have it as your default when running `git commit ...`.


## Testing

We ask and expect you to write test cases for the contribution you make, because it significantly helps to detect bugs while the project grows. Please place corresponding code into the `tests` directory. Please make pull requests after your contribution has passed all tests, only.

Please make sure
```Bash
pytest
```


## Coding style guidelines

Please follow [PEP8](https://peps.python.org/pep-0008/) and check compliance with the flake8 linter.

When writing code please adopt the following coding style guidelines:
- Try to well document your code, ideally with an approximate ratio 1:3 of documentation to code.
- Each function (of a class etc.) should have sufficient documentation on input, output, exceptions
and how it processes information. The goal is to have all documentation required for
the API in code such that [Sphinx](https://documentation-style-guide-sphinx.readthedocs.io/en/latest/style-guide.html)
can automatically generate documentation. An example:
```Python
def numbers_2_string(numbers):
"""
This is a one-liner summarising the function.

And here comes more details.

:param numbers:       list of random numbers to convert to string
:type numbers:        [float]
:returns:             the user given numbers, concatenated by space
:rtype:               str
:raises Exception:    if given input cannot be interpreted
if the input is not an iterable
"""
