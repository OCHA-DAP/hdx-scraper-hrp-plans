#!/usr/bin/python
"""Hrp_plans scraper"""

import logging

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.resource import Resource
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, configuration: Configuration, retriever: Retrieve, tempdir: str):
        self._configuration = configuration
        self._retriever = retriever
        self._tempdir = tempdir
        self.data = []
        self.dates = []

    def get_data(self) -> None:
        source_url = self._configuration["source_url"]
        json = self._retriever.download_json(source_url)

        for plan in json["data"]:
            new_row = {}
            new_row["code"] = plan["planVersion"]["code"]
            new_row["internalId"] = plan["planVersion"]["id"]

            start_date = plan["planVersion"]["startDate"]
            new_row["startDate"] = start_date
            self.dates.append(start_date)
            end_date = plan["planVersion"]["endDate"]
            new_row["endDate"] = end_date
            self.dates.append(end_date)

            new_row["planVersion"] = plan["planVersion"]["name"]

            categories = [c["name"] for c in plan["categories"]]
            new_row["categories"] = " | ".join(categories)

            iso3s = []
            for location in plan["locations"]:
                if location.get("adminLevel") == 0:
                    iso3 = location.get("iso3")
                    if iso3:
                        iso3s.append(iso3)
            new_row["locations"] = " | ".join(iso3s)

            years = [y["year"] for y in plan["years"]]
            years = int(years[0]) if len(years) == 1 else " | ".join(years)
            new_row["years"] = years

            new_row["origRequirements"] = plan["origRequirements"]
            new_row["revisedRequirements"] = plan["revisedRequirements"]

            self.data.append(new_row)
        return

    def generate_dataset(self) -> Dataset:
        dataset_name = self._configuration["dataset_info"]["name"]
        dataset_title = self._configuration["dataset_info"]["title"]
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )

        start_date = min(self.dates)
        end_date = max(self.dates)
        dataset.set_time_period(start_date, end_date)
        dataset.add_tags(self._configuration["tags"])
        dataset.add_other_location("world")

        resourcedata = {
            "name": "humanitarian-response-plans.csv",
            "description": "CSV list of Humanitarian Response Plans dating back to 1999 converted from the JSON API output.",
        }
        dataset.generate_resource(
            self._tempdir,
            "humanitarian-response-plans.csv",
            self.data,
            resourcedata,
            list(self.data[0].keys()),
            encoding="utf-8-sig",
        )

        resource = Resource(
            {
                "name": "HPC Tools API output",
                "description": "Original JSON API output (live).",
                "url": self._configuration["source_url"],
            }
        )
        resource.set_format("json")
        dataset.add_update_resource(resource)

        return dataset
