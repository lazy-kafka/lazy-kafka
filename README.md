# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/lazy-kafka/lazy-kafka/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                     |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/lazy\_kafka/\_\_init\_\_.py                          |        6 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/\_\_main\_\_.py                          |       98 |       11 |        6 |        1 |     88% |73, 76, 112, 115-116, 146-148, 179-180, 194-195 |
| src/lazy\_kafka/\_logging.py                             |       14 |       14 |        0 |        0 |      0% |      3-30 |
| src/lazy\_kafka/\_types.py                               |        8 |        8 |        4 |        0 |      0% |      1-13 |
| src/lazy\_kafka/cli/\_\_init\_\_.py                      |        3 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/cli/\_cli.py                             |       38 |        3 |       14 |        5 |     85% |25-\>exit, 39, 42, 80-\>83, 84 |
| src/lazy\_kafka/config.py                                |       96 |        6 |       16 |        3 |     92% |82-83, 115-119, 123-127 |
| src/lazy\_kafka/connect.py                               |      107 |        9 |        4 |        1 |     91% |86, 110-111, 160-161, 229-233 |
| src/lazy\_kafka/entry\_points.py                         |        4 |        1 |        0 |        0 |     75% |         7 |
| src/lazy\_kafka/plugin/\_\_init\_\_.py                   |       33 |        2 |        4 |        0 |     95% |    57, 61 |
| src/lazy\_kafka/plugins/\_\_init\_\_.py                  |        3 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/plugins/core\_kafka/\_\_init\_\_.py      |       27 |        3 |        0 |        0 |     89% | 34-35, 39 |
| src/lazy\_kafka/plugins/core\_kafka/cli.py               |       84 |       59 |       12 |        0 |     26% |38-58, 84-105, 131-134, 138-207 |
| src/lazy\_kafka/plugins/kafka\_connect/\_\_init\_\_.py   |       24 |        3 |        0 |        0 |     88% |     34-36 |
| src/lazy\_kafka/plugins/kafka\_connect/cli.py            |       26 |        5 |        4 |        2 |     77% |43, 48, 51-53 |
| src/lazy\_kafka/plugins/schema\_registry/\_\_init\_\_.py |       23 |        3 |        0 |        0 |     87% |     32-34 |
| src/lazy\_kafka/plugins/schema\_registry/cli.py          |       25 |        9 |        2 |        0 |     59% |     60-73 |
| src/lazy\_kafka/registry.py                              |      101 |       17 |       14 |        3 |     79% |45, 60-64, 68-\>75, 127, 131, 151-152, 196-215 |
| src/lazy\_kafka/scripts/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/scripts/produce\_from\_schema.py         |      130 |       37 |       52 |        2 |     75% |192, 195-196, 207-209, 213-216, 220-270 |
| src/lazy\_kafka/serializers.py                           |       45 |        4 |       10 |        1 |     91% |31-33, 74-75 |
| src/lazy\_kafka/theme.py                                 |        4 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/topic.py                                 |      243 |      118 |       46 |        1 |     47% |160-162, 165-167, 213, 250-252, 270-287, 300-317, 330-401, 410-412, 415-429, 463-492, 496 |
| src/lazy\_kafka/utils.py                                 |       26 |        0 |        8 |        0 |    100% |           |
| src/lazy\_kafka/widgets/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/widgets/\_logs.py                        |      181 |       20 |       38 |       11 |     83% |108, 116-119, 207-\>210, 220-\>222, 229, 244, 248-\>exit, 281, 328, 330-\>exit, 335-341, 345-346, 350-351, 355-\>exit, 360-\>exit, 370-\>373, 388, 416-\>exit |
| src/lazy\_kafka/widgets/\_status.py                      |       10 |        0 |        0 |        0 |    100% |           |
| src/lazy\_kafka/widgets/common.py                        |      195 |       26 |       34 |        9 |     84% |36-\>exit, 198-201, 204-207, 210-213, 236, 261-\>263, 263-\>exit, 269, 310-312, 323-324, 347, 350-351, 358, 360-361, 366-367, 381, 412-\>exit, 415-\>exit |
| src/lazy\_kafka/widgets/kconnect.py                      |       46 |       11 |        4 |        0 |     70% |34-47, 51, 90, 96-103 |
| src/lazy\_kafka/widgets/registry.py                      |      143 |       62 |       16 |        0 |     53% |38-41, 45, 101-104, 111-120, 134-152, 169-171, 185-187, 191-197, 200, 212-213, 233-239, 243-246, 250-255, 259-266, 287, 292 |
| src/lazy\_kafka/widgets/switcher.py                      |       46 |       19 |       12 |        0 |     50% |101-108, 123-139 |
| src/lazy\_kafka/widgets/topic.py                         |       38 |        4 |        0 |        0 |     89% | 44-52, 76 |
| src/lazy\_kafka/widgets/topic\_details.py                |       84 |        8 |        4 |        2 |     89% |116-119, 127, 144-146 |
| tests/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| tests/conftest.py                                        |       86 |       26 |        0 |        0 |     70% |26, 36, 42, 52, 108-111, 128-134, 141-145, 151, 167-171 |
| tests/integration/\_\_init\_\_.py                        |        0 |        0 |        0 |        0 |    100% |           |
| tests/integration/test\_search\_filter.py                |       87 |        0 |        0 |        0 |    100% |           |
| tests/integration/test\_tui.py                           |      212 |        0 |        6 |        0 |    100% |           |
| tests/test\_cli.py                                       |       96 |        0 |        0 |        0 |    100% |           |
| tests/test\_config.py                                    |      133 |        0 |        0 |        0 |    100% |           |
| tests/test\_connect.py                                   |      165 |        0 |        0 |        0 |    100% |           |
| tests/test\_plugin.py                                    |      101 |       13 |        8 |        3 |     85% |63, 66, 83, 86, 116, 119, 144-147, 168, 177-179, 187-189 |
| tests/test\_produce\_from\_schema.py                     |       97 |        0 |        0 |        0 |    100% |           |
| tests/test\_registry.py                                  |      147 |        0 |        0 |        0 |    100% |           |
| tests/test\_serializers.py                               |       70 |        0 |        0 |        0 |    100% |           |
| tests/test\_topic.py                                     |      192 |        1 |        0 |        0 |     99% |       315 |
| tests/test\_utils.py                                     |       55 |        0 |        0 |        0 |    100% |           |
| tests/test\_widgets.py                                   |       67 |        0 |        0 |        0 |    100% |           |
| **TOTAL**                                                | **3419** |  **502** |  **318** |   **44** | **83%** |           |


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