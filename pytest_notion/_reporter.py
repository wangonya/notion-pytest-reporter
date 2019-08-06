from notion.client import NotionClient
from notion.collection import NotionDate
from notion.block import CollectionViewBlock
from datetime import datetime
from logging import getLogger

logger = getLogger(__name__)


class NotionReporter(object):
    def __init__(self, token, cycle_url, execution_url, test_url):
        logger.info('Inside NotionReporter')
        self.notion = NotionClient(token_v2=token)
        self.cycles = self.notion.get_collection_view(cycle_url)
        self.tests = self.notion.get_collection_view(test_url)
        # Add test cycle
        self.cycle = self.cycles.collection.add_row(
            icon='🚴',
            name='Reporter Test',
            date_executed=NotionDate(datetime.now()),
            execution_status='Unexecuted'
        )
        cvb = self.cycle.children.add_new(CollectionViewBlock)
        collection = self.notion.get_collection(self.notion.create_record("collection", parent=cvb, schema=self.get_test_execution_schema()))
        view = self.notion.get_collection_view(self.notion.create_record("collection_view", parent=cvb, type="board"), collection=collection)
        view.set("collection_id", collection.id)
        cvb.set("collection_id", collection.id)
        cvb.set("view_ids", [view.id])
        cvb.title = "Test Executions"
        self.test_executions = view

    def pytest_collection_modifyitems(self, config, items):
        for item in items:
            notion_marker = [mark for mark in item.own_markers if mark.name == 'notion_test']
            if notion_marker:
                test_case_name = notion_marker[0].args[0]
                test_cases = self.tests.build_query(search=test_case_name).execute()
                if test_cases:
                    item.user_properties.append(test_cases[0])

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            test_execution = self.test_executions.collection.add_row(
                icon='🔫',
                name=report.user_properties[0].title,
                date_executed=NotionDate(datetime.now()),
                test_case=report.user_properties[0].id,
                # test_cycle=self.cycle.id,
                executed_by=self.notion.current_user
            )
            if report.passed:
                test_execution.status = 'Passed'
            if report.failed:
                test_execution.status = 'Failed'
                test_execution.notes = report.longreprtext

    def get_test_execution_schema(self):
        return {
            '$4X3': {
                'name': 'Status',
                'type': 'select',
                'options': [
                    {
                        'id': 'f24e4360-65c5-45de-b4e3-c9af423b6e2c',
                        'color': 'default',
                        'value': 'Unexecuted'
                    },
                    {
                        'id': 'f71238f5-7cf0-4f40-934b-f347434011b2',
                        'color': 'green',
                        'value': 'Passed'
                    },
                    {
                        'id': '966e59d2-dfed-4b2d-b324-9120aeab4cd8',
                        'color': 'red',
                        'value': 'Failed'
                    }
                ]
            },
            '-(mE': {
                'name': 'Notes',
                'type': 'text'
            },
            '5bJH': {
                'name': 'Test Case',
                'type': 'relation',
                'property': ':2X9',
                'collection_id': '270b0369-d6ec-4f53-b008-5a3e77df56e0'
            },
            'U+eo': {
                'name': 'Date Executed',
                'type': 'date'
            },
            '^ZM?': {
                'name': 'Executed by',
                'type': 'person'
            },
            'title': {
                'name': 'Name',
                'type': 'title'
            }
        }
