from os.path import join

from hdx.utilities.compare import assert_files_same
from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

from hdx.scraper.hrp_plans.pipeline import Pipeline


class TestPipeline:
    def test_pipeline(self, configuration, fixtures_dir, input_dir, config_dir):
        with temp_dir(
            "TestHRP_plans",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            with Download(user_agent="test") as downloader:
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=input_dir,
                    temp_dir=tempdir,
                    save=False,
                    use_saved=True,
                )
                pipeline = Pipeline(configuration, retriever, tempdir)
                pipeline.get_data()
                dataset = pipeline.generate_dataset()
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )
                assert dataset == {
                    "name": "humanitarian-response-plans",
                    "title": "Humanitarian Response Plans",
                    "dataset_date": "[1999-10-01T00:00:00 TO 2022-12-31T23:59:59]",
                    "tags": [
                        {
                            "name": "humanitarian response plan-hrp",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        }
                    ],
                    "groups": [{"name": "world"}],
                    "license_id": "other-pd-nr",
                    "methodology": "Registry",
                    "caveats": "All currency amounts are in USD. The JSON resource contains complete information, while the CSV resource is a simplified version for convenient spreadsheet use.",
                    "dataset_source": "HPC Tools",
                    "package_creator": "HDX Data Systems Team",
                    "private": False,
                    "maintainer": "07e9f1c2-523e-4862-8318-525436c5df1c",
                    "owner_org": "ocha-fts",
                    "data_update_frequency": 30,
                    "notes": "A live list of all past and present _Humanitarian Response Plans,_ with identifiers for use in International Aid Transparency Initiative (IATI) reporting and elsewhere. \r\n\r\nThe UN and its partners prepare a Humanitarian Response Plan (HRP) plan for a protracted or sudden onset emergency that requires international humanitarian assistance. The plan articulates the shared vision of how to respond to the assessed and expressed needs of the affected population.",
                    "subnational": "0",
                }

                resources = dataset.get_resources()
                assert resources == [
                    {
                        "name": "humanitarian-response-plans.csv",
                        "description": "CSV list of Humanitarian Response Plans dating back to 1999 converted from the JSON API output.",
                        "format": "csv",
                    },
                    {
                        "name": "HPC Tools API output",
                        "description": "Original JSON API output (live).",
                        "url": "http://api.hpc.tools/v2/public/plan",
                        "format": "json",
                    },
                ]

                file = "humanitarian-response-plans.csv"
                assert_files_same(join(fixtures_dir, file), join(tempdir, file))
