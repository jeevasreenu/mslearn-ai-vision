import sys
import os
import json
from dotenv import load_dotenv

# Azure Content Understanding
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput, AnalysisResult
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential


def main():
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load configuration
    load_dotenv()

    endpoint = os.getenv("ENDPOINT")
    analyzer_id = os.getenv("ANALYZER")
    api_version = "2026-06-01-preview"

    if not endpoint:
        print("ENDPOINT is missing in .env file")
        sys.exit(1)

    if not analyzer_id:
        print("ANALYZER is missing in .env file")
        sys.exit(1)

    print(f"Endpoint : {endpoint}")
    print(f"Analyzer : {analyzer_id}")

    # Create client
    credential = DefaultAzureCredential()

    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=credential,
        api_version=api_version
    )

    while True:

        file_no = input(
            "\nChoose a file (1, 2, or 3), or anything else to exit: "
        )

        if file_no not in ["1", "2", "3","4"]:
            print("Exiting...")
            break

        file_path = f"images/image{file_no}.jpg"

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"\nAnalyzing with analyzer '{analyzer_id}'")
        print(f"File: {file_path}")

        try:

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            poller = client.begin_analyze(
                analyzer_id=analyzer_id,
                inputs=[
                    AnalysisInput(data=file_bytes)
                ]
            )

            result: AnalysisResult = poller.result()

        except AzureError as err:
            print(f"\n[Azure Error]")
            print(err)
            continue

        except Exception as ex:
            print(f"\n[Unexpected Error]")
            print(ex)
            continue

        print("\n========== RAW RESPONSE ==========")

        try:
            print(json.dumps(result.as_dict(), indent=2))
        except Exception:
            print(result)

        print("==================================\n")

        # Verify contents exist
        if not result.contents:
            print("No contents returned by the analyzer.")
            continue

        content = result.contents[0]

        # Verify fields exist
        if not hasattr(content, "fields") or content.fields is None:
            print("Fields are NULL.")
            print("Your analyzer may not be returning Description/Tags fields.")
            continue

        fields = content.fields

        if len(fields) == 0:
            print("No fields returned.")
            continue

        print("\n========== ANALYZER OUTPUT ==========\n")

        for field_name, field_value in fields.items():

            print(f"Field: {field_name}")

            try:

                if hasattr(field_value, "value_string"):
                    print(f"Value : {field_value.value_string}")

                elif hasattr(field_value, "value_number"):
                    print(f"Value : {field_value.value_number}")

                elif hasattr(field_value, "value_boolean"):
                    print(f"Value : {field_value.value_boolean}")

                elif hasattr(field_value, "value_array") and field_value.value_array:

                    print("Values:")

                    for item in field_value.value_array:

                        if hasattr(item, "value_string"):
                            print(f"  - {item.value_string}")
                        else:
                            print(f"  - {item}")

                else:
                    print(field_value)

            except Exception as e:
                print(f"Unable to display value: {e}")

            print()

        print("====================================")


if __name__ == "__main__":
    main()