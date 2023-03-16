import hashlib
import os
import datetime

# Module "string": Common string operations
# (https://docs.python.org/3.11/library/sys.html#module-sys)
from string import Template


class DeltaTemplate(
    Template,
):
    """
    String template for timedelta objects formatted strings
    """

    delimiter = "%"


def strfdelta(
    def_time_delta,
    def_time_delta_format,
):
    """
    Generates the string for a timedelta object.
    :param def_time_delta:        timedelta, timedelta object
    :param def_time_delta_format:       str, format of the timedelta object string
    :return:                            str, timedelta formatted string
    """
    d = {"D": def_time_delta.days}
    hours, rem = divmod(
        def_time_delta.seconds,
        3600,
    )
    minutes, seconds = divmod(
        rem,
        60,
    )
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(def_time_delta_format)
    return t.substitute(**d)


def get_file_hash(def_file_path):
    with open(def_file_path, "rb") as f:
        file_data = f.read()
        return hashlib.sha512(file_data).hexdigest()


def sha512_hash(def_filename):
    """Calculate the SHA512 hash of a file."""
    sha512 = hashlib.sha512()
    with open(def_filename, "rb") as f:
        while True:
            if data := f.read(4096):
                sha512.update(data)
            else:
                break
    return sha512.hexdigest()


def print_verbose(
    def_message,
    def_verbose,
):
    if def_verbose:
        print(def_message)


