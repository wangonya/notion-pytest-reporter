from ._reporter import NotionReporter


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption(
        '--notion-token',
        dest='notion_token',
        action='store',
        type=str,
        default=None,
        help='Notion API Token (see README for details on how to extract)'
    )
    group.addoption(
        '--test-cycle-url',
        dest='notion_test_cycle_url',
        action='store',
        type=str,
        default='https://www.notion.so/colinwren/2a6e31c00aba43c0bcc55c02e8000c7b?v=d976804b8225424caf4402091c571452',
        help='URL for the Test Cycle Collection'
    )
    group.addoption(
        '--test-case-url',
        dest='notion_test_case_url',
        action='store',
        type=str,
        default='https://www.notion.so/colinwren/a742ec336cfd4dc3b9ca0491849fba6e?v=c30c7b81c1e3489f8e5f8cd799ec5f22',
        help='URL for the Test Case Collection'
    )


def pytest_configure(config):
    token = config.option.notion_token
    cycle_url = config.option.notion_test_cycle_url
    case_url = config.option.notion_test_case_url
    config.addinivalue_line('markers', 'notion_test(name): Name of test case')
    if token:
        config._notion_reporter = NotionReporter(token, cycle_url, case_url)
        config.pluginmanager.register(config._notion_reporter)


def pytest_unconfigure(config):
    notion_reporter = getattr(config, '_notion_reporter', None)
    if notion_reporter:
        del config._notion_reporter
        config.pluginmanager.unregister(notion_reporter)
