import converter, create_json, timetables
import pdfplumber as pdfp
import os, json
import pandas as pd

""""
TO-DO
1. comments
2. implement unwanted section in timetables.py - done(testing remains)
3. change course code check for unwanted ssections to instantenous

optional
1. function up the diff input blocks
2. implement better checking
3. provide an option to add or remove cdcs/huels etc before moving forward
"""


def verify_input_for_number(inp: list[str]) -> (bool, str):
    """
    Function to check if the input is numeric and greater than 0.

    Args:
    inp: list[str] - list of inputs from the user.

    Returns:
    (bool,str) - a tuple with boolean and the first character where it fails returns '' if all inputs are numbers.
    """

    for x in inp:
        if not x.isnumeric() or int(x) <= 0:
            return (False, x)
    return (True, "")


def confirm_general_input(inp: str, inp_str: str) -> bool:
    """
    Function to prompt user for confirmation of the input.

    Args:
    inp: str - the input given by the user
    inp_str: str - the field for which the input was

    Returns:
    bool - True if user confirms, False if user requests to edit
    """
    confirm: str = input(
        f"The {inp_str} is {inp}, press enter to continue or enter edit to change: "
    )
    while True:
        if confirm == "":
            return True
        elif confirm.lower() == "edit":
            return False
        else:
            confirm = input(
                f"'{confirm}' is not valid input!\nYour current {inp_str} is {inp} press enter to continue or enter edit: "
            )


def check_section(section_list: list[str], json_file: dict) -> (int, dict):
    """
    Function to check if a given list of unwanted sections is valid, i.e. not covers all possible sections or is not a section etc.

    Args:
    section_list list[str] - list of sections.
    json_file: dict - timetable json file.

    Returns:
    (int,dict) - a tuple with an int error code and a dict with relevant info as following:
                0 : No errors, it returns a dict of form {course_code : list[unwanted_sections]}
                1 : Invalid course code, a dict of form {course_code : ''}
                2 : Section doesn't exist in the course, a dict of form {course_code : section}
                3 : the given sections covers all the component of a course, a dict of the form {course_code,component_covered(Lecture/Tutorial/Practical)}
    """

    course_json = json_file["courses"]  # original dict of all courses and sections
    course_dict: dict = {}  # dict to keep track of allowed courses per course
    unwanted_section_dict: dict = (
        {}
    )  # dict to keep track of unwanted sections per course

    for section in section_list:
        section_details = [
            x for x in section.split(" ") if x.isalnum()
        ]  # turns str into list while removing invalid characters

        course = " ".join(
            section_details[0:2]
        ).upper()  # get course code from the splitted list
        sec = section_details[2].upper()

        # Check if the course code is valid
        if not course_json.get(course):
            return (1, {course: ""})

        # initialise dict for a course
        if not unwanted_section_dict.get(course):
            unwanted_section_dict[course] = []

        # initialise dict for a course
        if not course_dict.get(course):
            course_dict[course] = {"Lecture": [], "Tutorial": [], "Practical": []}

            # fill dict with all possible components and sections
            for x in course_json[course]["sections"].keys():
                if x.startswith("L"):
                    course_dict[course]["Lecture"].append(x)
                elif x.startswith("T"):
                    course_dict[course]["Tutorial"].append(x)
                elif x.startswith("P"):
                    course_dict[course]["Practical"].append(x)

            # remove unnecessary component
            course_dict[course] = {
                k: v for k, v in course_dict[course].items() if v != []
            }

        # check if the section is valid and manipulate dicts accordingly
        if sec.startswith("L"):
            if sec in course_dict[course].get("Lecture", []):
                course_dict[course]["Lecture"].remove(sec)
                unwanted_section_dict[course].append(sec)
            else:
                return (2, {course: sec})
        elif sec.startswith("T"):
            if sec in course_dict[course].get("Tutorial", []):
                course_dict[course]["Tutorial"].remove(sec)
                unwanted_section_dict[course].append(sec)
            else:
                return (2, {course: sec})
        elif sec.startswith("P"):
            if sec in course_dict[course].get("Practical", []):
                course_dict[course]["Practical"].remove(sec)
                unwanted_section_dict[course].append(sec)
            else:
                return (2, {course: sec})

    # check if a component of any course is completely covered, return relevant details accordingly
    for course, sections in course_dict.items():
        for y, z in sections.items():
            if z == []:
                return (3, {course: y})

    return (0, unwanted_section_dict)