def compare_files(
    def_file1,
    def_file2,
    def_options,
):
    # Get file status
    file1_stat = os.stat(def_file1)
    file2_stat = os.stat(def_file2)

    # Check file size
    file_size = None
    if "S" in def_options:
        file1_size = file1_stat.st_size
        file2_size = file2_stat.st_size
        file_size = {
            "details": "file_size",
            "result": file1_stat.st_size == file2_stat.st_size,
            "file1_data": str(file1_size),
            "file2_data": str(file2_size),
        }

    # Check modification time
    file_mtime = None
    if "T" in def_options:
        file_mtime = {
            "details": "file_mtime",
            "result": file1_stat.st_mtime == file2_stat.st_mtime,
            "file1_data": str(
                datetime.datetime.fromtimestamp(file1_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            "file2_data": str(
                datetime.datetime.fromtimestamp(file2_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
        }

    # Check file hash
    file_hash = None
    if "H" in def_options:
        file1_hash = sha512_hash(def_file1)
        file2_hash = sha512_hash(def_file2)
        file_hash = {
            "details": "file_hash",
            "result": file1_hash == file2_hash,
            "file1_data": str(file1_hash),
            "file2_data": str(file2_hash),
        }

    # Check bitwise comparison
    file_bit = None
    if "B" in def_options:
        file_bit = {
            "details": "file_bit",
            "result": True,
            "file1_data": "",
            "file2_data": "",
        }
        with open(def_file1, "rb") as f1, open(def_file2, "rb") as f2:
            for b1, b2 in zip(
                iter(lambda: f1.read(4096), b""), iter(lambda: f2.read(4096), b"")
            ):
                if b1 != b2:
                    file_bit["result"] = False
                    break

    results = []

    if file_size is not None:
        results.append(file_size)
    if file_mtime is not None:
        results.append(file_mtime)
    if file_hash is not None:
        results.append(file_hash)
    if file_bit is not None:
        results.append(file_bit)

    return results


def create_file_dict(
    def_folder,
    def_exclude_files=None,
    def_exclude_extensions=None,
):
    files_dict = {}
    for root, dirs, files in os.walk(def_folder, topdown=False):
        for file in files:
            # Skip excluded files
            if def_exclude_files and file in def_exclude_files:
                continue
            # Skip excluded file extensions
            if (
                def_exclude_extensions
                and os.path.splitext(file)[1].lower() in def_exclude_extensions
            ):
                continue
            file_path = os.path.join(root, file)
            files_dict[file_path[len(def_folder) + 1 :]] = file_path
    return files_dict


def evaluate_file_comparison_state(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose_general=True,
):
    # Store the files in each folder
    files1 = create_file_dict(
        def_folder1,
        def_exclude_files,
        def_exclude_extensions,
    )
    files2 = create_file_dict(
        def_folder2,
        def_exclude_files,
        def_exclude_extensions,
    )

    number_of_files_in_source = len(files1)
    number_of_files_in_target = len(files2)

    minimum_number_of_files = min(number_of_files_in_source, number_of_files_in_target)

    count_tick = round(
        0.1 * max(number_of_files_in_source, number_of_files_in_target), 0
    )

    print()
    print(">>>>>>>>> Comparing two folders <<<<<<<<<")
    print()
    print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"OPTIONS:  '{def_options}' is requested"
    )
    if "S" in def_options:
        print("                     -> S: Comparing the files for their size")
    if "T" in def_options:
        print(
            "                     -> T: Comparing the files for their modification time"
        )
    if "H" in def_options:
        print("                     -> H: Comparing the files for their hashes")
    if "B" in def_options:
        print("                     -> B: Comparing the files bitwise")

    print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"SOURCE:   '{def_folder1}' (number of files in source: '{number_of_files_in_source}')"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TARGET:   '{def_folder2}' (number of files in target: '{number_of_files_in_target}')"
    )
    print()

    if number_of_files_in_source != number_of_files_in_target:
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   Number of files in source and target are different\n"
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"DELTA:     -> {abs(number_of_files_in_target - number_of_files_in_source)} files"
        )
        print()

    # Check for missing files
    missing_files1 = set(files1.keys()).difference(set(files2.keys()))
    missing_files2 = set(files2.keys()).difference(set(files1.keys()))
    files_missing_target = {
        missing_file_target: f"{def_folder2}/{missing_file_target}"
        for missing_file_target in missing_files1
    }
    files_missing_source = {
        missing_file_source: f"{def_folder2}/{missing_file_source}"
        for missing_file_source in missing_files2
    }

    # Compare files
    comparison_start_time = datetime.datetime.now()
    print("")
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Comparison of files"
    )
    print("")

    files_identical = {}
    files_only_mtime_difference = {}
    files_any_difference_but_mtime = {}
    digits = f"0{len(str(min(number_of_files_in_source, number_of_files_in_target)))}d"
    time_old = datetime.datetime.now()
    file_count_old = 0
    for idx, file in enumerate(set(files1.keys()).intersection(set(files2.keys()))):
        file1 = files1[file]
        file2 = files2[file]
        results = compare_files(file1, file2, def_options)

        if idx % count_tick == 0:
            time_new = datetime.datetime.now()
            file_count_new = idx
            if file_count_new - file_count_old > 0:
                number_of_seconds = (time_new - time_old).total_seconds()
                number_of_files_compared = file_count_new - file_count_old
                comparisons_per_second = number_of_files_compared / number_of_seconds
                print_verbose(
                    f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
                    f"Number of files compared so far: {file_count_new + 1:{digits}}",
                    def_verbose_general,
                )
                print_verbose(
                    f"                     -> {int(round(comparisons_per_second, 0))} "
                    f"comparisons per second ",
                    def_verbose_general,
                )
                comparison_eta = (
                    minimum_number_of_files - idx
                ) / comparisons_per_second
                print_verbose(
                    f"                     -> ETA = {round(comparison_eta, 1)}",
                    def_verbose_general,
                )
                print_verbose(
                    f"                     -> Current file: '{file}'",
                    def_verbose_general,
                )
                print_verbose(
                    "",
                    def_verbose_general,
                )
            time_old = time_new
            file_count_old = file_count_new

        def check_files_identical(def_results):
            return all((item["result"] for item in def_results))

        if check_files_identical(results):
            files_identical[file] = results

        def check_files_any_difference_but_mtime(def_results):
            for item in def_results:
                if item["details"] != "file_mtime" and not item["result"]:
                    return True
            return False

        if check_files_any_difference_but_mtime(results):
            files_any_difference_but_mtime[file] = results

        def check_files_only_mtime_difference(def_results):
            for item in def_results:
                if item["details"] != "file_mtime" and not item["result"]:
                    return False
                if item["details"] == "file_mtime" and item["result"]:
                    return False
            return True

        details_mtime_found = False
        for test_for_mtime in results:
            if "file_mtime" in test_for_mtime["details"]:
                details_mtime_found = True

        if check_files_only_mtime_difference(results) and details_mtime_found:
            files_only_mtime_difference[file] = results

    comparison_end_time = datetime.datetime.now()
    elapsed_compare_time = comparison_end_time - comparison_start_time

    elapsed_run_time_format: str = "%H:%M:%S"
    elapsed_run_time_string = strfdelta(elapsed_compare_time, elapsed_run_time_format)
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"TIME:      {elapsed_run_time_string}\n"
    )
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Comparison of files"
    )
    print()

    return (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
    )


