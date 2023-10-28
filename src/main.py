import converter, create_json, timetables, visualize
import pdfplumber as pdfp
import os, json, tabulate
import pandas as pd


files_path_absolute: str = os.path.join(os.path.dirname(__file__), "files")


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
                1 : Section doesn't exist in the course, a dict of form {course_code : section}
                2 : the given sections covers all the component of a course, a dict of the form {course_code,component_covered(Lecture/Tutorial/Practical)}
    """

    course_json = json_file["courses"]  # original dict of all courses and sections
    course_dict: dict = {}  # dict to keep track of allowed courses per course
    unwanted_section_dict: dict = (
        {}
    )  # dict to keep track of unwanted sections per course

    for section in section_list:
        section_dict_courses = [x for x in section.split(" ")]  # turns str into list

        course = " ".join(
            section_dict_courses[0:2]
        ).upper()  # get course code from the splitted list
        sec = section_dict_courses[2].upper()
        print(sec)
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
                return (1, {course: sec})
        elif sec.startswith("T"):
            if sec in course_dict[course].get("Tutorial", []):
                course_dict[course]["Tutorial"].remove(sec)
                unwanted_section_dict[course].append(sec)
            else:
                return (1, {course: sec})
        elif sec.startswith("P"):
            if sec in course_dict[course].get("Practical", []):
                course_dict[course]["Practical"].remove(sec)
                unwanted_section_dict[course].append(sec)
            else:
                return (1, {course: sec})
        else:
            return (1, {course: sec})

    # check if a component of any course is completely covered, return relevant dict_courses accordingly
    for course, sections in course_dict.items():
        for y, z in sections.items():
            if z == []:
                return (2, {course: y})

    return (0, unwanted_section_dict)


def El_input():
    DELs: list[str] = []
    OPELs: list[str] = []
    HUELs: list[str] = []
    print("Please enter your DELs(enter q to when done):")
    while True:
        DEL: str = input("--> ").strip()
        if DEL.lower() == "q":
            break
        elif DEL.upper() not in courses:
            print("Invalid course code! Try again")
        elif DEL.upper() in DELs:
            print("course already added!")
        else:
            DELs.append(DEL.upper())

    print("Please enter your OPELs(enter q to when done):")
    while True:
        OPEL: str = input("--> ").strip()
        if OPEL.lower() == "q":
            break
        elif OPEL.upper() not in courses:
            print("Invalid course code! Try again")
        elif OPEL.upper() in OPELs:
            print("course already added!")
        else:
            OPELs.append(OPEL.upper())

    print("Please enter your HUELs(enter q to when done):")
    while True:
        HUEL: str = input("--> ").strip()
        if HUEL.lower() == "q":
            break
        elif HUEL.upper() not in courses:
            print("Invalid course code! Try again")
        elif HUEL.upper() in HUELs:
            print("course already added!")
        else:
            HUELs.append(HUEL.upper())

    return DELs, OPELs, HUELs


if __name__ == "__main__":
    print("----------Chronoscript CLI----------\n")
    json_path: str = os.path.join(files_path_absolute, "timetable.json")
    flag: bool = True
    if os.path.isfile(json_path):
        choice_in: str = input(
            f"Timetable JSON file found at '{json_path}',Enter to continue with this or enter 'json' to create new from scratch: "
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
                    f"'{choice_in}' is not a valid option! Please press enter to continue with existing file or input 'json' to make a new one: "
                )
    if flag:
        print("\n-------CSV generation-------\n")
        print("---Select timetable pdf---")
        print("Select path for the timetable pdf")
        print("1. Default path : files/timetable.pdf")
        print("2. Pass custom path")
        choice_in: str = input("Enter your choice: ")
        while True:
            if len(choice_in) <= 0 or not verify_input_for_number(choice_in.split())[0]:
                choice_in = input(
                    f"'{choice_in}' is not a valid choice! Enter 1 or 2: "
                )
            else:
                choice: int = int(choice_in[0])
                break

        pdf_path: str = os.path.join(files_path_absolute, "timetable.pdf")
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
                        pdf_path = os.path.join(files_path_absolute, "timetable.pdf")
                else:
                    if confirm_general_input(pdf_path, "file path"):
                        break
                    else:
                        continue

        print("\n---Page Selection---")
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
                    continue
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

            timetable = pd.read_csv(os.path.join(files_path_absolute, "output.csv"))
            create_json.create_json_file(
                timetable,
                columns,
                os.path.join(files_path_absolute, "timetable.json"),
                metadata[0],
                metadata[0],
                metadata[1],
            )
            print("JSON Created!")
        except:
            print("Some error occured! Terminating...")
            raise Exception

    print()
    print("-------TT generation-------\n")
    print("---Course Selection---")
    tt_json = json.load(open(json_path, "r"))
    courses = tt_json["courses"].keys()
    CDCs: list[str] = []
    print("Please enter your CDCs,Format:- MATH F111 (enter q to when done):")
    while True:
        CDC: str = input("--> ").strip()
        if CDC.lower() == "q":
            break
        elif CDC.upper() not in courses:
            print("Invalid course code! Please try again")
        elif CDC.upper() in CDCs:
            print("course already added!")
        else:
            CDCs.append(CDC.upper())

    # initialising variables
    DELs: list[str] = []
    OPELs: list[str] = []
    HUELs: list[str] = []
    nDELs: int = len(DELs)
    nOPELs: int = len(OPELs)
    nHUELs: int = len(HUELs)
    preference_order: list[str] = ["DELs", "HUELs", "OPELs"]

    choice_in = input(
        "Enter 'add' to add DELs,OPELs,HUELs or enter 'skip' to skip this section: "
    )
    while True:
        if choice_in.strip().lower() not in ["add", "skip"]:
            choice_in = input("Invalid Choice! Please enter add or skip: ").strip()
        else:
            break

    # input for Electives
    if choice_in.strip().lower() == "add":
        DELs, OPELs, HUELs = El_input()

        while True:
            ndels_in: str = input("Enter the number of DELs you want: ").strip()
            if ndels_in == "":
                nDELs = len(DELs)
                break
            elif not ndels_in.isnumeric() or int(ndels_in) > len(DELs):
                print("Invalid number of DELs.")
            elif int(ndels_in) <= len(DELs):
                nDELs = int(ndels_in)
                break

        while True:
            nopels_in: str = input("Enter the number of OPELs you want: ").strip()
            if nopels_in == "":
                nOPELs = len(OPELs)
                break
            elif not nopels_in.isnumeric() or int(nopels_in) > len(OPELs):
                print("Invalid number of OPELs.")
            elif int(nopels_in) <= len(OPELs):
                nOPELs = int(nopels_in)
                break

        while True:
            nhuels_in: str = input("Enter the number of HUELs you want: ").strip()
            if nhuels_in == "":
                nHUELs = len(HUELs)
                break
            elif not nhuels_in.isnumeric() or int(nhuels_in) > len(HUELs):
                print("Invalid number of HUELs.")
            elif int(nhuels_in) <= len(HUELs):
                nHUELs = int(nhuels_in)
                break

        print(("---Preference order---"))
        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order)], sep="\n")
        while True:
            choice_in = input(f"Enter your first preference: ").strip()
            if len(choice_in) == 0 or not verify_input_for_number(choice_in.split())[0]:
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

        print(*[f"{x} : {i+1}" for i, x in enumerate(preference_order[1:])], sep="\n")
        while True:
            choice_in = input(f"Enter your Second preference: ").strip()
            if len(choice_in) == 0 or not verify_input_for_number(choice_in.split())[0]:
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
        "\nPlease enter unwanted sections in the format: course_code section,for e.g. MATH F111 L1.(enter q to exit):"
    )
    while True:
        section: str = input("--> ").strip()
        cou: str = " ".join(section.split()[0:2])
        if section.lower() == "q":
            code, dict_courses = check_section(unwanted_sections, tt_json)
            if code == 0:
                break
            elif code == 1:
                print(
                    f"{list(dict_courses.keys())[0]} {list(dict_courses.values())[0]} is not a valid section! Please re-enter the sections."
                )
                unwanted_sections = []
            elif code == 2:
                print(
                    f"A timetable with the above unwanted sections is not possible since no {list(dict_courses.values())[0]} section is left for course {list(dict_courses.keys())[0]}. Please re-enter the sections."
                )
                unwanted_sections = []
        elif cou.upper() not in courses:
            print(f"Invalid course code! Please Try again.")
        else:
            unwanted_sections.append(section.upper())

    print("\n---Days Preference---")
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
    print()
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

    print()
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

        if len(set(days_order)) != 7:
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

    print()
    print("------Exam Schedule Fit------")
    exam_schedule_fit: set[str] = set([])
    exam_fit_dict: dict = {
        "1": "spread out exams",
        "2": "compact exams",
        "3": "Importance to a Specific Course",
        "4": "Avoid two exams on a day",
    }
    print(*[f"{k}: {v}" for k, v in exam_fit_dict.items()], sep="\n")
    while True:
        exam_schedule_fit_in: str = input(
            "Enter the your preferred schedule(s), you can enter two or more fits."
        ).strip()
        if (
            exam_schedule_fit_in != ""
            and not verify_input_for_number(exam_schedule_fit_in.split())[0]
        ):
            print(
                f"{verify_input_for_number(exam_schedule_fit_in.split())[1]} is not a valid entry!"
            )
            continue
        else:
            exam_schedule_fit = set([x for x in exam_schedule_fit_in.split()])
        if not exam_schedule_fit.issubset(set(exam_fit_dict.keys())):
            print(
                f"'{list(exam_schedule_fit.difference(set(exam_fit_dict.keys())))[0]}' is not a valid option! Please Try again"
            )
        elif "1" in exam_schedule_fit_in and "2" in exam_schedule_fit_in:
            print(
                "Exams can't be spread out and compact at the same time! Please try again."
            )
        else:
            if confirm_general_input(
                ",".join([exam_fit_dict[x] for x in exam_schedule_fit]), "exam fit"
            ):
                temp_ls: list[str] = list(exam_schedule_fit)
                temp_ls.sort()
                exam_fit: str = "".join(temp_ls)

                break
            else:
                continue
    course_fit: str = ""
    if "3" in exam_schedule_fit_in:
        while True:
            course_fit = (
                input(
                    "Enter the course you want to give priority to, Format:- MATH F111: "
                )
                .strip()
                .upper()
            )
            if course_fit not in tt_json["courses"].keys():
                print("Invalid course code! Please try again.")
            else:
                if confirm_general_input(course_fit, "important course"):
                    break
                else:
                    continue

    priority_dict: dict = {1: "Free days", 2: "Days Liteness", 3: "Exam Fit"}
    priorities: list[int] = []

    print()
    print(("---Priorities---"))
    print(*[f"{x} : {i}" for i, x in priority_dict.items()], sep="\n")

    while True:
        priorities_in: str = input(
            "Enter the priority order(all three), for e.g. 1 2 3: "
        ).strip()

        if not verify_input_for_number(priorities_in.split())[0]:
            print(
                f"Invalid input! '{verify_input_for_number(priorities_in.split())[1]}' is not a valid entry."
            )
            continue
        else:
            priorities = [int(x) for x in priorities_in.split()]

        if len(set(priorities)) != 3:
            print("Invalid input! Please include all three.")

        elif set(priorities) != set(priority_dict.keys()):
            print(
                f"'{list(set(priorities).difference(set(priority_dict.keys())))[0]}' is not a option! Please try again"
            )
        else:
            if confirm_general_input(
                " ".join([priority_dict[x] for x in priorities]), "priority order"
            ):
                break
            else:
                continue

    print()
    strong: str = False
    filter: str = False
    print("---Filter Timetables---")
    while True:
        choice_in = (
            input(
                "Do you prefer timetables with strong filter for free days,i.e.,only tts with exact free days, yes or no:   "
            )
            .strip()
            .lower()
        )
        if choice_in not in ["yes", "no"]:
            print("Invalid option.")
        else:
            if choice_in == "yes":
                strong = True
            break

    while True:
        choice_in = (
            input(
                "Do you want only the timetables with free days exactly matched, yes or no: "
            )
            .strip()
            .lower()
        )
        if choice_in not in ["yes", "no"]:
            print("Invalid option.")
        else:
            if choice_in == "yes":
                filter = True
            break

    free_days: list[str] = [days[x] for x in free_days]
    lite_order: list[str] = [days[x] for x in days_order]

    print("\nGenerating timetables....")
    filtered_json = timetables.get_filtered_json(tt_json, CDCs, DELs, HUELs, OPELs)

    exhaustive_list_of_timetables = timetables.generate_exhaustive_timetables(
        filtered_json, dict_courses, nDELs, nOPELs, nHUELs
    )

    timetables_without_clashes = timetables.remove_clashes(
        exhaustive_list_of_timetables, filtered_json
    )

    timetables_without_clashes = timetables.remove_exam_clashes(
        timetables_without_clashes, filtered_json
    )

    print(
        "Number of timetables without clashes (classes and exams):",
        len(timetables_without_clashes),
    )

    in_my_preference_order = timetables.generate_preferred_timetables(
        tt_json,
        timetables_without_clashes,
        filtered_json,
        free_days,
        lite_order,
        exam_fit,
        course_fit,
        priorities,
        filter=filter,
        strong=strong,
    )

    print("Number of timetables after filter: ", len(in_my_preference_order))

    if len(in_my_preference_order) > 0:
        print(
            "-----------------------------------------------------",
            "\nHighest match:\n",
            in_my_preference_order[0],
            "\n\n",
            "-----------------------------------------------------",
            "\nLowest match:\n",
            in_my_preference_order[-1],
        )
        timetables.export_to_json(in_my_preference_order, filtered_json)

        print()
        print("---Visualize---")
        while True:
            choice_in = (
                input(
                    "Press enter to visualize the best possible timetable or enter 'exit' to leave: "
                )
                .strip()
                .lower()
            )
            if choice_in == "exit":
                break
            elif choice_in == "":
                tts: dict = json.load(
                    open(os.path.join(files_path_absolute, "my_timetables.json"), "r")
                )
                dfs = visualize.convert_timetable_to_pandas_dataframe(tts, 0, False)
                print("======================================================\n")
                print("Class Schedule:\n\n")
                print(tabulate.tabulate(dfs[0], headers="keys", tablefmt="fancy_grid"))
                print("------------------------------------------------------\n")
                print("\nMidsem Schedule:\n\n")
                print(tabulate.tabulate(dfs[1], headers="keys", tablefmt="fancy_grid"))
                print("------------------------------------------------------\n")
                print("\nCompre Schedule:\n\n")
                print(tabulate.tabulate(dfs[2], headers="keys", tablefmt="fancy_grid"))
                print("======================================================\n")
            else:
                print("Invalid choice! Please try again.")
    else:
        print("No timetables found")
