import requests
import pandas as pd


class SHABRequestAPI:
    def __init__(self):
        self.base_url = """https://www.shab.ch/api/v1/"""

    def get_publications(self, size=1000, publication_date_start="2024-10-31", publication_date_end="2024-11-06", hr=False):
        url = self.base_url + "publications"
        url += f"?allowRubricSelection=true&cantons=GE&includeContent=true&pageRequest.page=0&pageRequest.size={size}&publicationStates=PUBLISHED&publicationStates=CANCELLED&publicationDate.end={publication_date_end}&publicationDate.start={publication_date_start}"
        if hr:
            url += "&subRubrics=HR01"

        response = requests.get(url)
        return response.json()["content"]

    def get_new_entries(self, size=1000, publication_date_start="2024-10-31", publication_date_end="2024-11-06"):
        # https://www.shab.ch/api/v1/publications?allowRubricSelection=true&cantons=GE&includeContent=false&pageRequest.page=0&pageRequest.size=1000&publicationDate.end=2024-11-12&publicationDate.start=2024-11-06&publicationStates=PUBLISHED&publicationStates=CANCELLED&subRubrics=HR01

        return self.get_publications(size=size, publication_date_start=publication_date_start, publication_date_end=publication_date_end, hr=True)

    def publications_data_to_df(self, data):
        # Extraction des données pour construire le DataFrame
        extracted_data = []
        for item in data:
            # Extraire les données de "meta"
            meta_data = item['meta']
            # Extraire les données de "content"
            content_data = item.get('content', {})

            # Les données de la compagnie peuvent être dans "commonsActual" ou dans "commonsNew"
            company_data = content_data.get(
                'commonsActual', {}).get('company', {})
            if not company_data:
                company_data = content_data.get(
                    'commonsNew', {}).get('company', {})

            address_data = company_data.get('address', {})

            # Vérification sécurisée pour capital
            capital_list = content_data.get(
                'commonsActual', {}).get('capital', [])
            if not capital_list:
                capital_list = content_data.get(
                    'commonsNew', {}).get('capital', [])

            # Vérifie que c'est une liste non vide
            if isinstance(capital_list, list) and len(capital_list) > 0:
                capital_data = capital_list[0]
            else:
                # Valeurs par défaut si pas de capital
                capital_data = {"nominal": None, "paid": None}

            # Combiner les données de meta, company, address et capital en une seule ligne
            row = {
                "id": meta_data.get("id"),
                "creationDate": meta_data.get("creationDate"),
                "updateDate": meta_data.get("updateDate"),
                "rubric": meta_data.get("rubric"),
                "subRubric": meta_data.get("subRubric"),
                "language": meta_data.get("language"),
                "publicationNumber": meta_data.get("publicationNumber"),
                "publicationState": meta_data.get("publicationState"),
                "publicationDate": meta_data.get("publicationDate"),
                "title_fr": meta_data.get("title", {}).get("fr"),
                "company_name": company_data.get("name"),
                "company_uid": company_data.get("uid"),
                "company_seat": company_data.get("seat"),
                "address_street": address_data.get("street"),
                "address_houseNumber": address_data.get("houseNumber"),
                "address_swissZipCode": address_data.get("swissZipCode"),
                "address_town": address_data.get("town"),
                "purpose": content_data.get("commonsActual", {}).get("purpose") or content_data.get("commonsNew", {}).get("purpose"),
                "capital_nominal": capital_data.get("nominal"),
                "capital_paid": capital_data.get("paid"),
                "journalNumber": content_data.get("journalNumber"),
                "publicationText": content_data.get("publicationText"),
            }

            extracted_data.append(row)
        return pd.DataFrame(extracted_data)
