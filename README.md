# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/lazy-kafka/lazy-kafka/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                          |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/lazy\_kafka/\_\_init\_\_.py                               |        6 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/\_\_main\_\_.py                               |       92 |       11 |        6 |        1 |     88% |53, 56, 88, 91-92, 122-124, 155-156, 170-171 |
| src/lazy\_kafka/\_logging.py                                  |       14 |       14 |        0 |        0 |      0% |      3-30 |
| src/lazy\_kafka/\_types.py                                    |       10 |       10 |        4 |        0 |      0% |      1-16 |
| src/lazy\_kafka/cli/\_\_init\_\_.py                           |        3 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/cli/\_cli.py                                  |       35 |        2 |       10 |        2 |     91% |    39, 79 |
| src/lazy\_kafka/config.py                                     |       96 |        6 |       16 |        3 |     92% |78-79, 111-115, 119-123 |
| src/lazy\_kafka/connect.py                                    |      106 |        8 |        2 |        0 |     93% |108-109, 154-155, 217-221 |
| src/lazy\_kafka/entry\_points.py                              |        4 |        1 |        0 |        0 |     75% |         7 |
| src/lazy\_kafka/plugin/\_\_init\_\_.py                        |       33 |        2 |        4 |        0 |     95% |    57, 61 |
| src/lazy\_kafka/plugins/\_\_init\_\_.py                       |        3 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/plugins/core\_kafka/\_\_init\_\_.py           |       27 |        3 |        0 |        0 |     89% | 32-33, 37 |
| src/lazy\_kafka/plugins/core\_kafka/cli.py                    |       80 |       55 |        8 |        0 |     28% |38-58, 84-103, 129-130, 134-203 |
| src/lazy\_kafka/plugins/kafka\_connect/\_\_init\_\_.py        |       23 |        3 |        0 |        0 |     87% |     32-34 |
| src/lazy\_kafka/plugins/schema\_registry/\_\_init\_\_.py      |       23 |        3 |        0 |        0 |     87% |     30-32 |
| src/lazy\_kafka/plugins/schema\_registry/cli.py               |       23 |        7 |        0 |        0 |     70% |     60-73 |
| src/lazy\_kafka/registry.py                                   |       99 |       16 |       12 |        2 |     80% |45, 60-64, 68-\>75, 123, 143-144, 188-207 |
| src/lazy\_kafka/scripts/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/scripts/topic\_schema\_consumer.py            |       24 |       24 |        4 |        0 |      0% |      1-56 |
| src/lazy\_kafka/scripts/topic\_schema\_consumer\_ex.py        |       31 |       31 |        4 |        0 |      0% |      1-98 |
| src/lazy\_kafka/scripts/topic\_schema\_consumer\_generator.py |       32 |       32 |        6 |        0 |      0% |      1-65 |
| src/lazy\_kafka/scripts/topic\_schema\_consumer\_n\_times.py  |       64 |       64 |       16 |        0 |      0% |     1-127 |
| src/lazy\_kafka/scripts/topic\_schema\_producer.py            |       48 |       48 |        2 |        0 |      0% |     1-140 |
| src/lazy\_kafka/theme.py                                      |        4 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/topic.py                                      |      234 |      107 |       40 |        1 |     50% |158-160, 163-165, 211, 248-250, 268-285, 298-315, 330-397, 411-425, 436-453 |
| src/lazy\_kafka/utils.py                                      |       26 |        0 |        8 |        0 |    100% |           |
| src/lazy\_kafka/widgets/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/widgets/\_logs.py                             |      181 |       20 |       38 |       11 |     83% |109, 117-120, 202-\>205, 215-\>217, 224, 239, 243-\>exit, 276, 323, 325-\>exit, 330-336, 340-341, 345-346, 350-\>exit, 355-\>exit, 365-\>368, 383, 413-\>exit |
| src/lazy\_kafka/widgets/\_status.py                           |       10 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/widgets/common.py                             |      159 |       67 |       22 |        4 |     54% |33-\>exit, 193-194, 197-200, 203-206, 209-212, 215-228, 231-233, 239-240, 251, 256, 259-260, 264-276, 286-290, 307-338, 341-\>exit, 344-\>exit |
| src/lazy\_kafka/widgets/kconnect.py                           |       46 |       11 |        4 |        0 |     70% |34-47, 51, 90, 96-103 |
| src/lazy\_kafka/widgets/registry.py                           |      143 |       62 |       16 |        0 |     53% |38-41, 45, 101-104, 111-120, 134-152, 167-169, 177-179, 183-189, 192, 204-205, 225-231, 235-238, 242-247, 251-258, 279, 284 |
| src/lazy\_kafka/widgets/switcher.py                           |       46 |       19 |       12 |        0 |     50% |101-108, 123-139 |
| src/lazy\_kafka/widgets/topic.py                              |       37 |       14 |        0 |        0 |     62% |43-44, 47-51, 54-55, 58-60, 63, 68 |
| src/lazy\_kafka/widgets/topic\_details.py                     |       86 |       22 |        4 |        0 |     71% |110-132, 142-144, 153-154 |
| tests/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                             |       88 |       27 |        0 |        0 |     69% |21, 31, 37, 43, 96-99, 116-122, 129-133, 139-140, 155-159 |
| tests/integration/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| tests/integration/test\_tui.py                                |      163 |        0 |        6 |        0 |    100% |           |
| tests/test\_cli.py                                            |       71 |        0 |        0 |        0 |    100% |           |
| tests/test\_config.py                                         |      135 |        0 |        0 |        0 |    100% |           |
| tests/test\_connect.py                                        |      168 |        0 |        0 |        0 |    100% |           |
| tests/test\_plugin.py                                         |      100 |       13 |        8 |        3 |     85% |55, 58, 74, 77, 106, 109, 134-137, 158, 167-169, 177-179 |
| tests/test\_registry.py                                       |      149 |        0 |        0 |        0 |    100% |           |
| tests/test\_topic.py                                          |      193 |        1 |        0 |        0 |     99% |       309 |
| tests/test\_utils.py                                          |       58 |        0 |        0 |        0 |    100% |           |
| tests/test\_widgets.py                                        |       70 |        0 |        0 |        0 |    100% |           |
| **TOTAL**                                                     | **3043** |  **703** |  **252** |   **27** | **74%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/lazy-kafka/lazy-kafka/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/lazy-kafka/lazy-kafka/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lazy-kafka/lazy-kafka/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/lazy-kafka/lazy-kafka/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Flazy-kafka%2Flazy-kafka%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/lazy-kafka/lazy-kafka/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.