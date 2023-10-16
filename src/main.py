import converter, create_json
import pdfplumber as pdfp
import os, json

""""
TO-DO
1. check for page number[1] is larger than page number[1]
2. have more apt error msgs for days input
3. integrate with actual scripts
4. comments

optional
1. function up the diff input blocks
2. implement better checking
"""


def verifyInputForNumber(inp: list[str]) -> (bool, str):
    """
    Function to check if the input is numeric.

    Args:
    inp: list[str] - list of inputs from the user.

    Returns:
    (bool,str) - a tuple with boolean and the first character where it fails returns '' if all inputs are numbers.
    """

    if inp == []:
        return (True, "")
    for x in inp:
        if not x.isnumeric() or int(x) < 0:
            return (False, x)
    return (True, "")


if __name__ == "__main__":
    print("-------CSV generation-------")
    print("---Select timetable file---")
    print("Select path for the timetable pdf")
    print("1. Default path : files/timetable.pdf")
    print("2. Pass custom path")
    while True:
        choice_in: str = input("Enter your choice: ")
        if not verifyInputForNumber(choice_in.split())[0]:
            print("Invalid Choice!")
        else:
            choice: int = int(choice_in[0])
            break

    file_path: str = r"./files/timetable.pdf"
    if choice == 2:
        file_path: str = input("Enter the complete file path: ")
        file_path.replace('"', "")
        while True:
            if not (os.path.isfile(file_path)):
                print("Invalid file path!")
                file_path: str = input(
                    "Enter the complete file path or press enter to continue with default file path: "
                )
                file_path.replace('"', "")
                if file_path == "":
                    file_path: str = r"./files/timetable.pdf"
                    break
            else:
                break

    while True:
        page_list_in: str = input(
            "Enter the start and end page of the timetable.For e.g. 1 4 : "
        )
        page_list: list[int] = []
        if not verifyInputForNumber(page_list_in.split())[0]:
            print(
                f"Invalid input! '{verifyInputForNumber(page_list_in.split())[1]}' is not a valid page number."
            )
            continue
        else:
            page_list = [int(x) for x in page_list_in.split()]
        if len(page_list) < 2:
            print("Invalid range! Please specify both a starting and an ending page")
        else:
            break
    try:
        file: pdfp.pdf.PDF = pdfp.open(file_path)
        pages: list[pdfp.page.Page] = file.pages[page_list[0] - 1 : page_list[1]]
        headers: list[str] = ["COM\nCOD"]

    except:
        print("Some Error occured! Terminating..")
        raise Exception

    print("CSV created!")
    print()

    print("-------JSON creation-------")
    while True:
        metadata_in: str = input(
            "Enter the academic year and semester(1 or 2). For e.g. 2023 1 :"
        )
        metadata: list[int] = []

        if not verifyInputForNumber(metadata_in.split())[0]:
            print(
                f"Invalid input! '{verifyInputForNumber(metadata_in.split())[1]}' is not a valid year or semester."
            )
            continue
        else:
            metadata = [int(x) for x in metadata_in.split()]
        if len(metadata) < 2:
            print("Invalid input! Please specify both year and semester")
        elif metadata[1] not in [1, 2]:
            print("Invalid input! semester has to be 1 or 2")
        else:
            break

    year: int = metadata[0]
    semester: int = metadata[1]
    print("JSON created!")
    print()

    print("-------TT generation-------")
    courses = json.load(open("./files/timetable.json", "r"))["courses"].keys()
    CDCs: list[str] = []
    print("Please enter your CDCs(enter q to when done):")
    while True:
        CDC: str = input()
        if CDC.lower() == "q":
            break
        elif CDC.upper() not in courses:
            print("Invalid course code! Please try again")
        else:
            CDCs.append(CDC)

    DELs: list[str] = []
    OPELs: list[str] = []
    HUELs: list[str] = []
    preference_order: list[str] = ["DELs", "HUELs", "OPELs"]
    choice = input(
        "Enter 'add' to add DELs,OPELs,HUELs or enter 'skip' to skip this section: "
    )
    while True:
        if choice.lower() not in ["add", "skip"]:
            choice = input("Invalid Choice! Please enter add or skip: ")
        else:
            break

    if choice.lower() == "add":
        print("Please enter your DELs(enter q to when done):")
        while True:
            DEL: str = input()
            if DEL.lower() == "q":
                break
            elif DEL.upper() not in courses:
                print("Invalid course code! Try again")
            else:
                DELs.append(DEL)

        print("Please enter your OPELs(enter q to when done):")
        while True:
            OPEL: str = input()
            if OPEL.lower() == "q":
                break
            elif OPEL.upper() not in courses:
                print("Invalid course code! Try again")
            else:
                OPELs.append(OPEL)

        print("Please enter your HUELs(enter q to when done):")
        while True:
            HUEL: str = input()
            if HUEL.lower() == "q":
                break
            elif HUEL.upper() not in courses:
                print("Invalid course code! Try again")
            else:
                HUELs.append(HUEL)

        print(("---Preference order---"))
        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order)], sep="\n")
        while True:
            choice_in = input(f"Enter your first preference: ")
            if not verifyInputForNumber(choice_in.split())[0]:
                print(
                    f"Invalid input! {verifyInputForNumber(choice_in)[1]} is not a valid selection."
                )
                continue
            else:
                choice = int(choice_in.split()[0])
            if choice not in [1, 2, 3]:
                print("Invalid input! Please select from 1,2 or 3.")
            else:
                preference_order[0], preference_order[choice - 1] = (
                    preference_order[choice - 1],
                    preference_order[0],
                )
                break

        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order[1:])], sep="\n")
        while True:
            choice_in = input(f"Enter your Second preference: ")
            if not verifyInputForNumber(choice_in.split())[0]:
                print(
                    f"Invalid input! {verifyInputForNumber(choice_in)[1]} is not a valid selection."
                )
                continue
            else:
                choice = int(choice_in.split()[0])
            if choice not in [1, 2]:
                print("Invalid input! Please select from 1 or 2.")
            else:
                preference_order[1], preference_order[choice] = (
                    preference_order[choice],
                    preference_order[1],
                )
                break

    print("---Days Preference---")
    days = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7,
    }
    print(*[f"{x} : {i}" for x, i in days.items()], sep="\n")
    while True:
        free_days_in: str = input(
            "Enter the days you would prefer to be free with a space in between: "
        )
        free_days: set[int] = set([])
        if not verifyInputForNumber(free_days_in.split())[0]:
            print(
                f"Invalid input! {verifyInputForNumber(free_days_in)[1]} is not a valid entry."
            )
            continue
        else:
            free_days = set([int(x) for x in free_days_in.split()])

        if not free_days.issubset(set(days.values())):
            print("Invalid set of days! Please Try again")
        else:
            break

    while True:
        days_order_in: str = input(
            "Enter the order of liteness of days, the earliest is litest and last is hardest: "
        )
        days_order: set[int] = set([])

        if not verifyInputForNumber(days_order_in.split())[0]:
            print(
                f"Invalid input! {verifyInputForNumber(days_order_in.split())[1]} is not a valid entry."
            )
            continue
        else:
            days_order = set([int(x) for x in days_order_in.split()])

        if len(days_order) != 7:
            print("Please input all the days inlcluding sunday!")

        elif days_order != set(days.values()):
            print("Invalid set of days! Please try again")
        else:
            break
