from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
import os
from typing import List, Optional
import re
import pytz

import requests
from bs4 import BeautifulSoup
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials


@dataclass
class Slaapje:
    start: datetime
    end: Optional[datetime] = None
    type: str = "sleep"
    deona: bool = True


@dataclass
class Voeding:
    start: datetime
    end: datetime
    amount: int
    type: str = "food"
    subtype: str = "formula"
    deona: bool = True


class DeonaException(Exception):
    """An exception for bad input in Deona."""


def get_timestamp_with_current_date(time_str):
    # Get the current date
    current_date = date.today()

    # Parse the time string into a time object
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    # Combine the date and time into a datetime object
    timestamp = datetime.combine(current_date, time_obj)

    # Localize
    local_tz = pytz.timezone("Europe/Brussels")
    local_dt = local_tz.localize(timestamp)
    utc_dt = local_dt.astimezone(pytz.UTC)

    return utc_dt


def extract_number(string):
    # Find all the digits in the string
    match = re.search(r"\d+", string)
    if match:
        # Convert the matched number to an integer
        return int(match.group())
    else:
        raise DeonaException(
            f"Geen nummer gevonden voor de hoeveelheid van het flesje! Origineel bericht: {string}"
        )


def record_exists(db, db_table: str, record: Voeding | Slaapje) -> bool:
    query = (
        db.collection(db_table)
        .where("start", "==", record.start)
        .where("end", "==", record.end)
        .where("type", "==", record.type)
        .limit(1)
    )

    return bool(query.get())


def read_from_deona():
    standaard_hoeveelheid = 240
    # Start a session
    session = requests.Session()
    db = firestore.client()
    db_table = "entries"

    # Step 1: Load the login page
    login_url = "https://lokerenkdv.mijn-deona.be/Account/Login"
    response = session.get(login_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the anti-forgery token from the page
    token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value")

    # Define login data
    login_data = {
        "Email": "victor.sonck@gmail.com",
        "Password": os.getenv("DEONA_PASSWORD"),
        "__RequestVerificationToken": token,
    }

    # Send a POST request to the login page
    response = session.post(login_url, data=login_data)

    # Now logged in, you can request another page
    url_page = "https://lokerenkdv.mijn-deona.be/api/BoekjeContent/2740/0/"
    page = session.get(url_page)

    # Use Beautiful Soup to parse and extract information
    soup = BeautifulSoup(page.content, "html.parser")
    if soup.contents == ["null"]:
        raise DeonaException("Iets is verkeerd gegaan bij het inloggen...")
    divs = soup.find_all("div", class_="boekjeContentRegel")

    open_slaapje: Optional[Slaapje] = None
    slaapjes: List[Slaapje] = []
    voedingen: List[Voeding] = []

    if len(divs) == 0:
        raise DeonaException("Geen dagboeklijnen gevonden!")

    for div in divs:
        hour = div.find("div", class_="boekjeRegelDatum").text.strip()
        if hour == "":
            continue
        timestamp = get_timestamp_with_current_date(hour)
        message = div.find("div", class_="boekjeRegelBericht").text.strip()

        if message.startswith("Slapen"):
            if "In slaap gevallen" in message or "In bed gelegd" in message:
                if open_slaapje:
                    raise DeonaException(
                        "2 keer na elkaar in slaap gevallen zonder wakker worden!"
                    )
                # Start een slaapje
                open_slaapje = Slaapje(start=timestamp)
            elif "Wakker geworden" in message:
                if not open_slaapje:
                    raise DeonaException("Is wakker geworden voor te gaan slapen!")
                # Stop een slaapje, zet het einduur, voeg het toe aan volledige slaapjes en reset het huidige slaapje
                open_slaapje.end = timestamp
                slaapjes.append(open_slaapje)
                open_slaapje = None
            elif "niet" in message and "slapen" in message:
                if not open_slaapje:
                    raise DeonaException(
                        "Heeft niet kunnen slapen, maar er was nog geen slaapje gestart?"
                    )
                # Dan toch niet in slaap gevallen
                open_slaapje = None

        elif message.startswith("Voeding"):
            if "alles op" in message:
                # Sometime the caregiver uses "alles opgedroken" to denote a bottle completed
                # at another time, sometime its "verder opgedronken" and sometimes "alles op!".
                # Decide if it is within a certain time window from the last to determine this.

                # So either we're completing a bottle that was not finished before
                if (
                    len(voedingen) > 0
                    and (timestamp - voedingen[-1].end) < timedelta(hours=1)
                    and voedingen[-1].amount < standaard_hoeveelheid
                ):
                    voedingen[-1].amount = standaard_hoeveelheid
                    voedingen[-1].end = timestamp

                else:
                    # OR the bottle was drank in one go
                    voedingen.append(
                        Voeding(
                            start=timestamp - timedelta(minutes=15),
                            end=timestamp,
                            amount=standaard_hoeveelheid,
                        )
                    )
            elif "beetje melk overgelaten" in message:
                # There is no number, so estimate it to be about 20ml ish under the standaard hoeveelheid
                voedingen.append(
                    Voeding(
                        start=timestamp - timedelta(minutes=15),
                        end=timestamp,
                        amount=max(0, standaard_hoeveelheid - 20),
                    )
                )
            elif "over" in message:
                # Get the number, it will always be in ml left in the bottle
                amount = extract_number(message)
                # Apparently this, too, can be used to denote the same bottle being completed
                if (
                    len(voedingen) > 0
                    and (timestamp - voedingen[-1].end) < timedelta(hours=1)
                    and voedingen[-1].amount < standaard_hoeveelheid
                ):
                    voedingen[-1].amount = standaard_hoeveelheid - amount
                    voedingen[-1].end = timestamp
                else:
                    # Or create a new bottle
                    voedingen.append(
                        Voeding(
                            start=timestamp - timedelta(minutes=15),
                            end=timestamp,
                            amount=standaard_hoeveelheid - amount,
                        )
                    )
            elif "verder opgedronken" in message:
                # Get the number, it will always be in ml left in the bottle
                voedingen[-1].amount = standaard_hoeveelheid
                voedingen[-1].end = timestamp
            elif match := re.search(r"(\d+) *g", message):
                voedingen.append(
                    Voeding(
                        start=timestamp - timedelta(minutes=15),
                        end=timestamp,
                        amount=match.group(1),
                        subtype="solid",
                    )
                )

    print("\n".join([f"{s.start} {s.end}" for s in slaapjes]))
    print("\n".join([f"{v.start} {v.end} {v.amount}" for v in voedingen]))

    if len(slaapjes) == 0 and len(voedingen) == 0:
        raise DeonaException(
            "Geen dagboek acties gevonden op de site, waarschijnlijk is de dag nog niet afgesloten in Deona."
        )

    for slaapje in slaapjes:
        if not record_exists(db, db_table, record=slaapje):
            db.collection(db_table).add(asdict(slaapje))

    for voeding in voedingen:
        if not record_exists(db, db_table, record=voeding):
            db.collection(db_table).add(asdict(voeding))


if __name__ == "__main__":
    cred = credentials.Certificate(
        "/home/victor/Projects/babytracker/babytracker-b2323-109057e17ae6.json"
    )
    firebase_admin.initialize_app(cred)
    read_from_deona()
