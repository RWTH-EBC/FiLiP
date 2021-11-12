"""
@author Thomas Storek

Tests for time series model
"""
import logging
import unittest
from filip.models.ngsi_v2.timeseries import TimeSeries


logger = logging.getLogger(__name__)


class TestTimeSeriesModel(unittest.TestCase):
    """
    Test class for time series model
    """
    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.data1 = {
            "attributes": [
                {
                    "attrName": "temperature",
                    "values": [
                        24.1,
                        25.3,
                        26.7
                    ]
                },
                {
                    "attrName": "pressure",
                    "values": [
                        1.01,
                        0.9,
                        1.02
                    ]
                }
            ],
            "entityId": "Kitchen",
            "index": [
                "2018-01-05T15:44:34",
                "2018-01-06T15:44:59",
                "2018-01-07T15:44:59"
            ]
        }
        self.data2 = {
            "attributes": [
                {
                    "attrName": "temperature",
                    "values": [
                        34.1,
                        35.3,
                        36.7
                    ]
                },
                {
                    "attrName": "pressure",
                    "values": [
                        2.01,
                        1.9,
                        2.02
                    ]
                }
            ],
            "entityId": "Kitchen",
            "index": [
                "2018-01-08T15:44:34",
                "2018-01-09T15:44:59",
                "2018-01-10T15:44:59"
            ]
        }

    def test_model_creation(self):
        """
        Test model creation
        """
        TimeSeries.parse_obj(self.data1)

    def test_extend(self):
        """
        Test merging of multiple time series objects
        """

        ts1 = TimeSeries.parse_obj(self.data1)
        logger.debug(f"Initial data set: \n {ts1.to_pandas()}")
        ts2 = TimeSeries.parse_obj(self.data2)
        ts1.extend(ts2)
        logger.debug(f"Extended data set: \n {ts1.to_pandas()}")

        with self.assertRaises(AssertionError):
            ts1.extend(ts2)


if __name__ == '__main__':
    unittest.main()