if __name__ == "__main__":
    print("----------Chronoscript CLI----------")
    json_path: str = r".\files\timetable.json"
    flag: bool = True
    if os.path.isfile(json_path):
        choice_in: str = input(
            f"Timetable JSON file found at '{json_path}',Enter to continue with this or enter json to create new from scratch: "
        )
        while True:
            if choice_in == "":
                flag = False
                break
            elif choice_in.lower() == "json":
                flag = True
                break
            else:
                choice_in = input(
                    f"'{choice_in}' is not a valid option! Please press enter to continue with existing file or input json to make a new one: "
                )
    if flag:
        print("-------CSV generation-------")
        print("---Select timetable pdf---")
        print("Select path for the timetable pdf")
        print("1. Default path : files/timetable.pdf")
        print("2. Pass custom path")
        choice_in: str = input("Enter your choice: ")
        while True:
            if len(choice_in) == 0 or not verify_input_for_number(choice_in.split())[0]:
                choice_in = input(
                    f"'{choice_in}' is not a valid choice! Enter 1 or 2: "
                )
            else:
                choice: int = int(choice_in[0])
                break

        pdf_path: str = r".\files\timetable.pdf"
        if choice == 2:
            pdf_path = input("Enter the complete file path: ")
            pdf_path.replace('"', "")
            while True:
                if not (os.path.isfile(pdf_path)):
                    pdf_path: str = input(
                        "Invalid file path! Enter the complete file path or press enter to continue with default file path: "
                    )
                    pdf_path.replace('"', "")
                    if pdf_path == "":
                        pdf_path = r".\files\timetable.pdf"
                else:
                    if confirm_general_input(pdf_path, "file path"):
                        break
                    else:
                        continue

        print("---Page Selection---")
        page_list: list[int] = []
        while True:
            page_list_in: str = input(
                "Enter the start and end page of the timetable.For e.g. 1 4 : "
            )
            if not verify_input_for_number(page_list_in.split())[0]:
                print(
                    f"Invalid input! '{verify_input_for_number(page_list_in.split())[1]}' is not a valid page number."
                )
                continue
            else:
                page_list = [int(x) for x in page_list_in.split()]
            if len(page_list) < 2:
                print(
                    "Invalid range! Please specify both a starting and an ending page."
                )
            elif page_list[1] < page_list[0]:
                print("End page number cant be smaller than the start.")
            else:
                if confirm_general_input(page_list_in, "Page range"):
                    break
                else:
                    continue

        try:
            file: pdfp.pdf.PDF = pdfp.open(pdf_path)
            pages: list[pdfp.page.Page] = file.pages[page_list[0] - 1 : page_list[1]]
            headers: list[str] = ["COM\nCOD"]
            print(f"Creating CSV using the file at {pdf_path} ....")
            converter.convert_timetable_to_csv(pages, headers)
            print("CSV created!\n")

        except:
            print("Some Error occured! Terminating..")
            raise Exception

        print("-------JSON creation-------")
        metadata: list[int] = []
        while True:
            metadata_in: str = input(
                "Enter the academic year and semester(1 or 2). For e.g. 2023 1 :"
            )
            if not verify_input_for_number(metadata_in.split())[0]:
                print(
                    f"Invalid input! '{verify_input_for_number(metadata_in.split())[1]}' is not a valid year or semester."
                )
                continue
            else:
                metadata = [int(x) for x in metadata_in.split()]
            if len(metadata) < 2:
                print("Invalid input! Please specify both year and semester")
            elif metadata[1] not in [1, 2]:
                print("Invalid input! semester has to be 1 or 2")
            else:
                if confirm_general_input(metadata_in, "year and semester"):
                    break
                else:
                    metadata_in: str = input(
                        "Enter the academic year and semester(1 or 2). For e.g. 2023 1 :"
                    )
        year: int = metadata[0]
        semester: int = metadata[1]
        try:
            print("Creating JSON....")
            columns = [
                "serial",
                "course_code",
                "course_name",
                "L",
                "P",
                "U",
                "section",
                "instructor",
                "room",
                "days",
                "hours",
                "midsem",
                "compre",
            ]

            timetable = pd.read_csv("./files/output.csv")
            create_json.create_json_file(
                timetable,
                columns,
                r".\files\timetable.json",
                metadata[0],
                metadata[0],
                metadata[1],
            )
            print("JSON Created!\n")
        except:
            print("Some error occured! Terminating...")
            raise Exception

    print("-------TT generation-------")
    tt_json = json.load(open(json_path, "r"))
    courses = tt_json["courses"].keys()
    CDCs: list[str] = []
    print("Please enter your CDCs(enter q to when done):")
    while True:
        CDC: str = input("--> ").strip()
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
    choice_in = input(
        "Enter 'add' to add DELs,OPELs,HUELs or enter 'skip' to skip this section: "
    )
    while True:
        if choice_in.strip().lower() not in ["add", "skip"]:
            choice_in = input("Invalid Choice! Please enter add or skip: ").strip()
        else:
            break

    if choice_in.strip().lower() == "add":
        print("Please enter your DELs(enter q to when done):")
        while True:
            DEL: str = input("--> ")
            if DEL.lower() == "q":
                break
            elif DEL.strip().upper() not in courses:
                print("Invalid course code! Try again")
            else:
                DELs.append(DEL)

        print("Please enter your OPELs(enter q to when done):")
        while True:
            OPEL: str = input("--> ")
            if OPEL.strip().lower() == "q":
                break
            elif OPEL.strip().upper() not in courses:
                print("Invalid course code! Try again")
            else:
                OPELs.append(OPEL)

        print("Please enter your HUELs(enter q to when done):")
        while True:
            HUEL: str = input("--> ")
            if HUEL.strip().lower() == "q":
                break
            elif HUEL.strip().upper() not in courses:
                print("Invalid course code! Try again")
            else:
                HUELs.append(HUEL)

        print(("---Preference order---"))
        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order)], sep="\n")
        while True:
            choice_in = input(f"Enter your first preference: ").strip()
            if not verify_input_for_number(choice_in.split())[0]:
                print(
                    f"Invalid input! '{verify_input_for_number(choice_in)[1]}' is not a valid selection."
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
        while True:
            choice_in = input(f"Enter your Second preference: ").strip()
            if not verify_input_for_number(choice_in.split())[0]:
                print(
                    f"Invalid input! '{verify_input_for_number(choice_in)[1]}' is not a valid selection."
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
    unwanted_sections: list[str] = []
    print(
        "Please enter unwanted sections in the format: course_code section,for e.g. MATH F111 L1.(enter q to exit):"
    )
    while True:
        section: str = input("--> ").strip()
        if section.lower() == "q":
            code, details = check_section(unwanted_sections, tt_json)
            if code == 0:
                break
            elif code == 1:
                print(f"{details.keys()[0]} is not a valid course code!")
            elif code == 2:
                print(
                    f"{details.items()[0]} {details.items()[1]} is not a valid section!"
                )
            elif code == 3:
                print(
                    f"A timetable with the above unwanted sections is not possible since no {details.items()[1]} section is left for course {details.items()[0]}"
                )
        else:
            unwanted_sections.append(section)

        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order[1:])], sep="\n")

    print("---Days Preference---")
    days = {
        1: "M",
        2: "T",
        3: "W",
        4: "Th",
        5: "F",
        6: "S",
        7: "Su",
    }
    print(*[f"{x} : {i}" for i, x in days.items()], sep="\n")
    free_days: set[int] = set([])
    while True:
        free_days_in: str = input(
            "Enter the days you would prefer to be free with a space in between: "
        ).strip()
        if free_days_in != "" and not verify_input_for_number(free_days_in.split())[0]:
            print(
                f"Invalid input! '{verify_input_for_number(free_days_in)[1]}' is not a valid entry."
            )
            continue
        else:
            free_days = set([int(x) for x in free_days_in.split()])

        if not free_days.issubset(set(days.keys())):
            print(
                f"'{list(free_days.difference(set(days.keys())))[0]}' is not a valid day! Please Try again"
            )
        else:
            if confirm_general_input(
                " ".join([days[x] for x in free_days]), "list of free days"
            ):
                break
            else:
                continue

    days_order: list[int] = []
    while True:
        days_order_in: str = input(
            "Enter the order of liteness of days, the earliest is litest and last is hardest: "
        ).strip()

        if not verify_input_for_number(days_order_in.split())[0]:
            print(
                f"Invalid input! '{verify_input_for_number(days_order_in.split())[1]}' is not a valid entry."
            )
            continue
        else:
            days_order = [int(x) for x in days_order_in.split()]

        if len(days_order) != 7:
            print("Please input all the days inlcluding sunday!")

        elif set(days_order) != set(days.keys()):
            print(
                f"'{list(set(days_order).difference(set(days.keys())))[0]}' is not a valid day! Please try again"
            )
        else:
            if confirm_general_input(
                " ".join([days[x] for x in days_order]), "order of days"
            ):
                break
            else:
                continue

    nDELs = len(DELs)
    nHUELs = len(HUELs)
    nOPELs = len(OPELs)

    free_days = [days[x] for x in free_days]
    lite_order = [days[x] for x in days_order]

    filtered_json = timetables.get_filtered_json(tt_json, CDCs, DELs, HUELs, OPELs)

    exhaustive_list_of_timetables = timetables.generate_exhaustive_timetables(
        filtered_json, nDELs, nOPELs, nHUELs
    )

    timetables_without_clashes = timetables.remove_clashes(
        exhaustive_list_of_timetables, filtered_json
    )

    timetables_without_clashes = timetables.remove_exam_clashes(
        timetables_without_clashes, filtered_json
    )

    in_my_preference_order = timetables.day_wise_filter(
        timetables_without_clashes,
        filtered_json,
        free_days,
        lite_order,
        filter=False,
        strong=False,
    )
