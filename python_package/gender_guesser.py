from gender_guesser.detector import Detector
import re


def guess_gender_worker(name):
    name = re.sub(r'\d+', '', name)  # Remove digits from name
    name_parts = re.split('[ _]', name)  # Split on " " and "_"
    name = name_parts[0]
    d = Detector()
    gender = d.get_gender(name)

    return {"name": name, "gender": gender}
