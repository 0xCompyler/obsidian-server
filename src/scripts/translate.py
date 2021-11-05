import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import secrets

def send_document(path: str):
    authenticator = IAMAuthenticator(secrets.translate_api_key)
    language_translator = LanguageTranslatorV3(
        version='2018-05-01',
        authenticator=authenticator
    )

    language_translator.set_service_url(secrets.translate_url)


    with open(path, 'rb') as file:
        result = language_translator.translate_document(
            file=file,
            file_content_type='application/pdf',
            filename='en.pdf',
            model_id='en-fr').get_result()
        return json.dumps(result, indent=2)


def get_document_status(document_id):
    authenticator = IAMAuthenticator(secrets.translate_api_key)
    language_translator = LanguageTranslatorV3(
        version='2018-05-01',
        authenticator=authenticator
    )

    language_translator.set_service_url(secrets.translate_url)

    result = language_translator.get_document_status(
        document_id).get_result()
    return json.dumps(result, indent=2)


def download_file(document_id):
    authenticator = IAMAuthenticator(secrets.translate_api_key)
    language_translator = LanguageTranslatorV3(
        version='2018-05-01',
        authenticator=authenticator
    )

    language_translator.set_service_url(secrets.translate_url)

    with open('translated.pdf', 'wb') as f:
        result = language_translator.get_translated_document(
            document_id,
            accept='application/pdf').get_result()
        f.write(result.content)

# print(send_document("DUMP/199301020.docx"))
print(get_document_status("7a8dec6f-dbe8-470c-a6ea-cbb30faa6c80"))
# download_file("34992346-6287-4368-b778-b09d59f09324")