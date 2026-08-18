from datetime import datetime

def normalize_text(name):
    name = name.lower().strip()
    name_arr = name.split(' ')
    name = " ".join(name_arr)

    return name

def normalize_weight(weight):

    weightclass = ''

    match weight:
        case none if weight is None:
            weightclass = "N/A"
        case Strawweight if weight <= 115:
            weightclass = "Strawweight"
        case Flyweight if weight <= 125:
            weightclass = "Flyweight"
        case Bantamweight if weight <= 135:
            weightclass = "Bantamweight"
        case Featherweight if weight <= 145:
            weightclass = "Featherweight"
        case Lightweight if weight <= 155:
            weightclass = "Lightweight"
        case Welterweight if weight <= 175:
            weightclass = "Welterweight"
        case Middleweight if weight <= 185:
            weightclass = "Middleweight"
        case L_heavyweight if weight <= 205:
            weightclass = "Light heavyweight"
        case Heavyweight if weight <= 265:
            weightclass = "Heavyweight"

    return weightclass

def normalize_age(date):
    if date == 0 or date == None:
        return "N/A"

    birth_date = datetime.fromisoformat(date).date()
    today = datetime.today().date()

    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return age

def normalize_height(height):
    if height == 0 or height == None:
        return "N/A"

    feet = height // 12
    inches = height % 12

    return f"{feet}'  {inches}\" "
    