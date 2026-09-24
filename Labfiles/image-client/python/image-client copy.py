import os
import json
import base64
import requests

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def main():

    os.system('cls' if os.name == 'nt' else 'clear')

    try:

        print("=" * 80)
        print("Starting application...")
        print("=" * 80)

        load_dotenv()

        endpoint = os.getenv("ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        print("ENDPOINT:", endpoint)
        print("MODEL_DEPLOYMENT:", model_deployment)

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True
            ),
            "https://cognitiveservices.azure.com/.default"
        )

        print("Token provider created successfully.")

        token = token_provider()

        print("Token acquired successfully.")
        print("Token Length:", len(token))

        img_no = 0

        while True:

            prompt = input(
                "\nEnter the prompt (or type 'quit' to exit): "
            )

            if prompt.lower() == "quit":
                break

            if not prompt.strip():
                print("Please enter a prompt.")
                continue

            print("\n" + "=" * 80)
            print("IMAGE REQUEST")
            print("=" * 80)
            print("Prompt:", prompt)

            flux_url = (
                "https://jeevita-raorunku-3566-resource.services.ai.azure.com"
                "/providers/blackforestlabs/v1/flux-2-pro"
                "?api-version=preview"
            )

            print("URL:", flux_url)

            payload = {
                "prompt": prompt,
                "model": "FLUX.2-pro",
                "width": 1024,
                "height": 1024,
                "n": 1
            }

            print("\nPayload:")
            print(json.dumps(payload, indent=2))

            response = requests.post(
                flux_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            print("\nStatus Code:", response.status_code)

            if response.status_code != 200:

                print("\nResponse Headers:")
                print(dict(response.headers))

                print("\nResponse Body:")
                print(response.text)

                continue

            print("✅ Image generated successfully")

            json_response = response.json()

            image_data = json_response["data"][0]["b64_json"]

            image_data_in_bytes = base64.b64decode(image_data)

            img_no += 1

            file_name = f"image_{img_no}.png"

            save_image(image_data_in_bytes, file_name)

    except Exception as ex:

        print("\nERROR TYPE:", type(ex).__name__)
        print("ERROR:", ex)


def save_image(image_data, file_name):

    image_dir = os.path.join(os.getcwd(), "images")

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    image_path = os.path.join(image_dir, file_name)

    with open(image_path, "wb") as image_file:
        image_file.write(image_data)

    print(f"\n✅ Image saved as {image_path}")


if __name__ == "__main__":
    main()