def compare_folders(
    def_folder1,
    def_folder2,
    def_exclude_files=None,
    def_exclude_extensions=None,
    def_options="STHB",
    def_verbose_general=True,
    def_verbose_pass=True,
):
    (
        files_missing_source,
        files_missing_target,
        files_identical,
        files_only_mtime_difference,
        files_any_difference_but_mtime,
    ) = evaluate_file_comparison_state(
        def_folder1,
        def_folder2,
        def_exclude_files,
        def_exclude_extensions,
        def_options,
        def_verbose_general,
    )

    print()
    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"BEGIN:     Evaluation of comparison"
    )
    print_verbose("", verbose_general)

    # print()
    digits = f"0{len(str(len(files_identical)))}d"
    for idx, file in enumerate(files_identical):
        print_verbose(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"PASS:      Files are identical:    '{file}' (file number: {idx + 1:{digits}})",
            def_verbose_pass,
        )
        for detail in files_identical[file]:
            print_verbose(
                f"                     -> {detail}",
                def_verbose_pass,
            )
    if files_identical:
        print()

    for file, path in files_missing_source.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"WARNING:   File missing in source: '{file}' in '{def_folder1}'"
        )
    if files_missing_source.items():
        print()

    for file, path in files_missing_target.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File missing in target: '{file}' in '{def_folder2}'"
        )
        # TODO: COPY TO TARGET?
    if files_missing_target.items():
        print()

    for file, details in files_only_mtime_difference.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR->OK: File differs:           '{file}':"
        )
        print(
            "                     -> OK: Only mtime differs. "
            "Files are otherwise identical (size, hash, bits)."
        )
        for detail in details:
            print(f"                     -> {detail}")
    if files_only_mtime_difference:
        print()

    for file, details in files_any_difference_but_mtime.items():
        print(
            f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
            f"ERROR:     File differs:           '{file}':"
        )
        for detail in details:
            print(f"                     -> {detail}")
    if files_any_difference_but_mtime:
        print()

    print(
        f"{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}: "
        f"END:       Evaluation of comparison"
    )
    print()
    print()
    print()


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python compare_folders.py folder1 folder2")
    #     sys.exit(1)
    # folder1 = sys.argv[1]
    # folder2 = sys.argv[2]

    # /usr/local/bin/rsync -avzHXA --delete --progress --progress --stats --dry-run --iconv=UTF8,UTF8-MAC --checksum test1/ test2/

    folder1 = "/Users/mh/temp/test1"
    folder2 = "/Users/mh/temp/test2"
    # folder1 = "/Users/mh/temp/movieposters1"
    # folder2 = "/Users/mh/temp/movieposters2"
    # folder1 = "/Users/mh/temp/01 - Januar"
    # folder2 = "/Users/mh/temp/02 - Januar"
    # folder1 = "/Volumes/Untitled"
    # folder2 = "/Users/mh/Documents/DJI Mini 3 Pro/DJI Mini 3 Pro"

    # Optional: specify a list of files to exclude
    # exclude_files = [".DS_Store"]
    exclude_files = []

    # Optional: specify a list of file extensions to exclude
    # exclude_extensions = [".log"]
    exclude_extensions = []

    options = [
        "S",
        "T",
        "H",
        "B",
        "ST",
        "SH",
        "SB",
        "TH",
        "TB",
        "HB",
        "STH",
        "STB",
        "SHB",
        "THB",
        "STHB",
    ]

    verbose_general = True
    verbose_pass = True

    options = "STHB"
    # S = Compare the files for their size
    # T = Compare the files for their modification time
    # H = Compare the files using hashes
    # B = Compare the files bitwise
    compare_folders(
        folder1,
        folder2,
        exclude_files,
        exclude_extensions,
        options,
        verbose_general,
        verbose_pass,
    )

    exit()

    for option in options:
        compare_folders(
            folder1,
            folder2,
            exclude_files,
            exclude_extensions,
            option,
            verbose_general,
            verbose_pass,
        )
